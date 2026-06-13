#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析采集结果 → summary.json + REPORT.md。
用法: python analyze.py results.jsonl
依赖: numpy scipy sklearn（conda env IDEA_Prompt_Risk_Perception）
"""
import json, sys, itertools, math
from collections import defaultdict
import numpy as np
from scipy import stats
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix

LABELS = ["happy", "angry", "sad", "fear", "surprise", "neutral"]
RISK = {"angry", "sad", "fear"}  # 风险信号 = 负面情绪
STRATS = ["S1_direct", "S2_role", "S3_def", "S4_few", "S5_cot", "S6_json"]
B = 1000
SEED = 2026

def load(path):
    by_key = {}
    for line in open(path, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        by_key[(r["domain"], r["id"], r["strategy"], r["model"])] = r
    return list(by_key.values())

def macro_f1_ci(gold, pred, rng):
    """bootstrap 95% CI for macro-F1（未解析按错处理：pred=None → 特殊错类）"""
    g = np.array(gold); p = np.array([x if x else "__fail__" for x in pred])
    point = f1_score(g, p, labels=LABELS, average="macro", zero_division=0)
    n = len(g); vals = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        vals.append(f1_score(g[idx], p[idx], labels=LABELS, average="macro", zero_division=0))
    return point, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))

def mcnemar(c01, c10):
    """exact binomial McNemar"""
    n = c01 + c10
    if n == 0:
        return 1.0
    k = min(c01, c10)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) * 0.5 ** n
    return min(1.0, p)

def bh_fdr(ps):
    m = len(ps); order = np.argsort(ps); out = np.empty(m)
    prev = 1.0
    for rank, idx in list(enumerate(order))[::-1]:
        val = min(prev, ps[idx] * m / (rank + 1)); out[idx] = val; prev = val
    return out

def main(path):
    recs = load(path)
    rng = np.random.default_rng(SEED)
    models = sorted(set(r["model"] for r in recs))
    domains = sorted(set(r["domain"] for r in recs))
    print(f"records={len(recs)} models={models} domains={domains}")

    # 索引: (model,domain,strategy) -> {id: rec}
    cell = defaultdict(dict)
    for r in recs:
        cell[(r["model"], r["domain"], r["strategy"])][r["id"]] = r

    summary = {"per_cell": [], "mcnemar": [], "friedman": {}, "risk": []}
    md = ["# 提示策略 × 模型 × 域 分析报告\n",
          f"- 总记录 {len(recs)}；模型 {models}；域 {domains}；B={B} bootstrap\n"]

    # ---- 每格指标 ----
    md.append("\n## 1. 每格 macro-F1 / acc / 解析率 / 时延\n")
    md.append("| model | domain | strategy | macroF1 [95%CI] | acc | parse% | lat(s) |")
    md.append("|---|---|---|---|---|---|---|")
    for m in models:
        for d in domains:
            for s in STRATS:
                rs = cell.get((m, d, s), {})
                if len(rs) < 30:
                    continue
                ids = sorted(rs)
                gold = [rs[i]["gold"] for i in ids]
                pred = [rs[i]["pred"] for i in ids]
                f1, lo, hi = macro_f1_ci(gold, pred, rng)
                acc = float(np.mean([g == p for g, p in zip(gold, pred)]))
                pr = float(np.mean([rs[i]["parse_ok"] for i in ids]))
                lat = float(np.median([rs[i]["latency_s"] for i in ids]))
                summary["per_cell"].append(dict(model=m, domain=d, strategy=s, n=len(ids),
                                                macro_f1=f1, ci=[lo, hi], acc=acc,
                                                parse_rate=pr, med_latency=lat))
                md.append(f"| {m} | {d} | {s} | {f1:.3f} [{lo:.3f},{hi:.3f}] "
                          f"| {acc:.3f} | {pr*100:.1f} | {lat:.2f} |")

    # ---- 风险信号二分类（派生）----
    md.append("\n## 2. 风险信号检测（angry/sad/fear→1）F1 / recall\n")
    md.append("| model | domain | strategy | F1 | recall | precision |")
    md.append("|---|---|---|---|---|---|")
    for m in models:
        for d in domains:
            for s in STRATS:
                rs = cell.get((m, d, s), {})
                if len(rs) < 30:
                    continue
                ids = sorted(rs)
                g = np.array([rs[i]["gold"] in RISK for i in ids])
                p = np.array([(rs[i]["pred"] or "") in RISK for i in ids])
                tp = int((g & p).sum()); fp = int((~g & p).sum()); fn = int((g & ~p).sum())
                prec = tp / (tp + fp) if tp + fp else 0.0
                rec = tp / (tp + fn) if tp + fn else 0.0
                f1b = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
                summary["risk"].append(dict(model=m, domain=d, strategy=s,
                                            f1=f1b, recall=rec, precision=prec))
                md.append(f"| {m} | {d} | {s} | {f1b:.3f} | {rec:.3f} | {prec:.3f} |")

    # ---- McNemar: 每策略 vs S1（模型×域 配对），BH-FDR ----
    md.append("\n## 3. 策略 vs S1_direct 的 McNemar 配对检验（exact, BH-FDR 校正）\n")
    md.append("| model | domain | strategy | b(只S错) | c(只基准错) | OR | p | p.adj | sig |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    tests = []
    for m in models:
        for d in domains:
            base = cell.get((m, d, "S1_direct"), {})
            for s in STRATS[1:]:
                rs = cell.get((m, d, s), {})
                common = sorted(set(base) & set(rs))
                if len(common) < 30:
                    continue
                b = sum(1 for i in common
                        if base[i]["pred"] == base[i]["gold"] and rs[i]["pred"] != rs[i]["gold"])
                c = sum(1 for i in common
                        if base[i]["pred"] != base[i]["gold"] and rs[i]["pred"] == rs[i]["gold"])
                p = mcnemar(b, c)
                orr = (c + 0.5) / (b + 0.5)
                tests.append(dict(model=m, domain=d, strategy=s, b=b, c=c, odds_ratio=orr, p=p))
    if tests:
        padj = bh_fdr(np.array([t["p"] for t in tests]))
        for t, pa in zip(tests, padj):
            t["p_adj"] = float(pa)
            sig = "✓" if pa < 0.05 else ""
            md.append(f"| {t['model']} | {t['domain']} | {t['strategy']} | {t['b']} | {t['c']} "
                      f"| {t['odds_ratio']:.2f} | {t['p']:.4g} | {pa:.4g} | {sig} |")
    summary["mcnemar"] = tests

    # ---- Friedman + Kendall's W: 策略排序跨 (model×domain) 一致性 ----
    md.append("\n## 4. 跨模型策略排序一致性（Friedman + Kendall's W，基于 macro-F1）\n")
    rows = []
    for m in models:
        for d in domains:
            vals = []
            for s in STRATS:
                hit = [c for c in summary["per_cell"]
                       if c["model"] == m and c["domain"] == d and c["strategy"] == s]
                vals.append(hit[0]["macro_f1"] if hit else None)
            if all(v is not None for v in vals):
                rows.append(vals)
    if len(rows) >= 3:
        arr = np.array(rows)
        chi2, p = stats.friedmanchisquare(*arr.T)
        k = arr.shape[1]; n = arr.shape[0]
        W = chi2 / (n * (k - 1))
        summary["friedman"] = dict(n_blocks=n, chi2=float(chi2), p=float(p), kendall_W=float(W))
        mean_rank = stats.rankdata(-arr, axis=1).mean(axis=0)
        md.append(f"- blocks(model×domain)={n}，χ²={chi2:.2f}，p={p:.4g}，Kendall's W={W:.3f}")
        md.append("- 平均名次（越小越好）: " +
                  ", ".join(f"{s}:{r:.2f}" for s, r in zip(STRATS, mean_rank)))

    # ---- 平凡基线 ----
    md.append("\n## 5. 平凡基线（按域，500 条抽样上）\n")
    for d in domains:
        ids_seen, gold = set(), []
        for r in recs:
            if r["domain"] == d and r["id"] not in ids_seen:
                ids_seen.add(r["id"]); gold.append(r["gold"])
        if not gold:
            continue
        g = np.array(gold)
        maj = max(set(gold), key=gold.count)
        f1_maj = f1_score(g, np.array([maj] * len(g)), labels=LABELS,
                          average="macro", zero_division=0)
        rng2 = np.random.default_rng(SEED)
        f1_rnd = float(np.mean([f1_score(g, rng2.choice(LABELS, len(g)),
                                         labels=LABELS, average="macro", zero_division=0)
                                for _ in range(20)]))
        md.append(f"- {d}: majority(={maj}) macro-F1={f1_maj:.3f}；random macro-F1≈{f1_rnd:.3f}")
        summary.setdefault("trivial", {})[d] = dict(majority=maj, majority_f1=float(f1_maj),
                                                    random_f1=f1_rnd)

    json.dump(summary, open("summary.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open("REPORT.md", "w", encoding="utf-8").write("\n".join(md))
    print("wrote summary.json REPORT.md")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results.jsonl")
