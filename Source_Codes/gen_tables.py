#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 summary.json 生成论文 LaTeX 表格片段到 LATEX/tables/*.tex（main.tex 用 \\input 引）。
纯 stdlib，本地可跑：python3 gen_tables.py <summary.json> <输出目录>
qwen3:32b 数据齐后重跑本脚本即自动更新所有表。
"""
import json, sys, os

SU = sys.argv[1] if len(sys.argv) > 1 else "summary.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "LATEX/tables"
os.makedirs(OUT, exist_ok=True)
s = json.load(open(SU, encoding="utf-8"))

STRATS = ["S1_direct", "S2_role", "S3_def", "S4_few", "S5_cot", "S6_json"]
SHORT = {"S1_direct": "S1直答", "S2_role": "S2角色", "S3_def": "S3定义",
         "S4_few": "S4少样本", "S5_cot": "S5思维链", "S6_json": "S6结构化"}
MODEL_ORDER = ["qwen3:8b", "qwen3:14b", "glm4:9b", "gemma3:12b", "llama3.1:8b"]
MODEL_TEX = {"qwen3:8b": "Qwen3-8B", "qwen3:14b": "Qwen3-14B",
             "glm4:9b": "GLM-4-9B", "gemma3:12b": "Gemma-3-12B", "llama3.1:8b": "Llama-3.1-8B"}
DOM = {"usual": "日常域", "virus": "疫情域"}

cells = {(c["model"], c["domain"], c["strategy"]): c for c in s["per_cell"]}
risk = {(c["model"], c["domain"], c["strategy"]): c for c in s.get("risk", [])}
models = [m for m in MODEL_ORDER if any(k[0] == m for k in cells)]
missing = [m for m in MODEL_ORDER if m not in models]

# ---- 表: 主结果 macro-F1 ----
lines = []
lines.append(r"\begin{tabular}{llcccccc}")
lines.append(r"\toprule")
lines.append("域 & 模型 & " + " & ".join(SHORT[x] for x in STRATS) + r" \\")
lines.append(r"\midrule")
for d in ["usual", "virus"]:
    for i, m in enumerate(MODEL_ORDER):
        first = f"\\multirow{{{len(MODEL_ORDER)}}}{{*}}{{{DOM[d]}}} " if i == 0 else ""
        if m in models:
            vals = [cells.get((m, d, st), {}).get("macro_f1") for st in STRATS]
            best = max(v for v in vals if v is not None)
            cs = [(f"\\textbf{{{v:.3f}}}" if v == best else f"{v:.3f}") if v is not None
                  else "--" for v in vals]
        else:
            cs = [r"\textcolor{red}{待补}"] * len(STRATS)
        lines.append(f"{first}& {MODEL_TEX[m]} & " + " & ".join(cs) + r" \\")
    if d == "usual":
        lines.append(r"\midrule")
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
open(f"{OUT}/tab_main_f1.tex", "w", encoding="utf-8").write("\n".join(lines))

# ---- 表: McNemar 显著项 ----
sig = [t for t in s["mcnemar"] if t.get("p_adj", 1) < 0.05]
sig.sort(key=lambda t: (t["domain"], t["strategy"], t["model"]))
lines = [r"\begin{tabular}{llcccc}", r"\toprule",
         r"域 & 模型 & 策略 & 优势比 & 精确$p$ & 校正$p$ \\", r"\midrule"]
for t in sig:
    direction = "" if t["odds_ratio"] >= 1 else r"$\downarrow$"
    p = f"{t['p']:.2e}".replace("e-0", "e-").replace("e-", r"\times 10^{-") + "}"
    pa = f"{t['p_adj']:.2e}".replace("e-0", "e-").replace("e-", r"\times 10^{-") + "}"
    lines.append(f"{DOM[t['domain']]} & {MODEL_TEX.get(t['model'], t['model'])} & "
                 f"{SHORT[t['strategy']]}{direction} & {t['odds_ratio']:.2f} & "
                 f"${p}$ & ${pa}$ \\\\")
lines += [r"\bottomrule", r"\end{tabular}"]
open(f"{OUT}/tab_mcnemar_sig.tex", "w", encoding="utf-8").write("\n".join(lines))

# ---- 表: 风险信号召回率 ----
lines = [r"\begin{tabular}{llcccccc}", r"\toprule",
         "域 & 模型 & " + " & ".join(SHORT[x] for x in STRATS) + r" \\", r"\midrule"]
for d in ["usual", "virus"]:
    for i, m in enumerate(MODEL_ORDER):
        first = f"\\multirow{{{len(MODEL_ORDER)}}}{{*}}{{{DOM[d]}}} " if i == 0 else ""
        if m in models:
            vals = [risk.get((m, d, st), {}).get("recall") for st in STRATS]
            best = max(v for v in vals if v is not None)
            cs = [(f"\\textbf{{{v:.3f}}}" if v == best else f"{v:.3f}") if v is not None
                  else "--" for v in vals]
        else:
            cs = [r"\textcolor{red}{待补}"] * len(STRATS)
        lines.append(f"{first}& {MODEL_TEX[m]} & " + " & ".join(cs) + r" \\")
    if d == "usual":
        lines.append(r"\midrule")
lines += [r"\bottomrule", r"\end{tabular}"]
open(f"{OUT}/tab_risk_recall.tex", "w", encoding="utf-8").write("\n".join(lines))

# ---- 表: 时延中位数（usual 域）----
lines = [r"\begin{tabular}{lcccccc}", r"\toprule",
         "模型 & " + " & ".join(SHORT[x] for x in STRATS) + r" \\", r"\midrule"]
for m in MODEL_ORDER:
    if m in models:
        vals = [cells.get((m, "usual", st), {}).get("med_latency") for st in STRATS]
        cs = [f"{v:.2f}" if v is not None else "--" for v in vals]
    else:
        cs = [r"\textcolor{red}{待补}"] * len(STRATS)
    lines.append(f"{MODEL_TEX[m]} & " + " & ".join(cs) + r" \\")
lines += [r"\bottomrule", r"\end{tabular}"]
open(f"{OUT}/tab_latency.tex", "w", encoding="utf-8").write("\n".join(lines))

# ---- 摘要/正文用的关键数字 ----
fr = s.get("friedman", {})
facts = {
    "models_done": models, "models_missing": missing,
    "friedman": fr,
    "n_sig": len(sig), "n_tests": len(s["mcnemar"]),
    "trivial": s.get("trivial", {}),
}
# usual/virus 最优格
for d in ["usual", "virus"]:
    best = max((c for c in s["per_cell"] if c["domain"] == d), key=lambda c: c["macro_f1"])
    facts[f"best_{d}"] = {k: best[k] for k in ("model", "strategy", "macro_f1", "ci")}
json.dump(facts, open(f"{OUT}/facts.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("tables written to", OUT, "| missing models:", missing)
