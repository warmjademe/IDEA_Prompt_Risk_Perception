# An Empirical Study of LLM Prompting Strategies for Online Public Opinion Risk Perception — Replication Package

> 🌐 Language: [中文](README.md) | **English**

This repository is the replication package for the paper *"An Empirical Study of Large Language Model Prompting Strategies for Online Public Opinion Risk Perception"*. It contains all experiment code, sampled data, raw predictions, and figures. The work is supported by a General Project of Philosophy and Social Science Research in Jiangsu Universities (Grant No. 2023SJSZ0993, PI: Li Fang).

## Overview

Using Weibo **6-class emotion recognition** and a derived **risk-signal detection** task (anger/sadness/fear → binary risk signal) as the test bed, we run a controlled empirical study over the public **SMP2020-EWECT** dataset (a *daily* domain and a *COVID-19 epidemic* domain): **6 prompting strategies × 5 open-source LLMs × 2 domains = 30,000 calls**. We answer four research questions: the main effect of prompting strategies, cross-model robustness, cross-context transfer, and the comparison against trivial baselines plus deployment cost. All models run locally via ollama on a single RTX 4090, with **zero paid API usage**.

- **6 prompting strategies**: S1 zero-shot direct, S2 role-play, S3 label definition, S4 few-shot, S5 chain-of-thought, S6 structured (JSON) output.
- **5 models**: Qwen3-8B, Qwen3-14B, GLM-4-9B, Gemma-3-12B, Llama-3.1-8B.
- **Statistics**: paired McNemar's test + Benjamini–Hochberg FDR correction + odds ratios; Friedman test + Kendall's W; bootstrap 95% confidence intervals.

## Key Findings

- The benefit of a prompting strategy depends heavily on the opinion context: in the daily domain most strategies are statistically indistinguishable from zero-shot direct answering, and few-shot can even be significantly harmful; in the epidemic domain, label definition, few-shot, and chain-of-thought yield significant gains with odds ratios of 2.96–7.40.
- The cross-model consistency of the strategy ranking is only weak to moderate (Kendall's W = 0.254); label definition is the only strategy that is simultaneously best on average rank, free of significant negative cases, and incurs no extra latency.
- The configuration that maximizes risk-signal recall differs from the one that maximizes macro-F1, and there is a catastrophic combination whose recall collapses to 0.159 — deployment requires re-validation under the recall criterion on the target domain.

## Repository Structure

```
Source_Codes/      Experiment and analysis code
  make_samples.py      Stratified sampling from SMP2020-EWECT + few-shot selection
  run_experiment.py    Main collection: 6 strategies × model × 2 domains; resumable, multi-threaded, GPU-courteous
  run_all.sh           Serial collection over the 5 models (BARK_URL env var controls push notifications)
  analyze.py           Statistical analysis → summary.json + REPORT.md
  make_figs.py         Figures (vector PDF, color-blind-safe palette)
  gen_tables.py        Generate LaTeX table fragments for the paper
  error_cases.py       Error analysis (confusion matrices + all-models-wrong samples)
  bert_baseline.py     [future work] fine-tuned BERT reference baseline
  mvsa_experiment.py   [future work] MVSA image-text multimodal three-condition experiment
  run_phase2.sh        [future work] BERT + MVSA relay script
data/              sample_{usual,virus}_500.jsonl stratified test sets; fewshot_{usual,virus}.json
results/           results_5m.jsonl raw predictions (30,000 records); summary.json; REPORT.md; error_cases.md
figs/              Paper figures (F1 heatmap, scale gradient, risk recall)
tables/            LaTeX table fragments
```

## Reproduction

1. **Environment**: Python 3.11; analysis depends on `numpy scipy scikit-learn matplotlib`; the collection scripts use only the standard library.
2. **Models**: pull the five models in ollama (`ollama pull qwen3:8b`, etc.).
3. **Data**: `data/` already contains the stratified test sets and few-shot examples; to re-sample from scratch, run `make_samples.py` (requires the original SMP2020-EWECT data).
4. **Collection**: `bash Source_Codes/run_all.sh`, or per model `python3 run_experiment.py --model qwen3:8b --out results.jsonl --workers 4`; results are appended and the run is resumable.
5. **Analysis & figures**:
   ```bash
   python analyze.py results/results_5m.jsonl    # → summary.json, REPORT.md
   python error_cases.py results/results_5m.jsonl
   python make_figs.py                           # → figs/*.pdf
   python gen_tables.py summary.json tables      # → tables/*.tex
   ```

`results/results_5m.jsonl` holds the raw predictions used in the paper; all reported statistics can be reproduced directly from it (see `results/REPORT.md`).

## Data Source

SMP2020-EWECT, a public Weibo emotion-classification evaluation dataset (6 emotions: happy/angry/sad/fear/surprise/neutral; *usual* daily domain and *virus* epidemic domain). This repository contains only a stratified subset of its test sets plus few-shot examples; for the original data see https://smp2020ewect.github.io/ .

## Note on Extension Scripts

`bert_baseline.py`, `mvsa_experiment.py`, and `run_phase2.sh` correspond to the fine-tuned-baseline comparison and the image-text multimodal extension, both listed as **future work** in the paper. They are included for reproducibility but their results are outside the scope of this paper.

## License

The code is released under the MIT License (see [LICENSE](LICENSE)). Use of the data subset is subject to the license and terms of the original SMP2020-EWECT dataset.
