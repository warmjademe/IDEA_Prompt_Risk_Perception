#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""错误案例分析：混淆矩阵 + 典型失败样例（全模型一致答错的题）→ error_cases.md
用法: python error_cases.py results.jsonl
"""
import json, sys
from collections import defaultdict, Counter
import numpy as np

LABELS = ["happy", "angry", "sad", "fear", "surprise", "neutral"]
CN = {"happy": "开心", "angry": "愤怒", "sad": "悲伤", "fear": "恐惧",
      "surprise": "惊讶", "neutral": "中性", None: "解析失败"}

def main(path):
    recs = {}
    for line in open(path, encoding="utf-8"):
        try:
            r = json.loads(line)
            recs[(r["domain"], r["id"], r["strategy"], r["model"])] = r
        except Exception:
            pass
    rows = list(recs.values())
    models = sorted(set(r["model"] for r in rows))
    out = ["# 错误案例分析\n"]

    # 全局混淆（S1 基准，全模型合并）
    for d in sorted(set(r["domain"] for r in rows)):
        cm = Counter()
        for r in rows:
            if r["domain"] == d and r["strategy"] == "S1_direct":
                cm[(r["gold"], r["pred"])] += 1
        out.append(f"\n## {d} 域 S1 基准混淆矩阵（行=真值，列=预测，全模型合并）\n")
        out.append("| 真值\\预测 | " + " | ".join(CN[l] for l in LABELS) + " | 解析失败 |")
        out.append("|" + "---|" * (len(LABELS) + 2))
        for g in LABELS:
            row = [str(cm.get((g, p), 0)) for p in LABELS] + [str(cm.get((g, None), 0))]
            out.append(f"| {CN[g]} | " + " | ".join(row) + " |")
        top_conf = sorted(((k, v) for k, v in cm.items() if k[0] != k[1] and k[1]),
                          key=lambda kv: -kv[1])[:6]
        out.append("\n主要混淆对：" + "；".join(
            f"{CN[g]}→{CN[p]}({n}次)" for (g, p), n in top_conf))

    # 难题：S1 下全部模型都答错的样本（候选讽刺/缺模态例子）
    by_item = defaultdict(dict)
    for r in rows:
        if r["strategy"] == "S1_direct":
            by_item[(r["domain"], r["id"])][r["model"]] = r
    out.append("\n## 全模型一致答错的样本（S1，前 20 条，候选讽刺反语/模态缺失归因）\n")
    n_shown = 0
    samples = {}
    for dom in ["usual", "virus"]:
        try:
            for l in open(f"data/sample_{dom}_500.jsonl", encoding="utf-8"):
                s = json.loads(l)
                samples[(dom, s["id"])] = s["content"]
        except FileNotFoundError:
            pass
    for (d, i), mm in sorted(by_item.items()):
        if len(mm) < len(models):
            continue
        if all(v["pred"] != v["gold"] for v in mm.values()):
            r0 = next(iter(mm.values()))
            preds = Counter(CN[v["pred"]] for v in mm.values())
            txt = samples.get((d, i), "")[:80]
            out.append(f"- [{d}/{i}] 真值={CN[r0['gold']]}，预测={dict(preds)}：{txt}")
            n_shown += 1
            if n_shown >= 20:
                break
    open("error_cases.md", "w", encoding="utf-8").write("\n".join(out))
    print(f"error_cases.md written ({n_shown} hard cases)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results.jsonl")
