# 面向网络舆情风险感知的大语言模型提示策略实证研究 — 复现包

> 🌐 Language: **中文** | [English](README.en.md)

本仓库是论文《面向网络舆情风险感知的大语言模型提示策略实证研究》的复现包，包含全部实验代码、抽样数据、原始预测结果与图表。研究受江苏高校哲学社会科学研究一般项目（项目编号 2023SJSZ0993，主持人：李芳）资助。

## 研究简介

以微博舆情**情绪识别（6 类）**与派生的**风险信号检测**（愤怒/悲伤/恐惧 → 风险信号的二分类）为任务载体，在公开数据集 **SMP2020-EWECT** 的日常域与疫情域上，对 **6 种提示策略 × 5 个开源大语言模型 × 2 个舆情域 = 30,000 次调用**开展受控实证，回答四个研究问题：策略主效应、跨模型稳健性、跨情境迁移、与平凡基线的对比及部署成本。全部模型经 ollama 本地部署于单张 RTX 4090，全程零付费 API。

- **6 种提示策略**：S1 零样本直答、S2 角色扮演、S3 标签定义、S4 少样本、S5 思维链、S6 结构化输出。
- **5 个模型**：Qwen3-8B、Qwen3-14B、GLM-4-9B、Gemma-3-12B、Llama-3.1-8B。
- **统计方法**：McNemar 配对检验 + BH-FDR 多重校正 + 优势比；Friedman 检验 + Kendall's W；bootstrap 95% 置信区间。

## 主要发现

- 提示策略的收益高度依赖舆情情境：日常域各策略与零样本直答基本无异、少样本反而可能显著有害；疫情域标签定义、少样本与思维链取得优势比 2.96～7.40 的显著增益。
- 策略排序的跨模型一致性仅为弱至中等（Kendall's W = 0.254）；标签定义是唯一兼具最优平均名次、无显著负例与零额外时延的策略。
- 风险信号召回口径与宏平均 F1 口径的最优配置不一致，存在召回坍缩至 0.159 的危险组合，部署前须按目标域以召回口径重新验证。

## 目录结构

```
Source_Codes/      实验与分析代码
  make_samples.py      从 SMP2020-EWECT 分层抽样 + 选 few-shot 示例
  run_experiment.py    主采集：6 策略 × 模型 × 2 域，可续跑、多线程、GPU 礼让
  run_all.sh           5 个模型串行采集（BARK_URL 环境变量控制推送通知）
  analyze.py           统计分析 → summary.json + REPORT.md
  make_figs.py         出图（矢量 PDF，色盲安全配色）
  gen_tables.py        生成论文 LaTeX 表格片段
  error_cases.py       错误案例分析（混淆矩阵 + 全模型一致错样本）
  bert_baseline.py     [后续工作] 微调 BERT 参照基线
  mvsa_experiment.py   [后续工作] MVSA 图文多模态三条件实验
  run_phase2.sh        [后续工作] BERT + MVSA 接力脚本
data/              sample_{usual,virus}_500.jsonl 分层抽样测试集；fewshot_{usual,virus}.json
results/           results_5m.jsonl 原始预测（30,000 条）；summary.json；REPORT.md；error_cases.md
figs/              论文图（F1 热力图、规模梯度、风险召回）
tables/            论文 LaTeX 表格片段
```

## 复现步骤

1. **环境**：Python 3.11，分析依赖 `numpy scipy scikit-learn matplotlib`；采集脚本仅用标准库。
2. **模型**：在 ollama 中拉取上述 5 个模型（`ollama pull qwen3:8b` 等）。
3. **数据**：`data/` 已含分层抽样的测试集与 few-shot 示例；如需从头抽样，运行 `make_samples.py`（需 SMP2020-EWECT 原始数据）。
4. **采集**：`bash Source_Codes/run_all.sh`，或单模型 `python3 run_experiment.py --model qwen3:8b --out results.jsonl --workers 4`；结果追加写入、可断点续跑。
5. **分析与出图**：
   ```bash
   python analyze.py results/results_5m.jsonl    # → summary.json, REPORT.md
   python error_cases.py results/results_5m.jsonl
   python make_figs.py                           # → figs/*.pdf
   python gen_tables.py summary.json tables      # → tables/*.tex
   ```

`results/results_5m.jsonl` 为论文使用的原始预测，可直接据此复现全部统计数字（见 `results/REPORT.md`）。

## 数据来源

SMP2020-EWECT 微博情绪分类评测公开数据集（6 类情绪：happy/angry/sad/fear/surprise/neutral；usual 日常域、virus 疫情域）。本仓库仅含从其测试集分层抽样的子集与 few-shot 示例，原始数据请见 https://smp2020ewect.github.io/ 。

## 关于扩展脚本

`bert_baseline.py`、`mvsa_experiment.py`、`run_phase2.sh` 对应论文中列为**后续工作**的微调小模型对比与图文多模态扩展，随包提供以备复现，其结果不在本论文范围内。

## 许可

代码以 MIT 许可证发布（见 [LICENSE](LICENSE)）。数据子集的使用须遵循 SMP2020-EWECT 原始数据集的许可与使用条款。
