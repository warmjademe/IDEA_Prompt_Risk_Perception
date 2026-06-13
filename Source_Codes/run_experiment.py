#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""舆情情绪识别 × 提示策略 × ollama 采集脚本（纯 stdlib，可续跑）。

每条记录: {domain,id,gold,strategy,model,pred,parse_ok,raw,latency_s}
续跑键: (domain,id,strategy,model) —— 已存在即跳过，追加写。
GPU 礼让: 启动时与每 50 条检查一次，他人进程占 >3GB 显存则等待。
"""
import json, re, sys, time, argparse, os, glob, subprocess, urllib.request
import threading
from concurrent.futures import ThreadPoolExecutor

OLLAMA = "http://127.0.0.1:11434/api/chat"
SEED = 2026
LABELS = ["happy", "angry", "sad", "fear", "surprise", "neutral"]
CN = {"happy": "开心", "angry": "愤怒", "sad": "悲伤",
      "fear": "恐惧", "surprise": "惊讶", "neutral": "中性"}
CN2EN = {v: k for k, v in CN.items()}
# 解析别名（中英 + 常见同义）
ALIAS = {
    "开心": "happy", "高兴": "happy", "快乐": "happy", "积极": "happy", "喜悦": "happy", "happy": "happy", "joy": "happy", "positive": "happy",
    "愤怒": "angry", "生气": "angry", "气愤": "angry", "angry": "angry", "anger": "angry",
    "悲伤": "sad", "伤心": "sad", "难过": "sad", "悲哀": "sad", "sad": "sad", "sadness": "sad",
    "恐惧": "fear", "害怕": "fear", "担忧": "fear", "恐慌": "fear", "fear": "fear", "afraid": "fear",
    "惊讶": "surprise", "吃惊": "surprise", "震惊": "surprise", "surprise": "surprise", "surprised": "surprise",
    "中性": "neutral", "中立": "neutral", "无情绪": "neutral", "客观": "neutral", "neutral": "neutral", "none": "neutral",
}
LABEL_LIST_CN = "、".join(CN[l] for l in LABELS)

DEFS = ("开心：表达喜悦、满意、赞美、祝福等正面情绪；"
        "愤怒：表达生气、不满、谴责、讽刺抨击；"
        "悲伤：表达难过、哀伤、失落、同情；"
        "恐惧：表达害怕、担忧、恐慌、焦虑；"
        "惊讶：表达出乎意料、震惊、难以置信；"
        "中性：客观陈述事实，没有明显情绪倾向。")

def build_prompt(strategy, text, fewshot):
    base_q = (f"请判断下面这条微博表达的主要情绪，只能从以下六类中选择一个："
              f"{LABEL_LIST_CN}。只输出情绪类别这一个词，不要输出其他内容。\n"
              f"微博：{text}\n情绪：")
    if strategy == "S1_direct":
        return base_q
    if strategy == "S2_role":
        return ("你是一名高校网络舆情分析员，负责研判校园网络舆情中网民的情绪状态，"
                "你的判断将用于舆情风险预警。\n" + base_q)
    if strategy == "S3_def":
        return f"六类情绪的判定标准如下。{DEFS}\n{base_q}"
    if strategy == "S4_few":
        shots = "\n".join(f"微博：{fewshot[lb]}\n情绪：{CN[lb]}" for lb in LABELS)
        return (f"请判断微博表达的主要情绪，只能从以下六类中选择一个：{LABEL_LIST_CN}。"
                f"参考下面的示例，只输出情绪类别。\n{shots}\n微博：{text}\n情绪：")
    if strategy == "S5_cot":
        return (f"请先用一两句话分析下面这条微博的内容和情感倾向，"
                f"然后在最后单独一行，以「情绪：X」的格式给出结论，"
                f"X 只能从以下六类中选择一个：{LABEL_LIST_CN}。\n微博：{text}")
    if strategy == "S6_json":
        return (f"请判断下面这条微博表达的主要情绪，类别只能从以下六类中选择一个："
                f'{LABEL_LIST_CN}。以 JSON 格式输出，形如 {{"情绪": "类别"}}，'
                f"不要输出任何其他内容。\n微博：{text}")
    raise ValueError(strategy)

STRATEGIES = ["S1_direct", "S2_role", "S3_def", "S4_few", "S5_cot", "S6_json"]

def call_ollama(model, prompt, num_predict):
    body = {"model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0, "seed": SEED, "num_predict": num_predict}}
    if model.startswith("qwen3"):
        body["think"] = False
    req = urllib.request.Request(OLLAMA, json.dumps(body).encode("utf-8"),
                                 {"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        out = json.loads(r.read().decode("utf-8"))
    return out["message"]["content"], time.time() - t0

def parse_label(raw, strategy):
    text = raw.strip()
    # 去掉可能漏出的 think 块
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    if strategy == "S6_json":
        m = re.search(r"\{.*?\}", text, re.S)
        if m:
            try:
                obj = json.loads(m.group(0))
                for v in obj.values():
                    v = str(v).strip().lower()
                    if v in ALIAS:
                        return ALIAS[v], True
            except Exception:
                pass
    if strategy == "S5_cot":
        ms = re.findall(r"情绪[:：]\s*[「\"']?([^\s「」\"'。，,]+)", text)
        for cand in reversed(ms):
            c = cand.strip().lower()
            if c in ALIAS:
                return ALIAS[c], True
    # 通用：先试整串精确匹配，再扫别名
    low = text.lower().strip().strip("。.！!「」\"'**")
    if low in ALIAS:
        return ALIAS[low], True
    found = []
    for k, v in ALIAS.items():
        if k in text.lower():
            found.append((text.lower().rfind(k), v))
    if found:
        found.sort()
        return found[-1][1], len(set(v for _, v in found)) == 1
    return None, False

def gpu_others_busy():
    """他人进程占 >3GB 显存则 True（ollama 自身不算他人）。"""
    try:
        q = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20).stdout.strip()
        used = 0
        for line in q.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3 and "ollama" not in parts[1]:
                used += int(parts[2])
        return used > 3000
    except Exception:
        return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--domains", default="usual,virus")
    ap.add_argument("--strategies", default="all")
    ap.add_argument("--data_dir", default="data")
    ap.add_argument("--out", default="results.jsonl")
    ap.add_argument("--limit", type=int, default=0, help="每域每策略最多跑多少条（冒烟用）")
    ap.add_argument("--workers", type=int, default=1, help="并发线程数（ollama 服务端支持并行时提速）")
    args = ap.parse_args()
    strategies = STRATEGIES if args.strategies == "all" else args.strategies.split(",")

    # 续跑：读 cwd 下所有 results*.jsonl，防止换文件名/分片后重复采
    done = set()
    for f in set(glob.glob("results*.jsonl") + ([args.out] if os.path.exists(args.out) else [])):
        if not os.path.exists(f):
            continue
        for line in open(f, encoding="utf-8"):
            try:
                r = json.loads(line)
                done.add((r["domain"], r["id"], r["strategy"], r["model"]))
            except Exception:
                pass
    print(f"[resume] {len(done)} records already done", flush=True)

    fout = open(args.out, "a", encoding="utf-8")
    lock = threading.Lock()
    n_new = 0

    def work(item):
        domain, strat, s, fewshot = item
        if gpu_others_busy():
            with lock:
                print("[gpu] occupied by others, waiting 120s...", flush=True)
            while gpu_others_busy():
                time.sleep(120)
        prompt = build_prompt(strat, s["content"], fewshot)
        npred = 400 if strat == "S5_cot" else 64
        try:
            raw, lat = call_ollama(args.model, prompt, npred)
        except Exception as e:
            with lock:
                print(f"[err] {domain}/{s['id']}/{strat}: {e}", flush=True)
            time.sleep(10)
            try:
                raw, lat = call_ollama(args.model, prompt, npred)
            except Exception as e2:
                with lock:
                    print(f"[err2-skip] {e2}", flush=True)
                return 0
        pred, ok = parse_label(raw, strat)
        rec = json.dumps({"domain": domain, "id": s["id"], "gold": s["label"],
                          "strategy": strat, "model": args.model,
                          "pred": pred, "parse_ok": ok,
                          "raw": raw[:500], "latency_s": round(lat, 3)},
                         ensure_ascii=False)
        with lock:
            fout.write(rec + "\n")
            fout.flush()
        return 1

    for domain in args.domains.split(","):
        samples = [json.loads(l) for l in
                   open(f"{args.data_dir}/sample_{domain}_500.jsonl", encoding="utf-8")]
        fewshot = json.load(open(f"{args.data_dir}/fewshot_{domain}.json", encoding="utf-8"))
        if args.limit:
            samples = samples[:args.limit]
        for strat in strategies:
            todo = [(domain, strat, s, fewshot) for s in samples
                    if (domain, s["id"], strat, args.model) not in done]
            print(f"[{args.model}|{domain}|{strat}] todo={len(todo)} workers={args.workers}",
                  flush=True)
            t0 = time.time()
            if args.workers <= 1:
                results = [work(it) for it in todo]
            else:
                with ThreadPoolExecutor(max_workers=args.workers) as ex:
                    results = list(ex.map(work, todo))
            n_new += sum(results)
            if todo:
                print(f"  cell done in {(time.time()-t0)/60:.1f} min "
                      f"({(time.time()-t0)/max(len(todo),1):.2f}s/条)", flush=True)
    fout.close()
    print(f"[done] model={args.model} new={n_new}", flush=True)

if __name__ == "__main__":
    main()
