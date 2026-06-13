#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 SMP2020-EWECT mirror 分层抽样测试集 + 抽 few-shot 例。本地跑一次。"""
import json, random, os
from collections import defaultdict

SRC = "/tmp/smp2020_mirror/data/raw"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SEED = 2026
N_PER_DOMAIN = 500
LABELS = ["happy", "angry", "sad", "fear", "surprise", "neutral"]

os.makedirs(OUT, exist_ok=True)
rng = random.Random(SEED)

for domain in ["usual", "virus"]:
    test = json.load(open(f"{SRC}/{domain}_test_labeled.txt", encoding="utf-8"))
    by_label = defaultdict(list)
    for x in test:
        if x["label"] in LABELS and x["content"].strip():
            by_label[x["label"]].append(x)
    total = sum(len(v) for v in by_label.values())
    # 按比例分层，至少每类 10 条，余数给最大类
    quota = {}
    for lb in LABELS:
        quota[lb] = max(10, round(len(by_label[lb]) / total * N_PER_DOMAIN))
    while sum(quota.values()) > N_PER_DOMAIN:
        big = max(quota, key=quota.get); quota[big] -= 1
    while sum(quota.values()) < N_PER_DOMAIN:
        big = max(LABELS, key=lambda l: len(by_label[l])); quota[big] += 1
    sample = []
    for lb in LABELS:
        pool = sorted(by_label[lb], key=lambda x: x["id"])
        rng.shuffle(pool)
        sample.extend(pool[:quota[lb]])
    rng.shuffle(sample)
    with open(f"{OUT}/sample_{domain}_500.jsonl", "w", encoding="utf-8") as f:
        for x in sample:
            f.write(json.dumps({"domain": domain, "id": x["id"],
                                "content": x["content"], "label": x["label"]},
                               ensure_ascii=False) + "\n")
    print(domain, "sampled:", len(sample), {lb: quota[lb] for lb in LABELS})

    # few-shot：train 每类抽 1 条，偏好 20~60 字的干净样本
    train = json.load(open(f"{SRC}/{domain}_train.txt", encoding="utf-8"))
    fs = {}
    by_label_tr = defaultdict(list)
    for x in train:
        if x["label"] in LABELS:
            by_label_tr[x["label"]].append(x)
    for lb in LABELS:
        pool = [x for x in by_label_tr[lb] if 15 <= len(x["content"]) <= 60]
        pool = sorted(pool, key=lambda x: x["id"])
        rng.shuffle(pool)
        fs[lb] = pool[0]["content"]
    json.dump(fs, open(f"{OUT}/fewshot_{domain}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(domain, "fewshot ids ok")
