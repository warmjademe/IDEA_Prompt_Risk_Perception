# 提示策略 × 模型 × 域 分析报告

- 总记录 30000；模型 ['gemma3:12b', 'glm4:9b', 'llama3.1:8b', 'qwen3:14b', 'qwen3:8b']；域 ['usual', 'virus']；B=1000 bootstrap


## 1. 每格 macro-F1 / acc / 解析率 / 时延

| model | domain | strategy | macroF1 [95%CI] | acc | parse% | lat(s) |
|---|---|---|---|---|---|---|
| gemma3:12b | usual | S1_direct | 0.683 [0.632,0.728] | 0.722 | 100.0 | 1.50 |
| gemma3:12b | usual | S2_role | 0.674 [0.622,0.720] | 0.708 | 100.0 | 1.47 |
| gemma3:12b | usual | S3_def | 0.694 [0.645,0.739] | 0.736 | 100.0 | 1.43 |
| gemma3:12b | usual | S4_few | 0.663 [0.612,0.712] | 0.708 | 100.0 | 1.45 |
| gemma3:12b | usual | S5_cot | 0.682 [0.631,0.727] | 0.710 | 100.0 | 8.88 |
| gemma3:12b | usual | S6_json | 0.699 [0.647,0.743] | 0.730 | 100.0 | 2.30 |
| gemma3:12b | virus | S1_direct | 0.519 [0.467,0.565] | 0.540 | 99.2 | 1.40 |
| gemma3:12b | virus | S2_role | 0.509 [0.457,0.554] | 0.544 | 99.6 | 1.38 |
| gemma3:12b | virus | S3_def | 0.580 [0.523,0.633] | 0.660 | 99.8 | 1.35 |
| gemma3:12b | virus | S4_few | 0.626 [0.560,0.685] | 0.684 | 100.0 | 1.40 |
| gemma3:12b | virus | S5_cot | 0.587 [0.516,0.650] | 0.668 | 99.4 | 8.48 |
| gemma3:12b | virus | S6_json | 0.575 [0.521,0.626] | 0.624 | 99.6 | 2.19 |
| glm4:9b | usual | S1_direct | 0.713 [0.663,0.760] | 0.738 | 99.4 | 2.23 |
| glm4:9b | usual | S2_role | 0.697 [0.646,0.739] | 0.722 | 99.6 | 2.32 |
| glm4:9b | usual | S3_def | 0.700 [0.647,0.744] | 0.720 | 99.8 | 2.30 |
| glm4:9b | usual | S4_few | 0.676 [0.617,0.725] | 0.736 | 99.8 | 2.27 |
| glm4:9b | usual | S5_cot | 0.713 [0.657,0.760] | 0.742 | 99.4 | 10.48 |
| glm4:9b | usual | S6_json | 0.712 [0.661,0.756] | 0.732 | 99.8 | 4.55 |
| glm4:9b | virus | S1_direct | 0.645 [0.578,0.701] | 0.678 | 97.6 | 2.38 |
| glm4:9b | virus | S2_role | 0.587 [0.523,0.644] | 0.592 | 98.4 | 2.29 |
| glm4:9b | virus | S3_def | 0.652 [0.596,0.704] | 0.686 | 99.0 | 2.42 |
| glm4:9b | virus | S4_few | 0.613 [0.546,0.672] | 0.720 | 100.0 | 2.28 |
| glm4:9b | virus | S5_cot | 0.587 [0.523,0.648] | 0.656 | 99.4 | 11.30 |
| glm4:9b | virus | S6_json | 0.648 [0.582,0.699] | 0.632 | 99.6 | 4.98 |
| llama3.1:8b | usual | S1_direct | 0.556 [0.506,0.600] | 0.680 | 99.8 | 3.80 |
| llama3.1:8b | usual | S2_role | 0.538 [0.488,0.581] | 0.662 | 98.8 | 3.89 |
| llama3.1:8b | usual | S3_def | 0.642 [0.591,0.690] | 0.702 | 98.4 | 3.74 |
| llama3.1:8b | usual | S4_few | 0.382 [0.346,0.416] | 0.564 | 100.0 | 3.90 |
| llama3.1:8b | usual | S5_cot | 0.616 [0.558,0.670] | 0.676 | 96.0 | 13.94 |
| llama3.1:8b | usual | S6_json | 0.579 [0.528,0.627] | 0.700 | 99.8 | 5.91 |
| llama3.1:8b | virus | S1_direct | 0.463 [0.416,0.506] | 0.614 | 99.4 | 3.71 |
| llama3.1:8b | virus | S2_role | 0.459 [0.396,0.519] | 0.606 | 98.0 | 3.81 |
| llama3.1:8b | virus | S3_def | 0.561 [0.508,0.617] | 0.718 | 99.0 | 3.85 |
| llama3.1:8b | virus | S4_few | 0.170 [0.143,0.199] | 0.536 | 100.0 | 3.80 |
| llama3.1:8b | virus | S5_cot | 0.474 [0.425,0.519] | 0.648 | 94.4 | 13.67 |
| llama3.1:8b | virus | S6_json | 0.457 [0.402,0.504] | 0.608 | 100.0 | 5.75 |
| qwen3:14b | usual | S1_direct | 0.698 [0.648,0.743] | 0.710 | 99.8 | 1.93 |
| qwen3:14b | usual | S2_role | 0.713 [0.665,0.755] | 0.728 | 99.6 | 1.93 |
| qwen3:14b | usual | S3_def | 0.710 [0.663,0.750] | 0.726 | 99.4 | 1.94 |
| qwen3:14b | usual | S4_few | 0.705 [0.656,0.753] | 0.732 | 100.0 | 2.17 |
| qwen3:14b | usual | S5_cot | 0.703 [0.652,0.749] | 0.722 | 100.0 | 12.93 |
| qwen3:14b | usual | S6_json | 0.717 [0.667,0.764] | 0.736 | 99.8 | 4.23 |
| qwen3:14b | virus | S1_direct | 0.538 [0.486,0.584] | 0.524 | 97.6 | 2.18 |
| qwen3:14b | virus | S2_role | 0.540 [0.485,0.589] | 0.546 | 97.0 | 2.35 |
| qwen3:14b | virus | S3_def | 0.624 [0.572,0.675] | 0.684 | 98.4 | 2.46 |
| qwen3:14b | virus | S4_few | 0.632 [0.573,0.683] | 0.692 | 99.4 | 2.45 |
| qwen3:14b | virus | S5_cot | 0.633 [0.568,0.689] | 0.720 | 99.8 | 13.18 |
| qwen3:14b | virus | S6_json | 0.584 [0.520,0.638] | 0.538 | 99.4 | 4.44 |
| qwen3:8b | usual | S1_direct | 0.692 [0.641,0.737] | 0.706 | 99.6 | 0.50 |
| qwen3:8b | usual | S2_role | 0.690 [0.637,0.734] | 0.712 | 99.6 | 0.52 |
| qwen3:8b | usual | S3_def | 0.705 [0.657,0.747] | 0.730 | 99.8 | 0.51 |
| qwen3:8b | usual | S4_few | 0.633 [0.581,0.678] | 0.658 | 100.0 | 0.58 |
| qwen3:8b | usual | S5_cot | 0.688 [0.639,0.732] | 0.698 | 100.0 | 4.80 |
| qwen3:8b | usual | S6_json | 0.670 [0.616,0.719] | 0.700 | 99.8 | 2.19 |
| qwen3:8b | virus | S1_direct | 0.493 [0.427,0.550] | 0.416 | 99.2 | 1.16 |
| qwen3:8b | virus | S2_role | 0.462 [0.388,0.517] | 0.378 | 99.2 | 1.23 |
| qwen3:8b | virus | S3_def | 0.549 [0.484,0.601] | 0.526 | 99.8 | 1.13 |
| qwen3:8b | virus | S4_few | 0.571 [0.507,0.632] | 0.646 | 100.0 | 1.15 |
| qwen3:8b | virus | S5_cot | 0.610 [0.541,0.665] | 0.624 | 100.0 | 6.17 |
| qwen3:8b | virus | S6_json | 0.524 [0.456,0.582] | 0.464 | 99.8 | 2.25 |

## 2. 风险信号检测（angry/sad/fear→1）F1 / recall

| model | domain | strategy | F1 | recall | precision |
|---|---|---|---|---|---|
| gemma3:12b | usual | S1_direct | 0.891 | 0.931 | 0.853 |
| gemma3:12b | usual | S2_role | 0.869 | 0.897 | 0.842 |
| gemma3:12b | usual | S3_def | 0.905 | 0.950 | 0.865 |
| gemma3:12b | usual | S4_few | 0.879 | 0.870 | 0.887 |
| gemma3:12b | usual | S5_cot | 0.876 | 0.847 | 0.906 |
| gemma3:12b | usual | S6_json | 0.900 | 0.927 | 0.874 |
| gemma3:12b | virus | S1_direct | 0.770 | 0.855 | 0.701 |
| gemma3:12b | virus | S2_role | 0.747 | 0.876 | 0.651 |
| gemma3:12b | virus | S3_def | 0.759 | 0.910 | 0.650 |
| gemma3:12b | virus | S4_few | 0.810 | 0.807 | 0.812 |
| gemma3:12b | virus | S5_cot | 0.799 | 0.807 | 0.791 |
| gemma3:12b | virus | S6_json | 0.795 | 0.841 | 0.753 |
| glm4:9b | usual | S1_direct | 0.872 | 0.817 | 0.934 |
| glm4:9b | usual | S2_role | 0.858 | 0.794 | 0.933 |
| glm4:9b | usual | S3_def | 0.850 | 0.779 | 0.936 |
| glm4:9b | usual | S4_few | 0.896 | 0.889 | 0.903 |
| glm4:9b | usual | S5_cot | 0.893 | 0.863 | 0.926 |
| glm4:9b | usual | S6_json | 0.876 | 0.840 | 0.917 |
| glm4:9b | virus | S1_direct | 0.786 | 0.759 | 0.815 |
| glm4:9b | virus | S2_role | 0.815 | 0.807 | 0.824 |
| glm4:9b | virus | S3_def | 0.791 | 0.759 | 0.827 |
| glm4:9b | virus | S4_few | 0.780 | 0.855 | 0.717 |
| glm4:9b | virus | S5_cot | 0.786 | 0.772 | 0.800 |
| glm4:9b | virus | S6_json | 0.817 | 0.814 | 0.819 |
| llama3.1:8b | usual | S1_direct | 0.882 | 0.885 | 0.879 |
| llama3.1:8b | usual | S2_role | 0.885 | 0.943 | 0.834 |
| llama3.1:8b | usual | S3_def | 0.888 | 0.905 | 0.871 |
| llama3.1:8b | usual | S4_few | 0.814 | 0.794 | 0.835 |
| llama3.1:8b | usual | S5_cot | 0.871 | 0.847 | 0.895 |
| llama3.1:8b | usual | S6_json | 0.899 | 0.916 | 0.882 |
| llama3.1:8b | virus | S1_direct | 0.780 | 0.869 | 0.708 |
| llama3.1:8b | virus | S2_role | 0.722 | 0.924 | 0.593 |
| llama3.1:8b | virus | S3_def | 0.776 | 0.862 | 0.706 |
| llama3.1:8b | virus | S4_few | 0.272 | 0.159 | 0.958 |
| llama3.1:8b | virus | S5_cot | 0.748 | 0.786 | 0.713 |
| llama3.1:8b | virus | S6_json | 0.766 | 0.834 | 0.708 |
| qwen3:14b | usual | S1_direct | 0.891 | 0.885 | 0.896 |
| qwen3:14b | usual | S2_role | 0.895 | 0.893 | 0.897 |
| qwen3:14b | usual | S3_def | 0.883 | 0.851 | 0.918 |
| qwen3:14b | usual | S4_few | 0.887 | 0.866 | 0.908 |
| qwen3:14b | usual | S5_cot | 0.903 | 0.920 | 0.886 |
| qwen3:14b | usual | S6_json | 0.904 | 0.916 | 0.892 |
| qwen3:14b | virus | S1_direct | 0.683 | 0.848 | 0.572 |
| qwen3:14b | virus | S2_role | 0.692 | 0.869 | 0.575 |
| qwen3:14b | virus | S3_def | 0.749 | 0.793 | 0.710 |
| qwen3:14b | virus | S4_few | 0.753 | 0.862 | 0.668 |
| qwen3:14b | virus | S5_cot | 0.779 | 0.890 | 0.694 |
| qwen3:14b | virus | S6_json | 0.755 | 0.883 | 0.660 |
| qwen3:8b | usual | S1_direct | 0.897 | 0.863 | 0.934 |
| qwen3:8b | usual | S2_role | 0.921 | 0.908 | 0.933 |
| qwen3:8b | usual | S3_def | 0.907 | 0.908 | 0.905 |
| qwen3:8b | usual | S4_few | 0.837 | 0.752 | 0.943 |
| qwen3:8b | usual | S5_cot | 0.896 | 0.874 | 0.920 |
| qwen3:8b | usual | S6_json | 0.897 | 0.912 | 0.882 |
| qwen3:8b | virus | S1_direct | 0.755 | 0.724 | 0.789 |
| qwen3:8b | virus | S2_role | 0.776 | 0.786 | 0.765 |
| qwen3:8b | virus | S3_def | 0.769 | 0.793 | 0.747 |
| qwen3:8b | virus | S4_few | 0.777 | 0.759 | 0.797 |
| qwen3:8b | virus | S5_cot | 0.796 | 0.807 | 0.785 |
| qwen3:8b | virus | S6_json | 0.799 | 0.848 | 0.755 |

## 3. 策略 vs S1_direct 的 McNemar 配对检验（exact, BH-FDR 校正）

| model | domain | strategy | b(只S错) | c(只基准错) | OR | p | p.adj | sig |
|---|---|---|---|---|---|---|---|---|
| gemma3:12b | usual | S2_role | 17 | 10 | 0.60 | 0.2478 | 0.3951 |  |
| gemma3:12b | usual | S3_def | 17 | 24 | 1.40 | 0.3489 | 0.5131 |  |
| gemma3:12b | usual | S4_few | 37 | 30 | 0.81 | 0.4638 | 0.6621 |  |
| gemma3:12b | usual | S5_cot | 33 | 27 | 0.82 | 0.519 | 0.6828 |  |
| gemma3:12b | usual | S6_json | 14 | 18 | 1.28 | 0.5966 | 0.7649 |  |
| gemma3:12b | virus | S2_role | 25 | 27 | 1.08 | 0.8899 | 0.9375 |  |
| gemma3:12b | virus | S3_def | 14 | 74 | 5.14 | 5.089e-11 | 3.635e-10 | ✓ |
| gemma3:12b | virus | S4_few | 24 | 96 | 3.94 | 2.162e-11 | 1.802e-10 | ✓ |
| gemma3:12b | virus | S5_cot | 25 | 89 | 3.51 | 1.315e-09 | 8.22e-09 | ✓ |
| gemma3:12b | virus | S6_json | 8 | 50 | 5.94 | 1.57e-08 | 7.138e-08 | ✓ |
| glm4:9b | usual | S2_role | 19 | 11 | 0.59 | 0.2005 | 0.3699 |  |
| glm4:9b | usual | S3_def | 25 | 16 | 0.65 | 0.211 | 0.3699 |  |
| glm4:9b | usual | S4_few | 33 | 32 | 0.97 | 1 | 1 |  |
| glm4:9b | usual | S5_cot | 39 | 41 | 1.05 | 0.9111 | 0.9375 |  |
| glm4:9b | usual | S6_json | 24 | 21 | 0.88 | 0.766 | 0.8616 |  |
| glm4:9b | virus | S2_role | 52 | 9 | 0.18 | 1.803e-08 | 7.512e-08 | ✓ |
| glm4:9b | virus | S3_def | 20 | 24 | 1.20 | 0.6516 | 0.8145 |  |
| glm4:9b | virus | S4_few | 35 | 56 | 1.59 | 0.03545 | 0.08862 |  |
| glm4:9b | virus | S5_cot | 59 | 48 | 0.82 | 0.3337 | 0.5056 |  |
| glm4:9b | virus | S6_json | 52 | 29 | 0.56 | 0.014 | 0.03851 | ✓ |
| llama3.1:8b | usual | S2_role | 29 | 20 | 0.69 | 0.2529 | 0.3951 |  |
| llama3.1:8b | usual | S3_def | 27 | 38 | 1.40 | 0.2145 | 0.3699 |  |
| llama3.1:8b | usual | S4_few | 81 | 23 | 0.29 | 9.345e-09 | 4.672e-08 | ✓ |
| llama3.1:8b | usual | S5_cot | 49 | 47 | 0.96 | 0.9188 | 0.9375 |  |
| llama3.1:8b | usual | S6_json | 20 | 30 | 1.49 | 0.2026 | 0.3699 |  |
| llama3.1:8b | virus | S2_role | 36 | 32 | 0.89 | 0.7163 | 0.8527 |  |
| llama3.1:8b | virus | S3_def | 26 | 78 | 2.96 | 3.278e-07 | 1.261e-06 | ✓ |
| llama3.1:8b | virus | S4_few | 121 | 82 | 0.68 | 0.007499 | 0.02205 | ✓ |
| llama3.1:8b | virus | S5_cot | 52 | 69 | 1.32 | 0.1455 | 0.3031 |  |
| llama3.1:8b | virus | S6_json | 31 | 28 | 0.90 | 0.7948 | 0.864 |  |
| qwen3:14b | usual | S2_role | 7 | 16 | 2.20 | 0.09314 | 0.2025 |  |
| qwen3:14b | usual | S3_def | 13 | 21 | 1.59 | 0.2295 | 0.3825 |  |
| qwen3:14b | usual | S4_few | 25 | 36 | 1.43 | 0.2 | 0.3699 |  |
| qwen3:14b | usual | S5_cot | 25 | 31 | 1.24 | 0.5044 | 0.6816 |  |
| qwen3:14b | usual | S6_json | 6 | 19 | 3.00 | 0.01463 | 0.03851 | ✓ |
| qwen3:14b | virus | S2_role | 11 | 22 | 1.96 | 0.08014 | 0.1821 |  |
| qwen3:14b | virus | S3_def | 12 | 92 | 7.40 | 1.953e-16 | 2.441e-15 | ✓ |
| qwen3:14b | virus | S4_few | 25 | 109 | 4.29 | 1.053e-13 | 1.053e-12 | ✓ |
| qwen3:14b | virus | S5_cot | 22 | 120 | 5.36 | 1.568e-17 | 3.919e-16 | ✓ |
| qwen3:14b | virus | S6_json | 32 | 39 | 1.22 | 0.4767 | 0.6621 |  |
| qwen3:8b | usual | S2_role | 23 | 26 | 1.13 | 0.7754 | 0.8616 |  |
| qwen3:8b | usual | S3_def | 13 | 25 | 1.89 | 0.07295 | 0.1737 |  |
| qwen3:8b | usual | S4_few | 41 | 17 | 0.42 | 0.002233 | 0.007973 | ✓ |
| qwen3:8b | usual | S5_cot | 34 | 30 | 0.88 | 0.708 | 0.8527 |  |
| qwen3:8b | usual | S6_json | 21 | 18 | 0.86 | 0.7493 | 0.8616 |  |
| qwen3:8b | virus | S2_role | 31 | 12 | 0.40 | 0.005402 | 0.01801 | ✓ |
| qwen3:8b | virus | S3_def | 18 | 73 | 3.97 | 5.009e-09 | 2.783e-08 | ✓ |
| qwen3:8b | virus | S4_few | 35 | 150 | 4.24 | 3.696e-18 | 1.848e-16 | ✓ |
| qwen3:8b | virus | S5_cot | 30 | 134 | 4.41 | 6.816e-17 | 1.136e-15 | ✓ |
| qwen3:8b | virus | S6_json | 25 | 49 | 1.94 | 0.007084 | 0.02205 | ✓ |

## 4. 跨模型策略排序一致性（Friedman + Kendall's W，基于 macro-F1）

- blocks(model×domain)=10，χ²=12.69，p=0.02651，Kendall's W=0.254
- 平均名次（越小越好）: S1_direct:3.80, S2_role:4.70, S3_def:2.20, S4_few:4.30, S5_cot:2.80, S6_json:3.20

## 5. 平凡基线（按域，500 条抽样上）

- usual: majority(=angry) macro-F1=0.077；random macro-F1≈0.155
- virus: majority(=happy) macro-F1=0.113；random macro-F1≈0.140