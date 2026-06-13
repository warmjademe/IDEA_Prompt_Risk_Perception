#!/bin/bash
# Phase-2 接力：等主采集(run_all.sh)结束 → 卸载 ollama 模型腾显存 → BERT 基线×2 域
# → MVSA 多模态×gemma3:12b → 统计分析 → Bark。
# 用法: setsid nohup bash run_phase2.sh > run_phase2.log 2>&1 &
cd "$(dirname "$0")"
BARK="${BARK_URL:-}"  # 设置 BARK_URL 环境变量以启用推送通知（脱敏）

echo "[phase2] waiting for run_all.sh to finish..."
while pgrep -f "bash run_all.sh" > /dev/null; do sleep 300; done
echo "[phase2] run_all.sh finished at $(date '+%F %T')"

# 让 ollama 立即卸载所有驻留模型，给 BERT 腾显存
for m in qwen3:8b llama3.1:8b glm4:9b gemma3:12b qwen3:14b qwen3:32b; do
  curl -s http://127.0.0.1:11434/api/generate -d "{\"model\":\"$m\",\"keep_alive\":0}" > /dev/null
done
sleep 60

source ~/miniconda3/etc/profile.d/conda.sh
conda activate IDEA_Prompt_Risk_Perception

echo "[phase2] BERT usual..."
python bert_baseline.py --domain usual --model_dir bert-base-chinese 2>&1 | tail -5
echo "[phase2] BERT virus..."
python bert_baseline.py --domain virus --model_dir bert-base-chinese 2>&1 | tail -5

echo "[phase2] MVSA multimodal (gemma3:12b)..."
python3 mvsa_experiment.py --model gemma3:12b --test_json data/mvsa_test.json
N=$(wc -l < mvsa_results.jsonl 2>/dev/null || echo 0)

echo "[phase2] analyze..."
python analyze.py results.jsonl 2>&1 | tail -3

curl -s "$BARK/Phase2全部完成/BERT基线+MVSA多模态(${N}条)+统计分析跑完,可以回填论文了" > /dev/null
echo "[phase2] ALL PHASE2 DONE $(date '+%F %T')"
