#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""出图（矢量 PDF，色盲安全）。在 NAS conda env 跑：python make_figs.py
输入: summary.json（analyze.py 产物）；输出: figs/*.pdf
中文字体经 addfont 强注册（DroidSansFallbackFull.ttf 与脚本同目录）。
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "DroidSansFallbackFull.ttf")
if os.path.exists(FONT):
    font_manager.fontManager.addfont(FONT)
    cjk = font_manager.FontProperties(fname=FONT).get_name()
    # 拉丁用 DejaVu，CJK 回退到 Droid（matplotlib>=3.6 支持字体回退链）
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", cjk]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42

# Okabe-Ito 色盲安全配色
OI = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
STRATS = ["S1_direct", "S2_role", "S3_def", "S4_few", "S5_cot", "S6_json"]
SHORT = {"S1_direct": "S1直答", "S2_role": "S2角色", "S3_def": "S3定义",
         "S4_few": "S4少样本", "S5_cot": "S5思维链", "S6_json": "S6结构化"}
DOM_CN = {"usual": "日常域", "virus": "疫情域"}

s = json.load(open("summary.json", encoding="utf-8"))
cells = s["per_cell"]
models = sorted(set(c["model"] for c in cells))
domains = sorted(set(c["domain"] for c in cells))
os.makedirs("figs", exist_ok=True)

def get(model, domain, strat, field="macro_f1", src=None):
    for c in (src or cells):
        if c["model"] == model and c["domain"] == domain and c["strategy"] == strat:
            return c.get(field)
    return np.nan

# ---- 图1: 模型×策略 macro-F1 热力图（两域两面板）----
fig, axes = plt.subplots(1, len(domains), figsize=(6.0 * len(domains), 0.55 * len(models) + 1.8))
axes = np.atleast_1d(axes)
for ax, d in zip(axes, domains):
    M = np.array([[get(m, d, st) for st in STRATS] for m in models], dtype=float)
    im = ax.imshow(M, cmap="viridis", aspect="auto",
                   vmin=np.nanmin(M) - 0.02, vmax=np.nanmax(M) + 0.02)
    ax.set_xticks(range(len(STRATS)), [SHORT[x] for x in STRATS], rotation=20)
    ax.set_yticks(range(len(models)), models)
    ax.set_title(f"{DOM_CN.get(d, d)}（宏平均F1）")
    for i in range(len(models)):
        for j in range(len(STRATS)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.3f}", ha="center", va="center",
                        color="white" if M[i, j] < np.nanmean(M) else "black", fontsize=8)
fig.tight_layout()
fig.savefig("figs/fig_heatmap_f1.pdf", bbox_inches="tight")
plt.close(fig)

# ---- 图2: Qwen3 规模梯度（8B/14B/32B）----
qwen = [m for m in models if m.startswith("qwen3")]
def size_of(m):
    return int(m.split(":")[1].rstrip("b"))
qwen = sorted(qwen, key=size_of)
if len(qwen) >= 2:
    fig, axes = plt.subplots(1, len(domains), figsize=(5.2 * len(domains), 3.6), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, d in zip(axes, domains):
        for k, st in enumerate(STRATS):
            ys = [get(m, d, st) for m in qwen]
            ax.plot([size_of(m) for m in qwen], ys, marker="o",
                    color=OI[k], label=SHORT[st])
        ax.set_xticks([size_of(m) for m in qwen], [f"{size_of(m)}B" for m in qwen])
        ax.set_xlabel("Qwen3 参数规模")
        ax.set_title(DOM_CN.get(d, d))
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("宏平均F1")
    axes[-1].legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig("figs/fig_scale.pdf", bbox_inches="tight")
    plt.close(fig)

# ---- 图3: 风险信号召回率（策略×模型，两域）----
risk = s.get("risk", [])
fig, axes = plt.subplots(1, len(domains), figsize=(6.0 * len(domains), 3.6), sharey=True)
axes = np.atleast_1d(axes)
w = 0.8 / max(len(models), 1)
for ax, d in zip(axes, domains):
    for i, m in enumerate(models):
        ys = [get(m, d, st, "recall", risk) for st in STRATS]
        ax.bar(np.arange(len(STRATS)) + i * w, ys, w, color=OI[i % len(OI)], label=m)
    ax.set_xticks(np.arange(len(STRATS)) + 0.4 - w / 2, [SHORT[x] for x in STRATS], rotation=20)
    ax.set_title(f"{DOM_CN.get(d, d)}（风险信号召回率）")
    ax.set_ylim(0.5, 1.0)
    ax.grid(axis="y", alpha=0.3)
axes[0].set_ylabel("召回率")
axes[-1].legend(fontsize=7)
fig.tight_layout()
fig.savefig("figs/fig_risk_recall.pdf", bbox_inches="tight")
plt.close(fig)

print("figs written:", os.listdir("figs"))
