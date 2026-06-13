#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BERT 参照基线：bert-base-chinese 在两域 train 上各微调一次，在同一 500 条抽样上评估。

用法: python bert_baseline.py --domain usual --model_dir ./bert-base-chinese
输出: bert_results.json（macro-F1/acc/风险信号 F1·recall + 训练耗时）
"""
import json, time, argparse, random
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (BertTokenizerFast, BertForSequenceClassification,
                          get_linear_schedule_with_warmup)
from sklearn.metrics import f1_score, accuracy_score

LABELS = ["happy", "angry", "sad", "fear", "surprise", "neutral"]
L2I = {l: i for i, l in enumerate(LABELS)}
RISK = {"angry", "sad", "fear"}
SEED = 2026

def set_seed(s):
    random.seed(s); np.random.seed(s)
    torch.manual_seed(s); torch.cuda.manual_seed_all(s)

class DS(Dataset):
    def __init__(self, rows, tok, maxlen=128):
        self.enc = tok([r["content"] for r in rows], truncation=True,
                       max_length=maxlen, padding="max_length")
        self.y = [L2I[r["label"]] for r in rows]
    def __len__(self):
        return len(self.y)
    def __getitem__(self, i):
        return {k: torch.tensor(v[i]) for k, v in self.enc.items()} | \
               {"labels": torch.tensor(self.y[i])}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, choices=["usual", "virus"])
    ap.add_argument("--train_file", default=None)
    ap.add_argument("--test_file", default=None)
    ap.add_argument("--model_dir", default="bert-base-chinese")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--lr", type=float, default=2e-5)
    args = ap.parse_args()
    set_seed(SEED)

    train_file = args.train_file or f"data/{args.domain}_train.txt"
    test_file = args.test_file or f"data/sample_{args.domain}_500.jsonl"
    train = [r for r in json.load(open(train_file, encoding="utf-8"))
             if r["label"] in LABELS and r["content"].strip()]
    test = [json.loads(l) for l in open(test_file, encoding="utf-8")]

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tok = BertTokenizerFast.from_pretrained(args.model_dir)
    model = BertForSequenceClassification.from_pretrained(
        args.model_dir, num_labels=len(LABELS)).to(dev)
    dl = DataLoader(DS(train, tok), batch_size=args.bs, shuffle=True,
                    generator=torch.Generator().manual_seed(SEED))
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    steps = len(dl) * args.epochs
    sch = get_linear_schedule_with_warmup(opt, int(steps * 0.1), steps)

    t0 = time.time()
    model.train()
    for ep in range(args.epochs):
        tot = 0.0
        for b in dl:
            b = {k: v.to(dev) for k, v in b.items()}
            out = model(**b)
            out.loss.backward()
            opt.step(); sch.step(); opt.zero_grad()
            tot += out.loss.item()
        print(f"[{args.domain}] epoch {ep+1} loss {tot/len(dl):.4f}", flush=True)
    train_min = (time.time() - t0) / 60

    model.eval()
    preds = []
    with torch.no_grad():
        for i in range(0, len(test), 64):
            chunk = test[i:i+64]
            enc = tok([r["content"] for r in chunk], truncation=True, max_length=128,
                      padding=True, return_tensors="pt").to(dev)
            preds.extend(model(**enc).logits.argmax(-1).cpu().tolist())
    gold = [r["label"] for r in test]
    pred = [LABELS[p] for p in preds]
    g_r = np.array([g in RISK for g in gold]); p_r = np.array([p in RISK for p in pred])
    tp = int((g_r & p_r).sum()); fp = int((~g_r & p_r).sum()); fn = int((g_r & ~p_r).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    res = {"domain": args.domain, "n_train": len(train), "n_test": len(test),
           "macro_f1": f1_score(gold, pred, labels=LABELS, average="macro", zero_division=0),
           "acc": accuracy_score(gold, pred),
           "risk_f1": 2*prec*rec/(prec+rec) if prec+rec else 0.0,
           "risk_recall": rec, "risk_precision": prec,
           "train_minutes": round(train_min, 1),
           "hyper": {"epochs": args.epochs, "bs": args.bs, "lr": args.lr,
                     "maxlen": 128, "seed": SEED}}
    out_path = f"bert_results_{args.domain}.json"
    json.dump(res, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
