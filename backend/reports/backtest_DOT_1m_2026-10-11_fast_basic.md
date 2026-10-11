# Backtest DOT 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 75389 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 67.7% | naive 43.1%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 46.6% | |
| Coverage (share of non-neutral calls) | 74.1% | 100% |
| Brier score (lower is better) | 0.2213 | base rate 0.2500 |
| Log loss | 0.6325 | coin flip 0.6931 |
| Up calls: n / precision / recall | 26983 / 67.7% / 48.5% | |
| Down calls: n / precision / recall | 26628 / 67.7% / 47.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 25.42% (19.83% to 30.93%)
- Accuracy minus the best simple rule: 17.29% (13.46% to 20.97%)
- Brier improvement over base rate: 0.03447 (0.01993 to 0.04914)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -370.80 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -470.10 |
| Buy and hold | 31.0% | -27.0% | 1.59 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.0-0.1 | 1015 | 0.076 | 0.119 |
| 0.1-0.2 | 4085 | 0.153 | 0.189 |
| 0.2-0.3 | 6125 | 0.252 | 0.272 |
| 0.3-0.4 | 8438 | 0.354 | 0.365 |
| 0.4-0.5 | 18298 | 0.459 | 0.452 |
| 0.5-0.6 | 17513 | 0.543 | 0.540 |
| 0.6-0.7 | 8970 | 0.647 | 0.639 |
| 0.7-0.8 | 6107 | 0.746 | 0.734 |
| 0.8-0.9 | 4046 | 0.846 | 0.824 |
| 0.9-1.0 | 792 | 0.919 | 0.879 |

## Most useful features (average gain)

- log_ret_1: 173.21
- stoch_k: 154.35
- dist_ema9: 141.81
- ret_1: 134.66
- btc_ret_1: 79.11
- upper_wick_pct: 70.20
- lower_wick_pct: 52.06
- btc_ret_6: 49.71

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 800 | 85.0% | 71.6% | 39.9% | 0.2038 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 799 | 86.1% | 71.1% | 39.1% | 0.2023 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 792 | 85.2% | 73.3% | 38.4% | 0.1944 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 800 | 87.3% | 75.5% | 38.2% | 0.1822 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 798 | 90.0% | 71.6% | 39.1% | 0.2005 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 800 | 87.0% | 76.0% | 38.6% | 0.1808 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 791 | 89.6% | 78.0% | 38.5% | 0.1687 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 800 | 87.9% | 63.0% | 45.1% | 0.2431 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 799 | 76.7% | 68.7% | 43.1% | 0.2192 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 170 | 80.7% | 60.7% | 43.8% | 0.2411 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 800 | 65.9% | 64.5% | 44.9% | 0.2346 | 0.2500 |
| 39 | 2026-09-16 to 2026-09-23 | 94 | 66.0% | 54.5% | 47.2% | 0.2534 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 359 | 30.6% | 58.2% | 49.6% | 0.2471 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 37 | 19.3% | 61.8% | 47.3% | 0.2463 | 0.2500 |
