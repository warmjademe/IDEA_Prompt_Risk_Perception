#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多模态扩展实验：MVSA-Single 测试集 487 图文对 × 3 条件 × 视觉 LLM（ollama）。

条件: TXT=仅文本 / IMG=仅图像 / MM=图文联合。三分类 positive/negative/neutral。
标签语义（已对样本核实）: 0=positive, 1=negative, 2=neutral。
可续跑: JSONL 按 (id, condition, model) 去重。
"""
import json, re, time, argparse, os, base64, urllib.request, subprocess

OLLAMA = "http://127.0.0.1:11434/api/chat"
SEED = 2026
ID2LB = {0: "positive", 1: "negative", 2: "neutral"}
ALIAS = {"positive": "positive", "negative": "negative", "neutral": "neutral",
         "正面": "positive", "负面": "negative", "中性": "neutral",
         "pos": "positive", "neg": "negative", "neu": "neutral"}

PROMPTS = {
    "TXT": ("Determine the overall sentiment of the following tweet. "
            "Answer with exactly one word: positive, negative, or neutral.\n"
            "Tweet: {text}\nSentiment:"),
    "IMG": ("Determine the overall sentiment expressed by this image posted on social media. "
            "Answer with exactly one word: positive, negative, or neutral.\nSentiment:"),
    "MM":  ("Determine the overall sentiment of this social media post, considering BOTH "
            "the attached image and the tweet text together. "
            "Answer with exactly one word: positive, negative, or neutral.\n"
            "Tweet: {text}\nSentiment:"),
}

def gpu_others_busy():
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

def load_image_b64(path, max_side=768):
    """大图缩放后再编码，降低视觉前处理开销；PIL 不可用则原图直传。"""
    try:
        import io
        from PIL import Image
        im = Image.open(path).convert("RGB")
        if max(im.size) > max_side:
            im.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=90)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return base64.b64encode(open(path, "rb").read()).decode()

def call(model, prompt, img_b64):
    msg = {"role": "user", "content": prompt}
    if img_b64:
        msg["images"] = [img_b64]
    body = {"model": model, "messages": [msg], "stream": False,
            "options": {"temperature": 0, "seed": SEED, "num_predict": 32}}
    req = urllib.request.Request(OLLAMA, json.dumps(body).encode("utf-8"),
                                 {"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        out = json.loads(r.read().decode("utf-8"))
    return out["message"]["content"], time.time() - t0

def parse(raw):
    low = raw.strip().lower()
    head = re.split(r"[\s\.,!:：。]+", low)
    for tok in head[:6]:
        if tok in ALIAS:
            return ALIAS[tok], True
    found = [(low.rfind(k), v) for k, v in ALIAS.items() if k in low]
    if found:
        found.sort()
        return found[-1][1], len(set(v for _, v in found)) == 1
    return None, False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemma3:12b")
    ap.add_argument("--data_dir", default="mvsa")
    ap.add_argument("--test_json", default="data/mvsa_test.json")
    ap.add_argument("--out", default="mvsa_results.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    test = json.load(open(args.test_json, encoding="utf-8"))
    items = sorted(test.items(), key=lambda kv: int(kv[0]))
    if args.limit:
        items = items[:args.limit]

    done = set()
    if os.path.exists(args.out):
        for line in open(args.out, encoding="utf-8"):
            try:
                r = json.loads(line)
                done.add((r["id"], r["condition"], r["model"]))
            except Exception:
                pass
    print(f"[resume] {len(done)} done", flush=True)

    fout = open(args.out, "a", encoding="utf-8")
    n = 0
    for cond in ["TXT", "IMG", "MM"]:
        todo = [(k, v) for k, v in items if (k, cond, args.model) not in done]
        print(f"[{args.model}|{cond}] todo={len(todo)}", flush=True)
        for i, (k, v) in enumerate(todo):
            while gpu_others_busy():
                print("[gpu] waiting...", flush=True)
                time.sleep(120)
            try:
                text = open(f"{args.data_dir}/data/{k}.txt", encoding="utf-8",
                            errors="replace").read().strip()
            except FileNotFoundError:
                continue
            img = None
            if cond in ("IMG", "MM"):
                ipath = f"{args.data_dir}/data/{k}.jpg"
                if not os.path.exists(ipath):
                    continue
                img = load_image_b64(ipath)
            prompt = PROMPTS[cond].format(text=text)
            try:
                raw, lat = call(args.model, prompt, img)
            except Exception as e:
                print(f"[err] {k}/{cond}: {e}", flush=True)
                time.sleep(10)
                try:
                    raw, lat = call(args.model, prompt, img)
                except Exception as e2:
                    print(f"[err2-skip] {e2}", flush=True)
                    continue
            pred, ok = parse(raw)
            fout.write(json.dumps({
                "id": k, "gold": ID2LB[v["label"]],
                "gold_text": ID2LB.get(v.get("text_label"), None),
                "gold_img": ID2LB.get(v.get("img_label"), None),
                "condition": cond, "model": args.model,
                "pred": pred, "parse_ok": ok, "raw": raw[:200],
                "latency_s": round(lat, 3)}, ensure_ascii=False) + "\n")
            fout.flush()
            n += 1
            if (i + 1) % 50 == 0:
                print(f"  ...{i+1}/{len(todo)} ({lat:.2f}s)", flush=True)
    fout.close()
    print(f"[done] new={n}", flush=True)

if __name__ == "__main__":
    main()
