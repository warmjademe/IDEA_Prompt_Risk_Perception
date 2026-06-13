#!/bin/bash
# NAS 全量采集：6 模型串行（小→大），可续跑，结尾 Bark 推送。
# 用法: setsid nohup bash run_all.sh > run_all.log 2>&1 &
cd "$(dirname "$0")"
BARK="${BARK_URL:-}"  # 设置 BARK_URL 环境变量以启用推送通知（脱敏）
MODELS="qwen3:8b llama3.1:8b glm4:9b gemma3:12b qwen3:14b"  # 论文最终用 5 个模型
START=$(date +%s)
for m in $MODELS; do
  echo "===== [$(date '+%F %T')] start $m ====="
  python3 run_experiment.py --model "$m" --out results.jsonl --workers 4
  echo "===== [$(date '+%F %T')] done $m ====="
done
ELAPSED=$(( ($(date +%s) - START) / 60 ))
N=$(wc -l < results.jsonl)
curl -s "$BARK/提示策略实验完成/全部5模型跑完,共${N}条记录,耗时${ELAPSED}分钟" > /dev/null
echo "ALL DONE: $N records, ${ELAPSED} min"
