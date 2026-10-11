# Backtest ADA 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 104137 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 59.7% | naive 47.0%, reverse 53.0%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 26.2% | |
| Coverage (share of non-neutral calls) | 44.8% | 100% |
| Brier score (lower is better) | 0.2455 | base rate 0.2500 |
| Log loss | 0.6842 | coin flip 0.6931 |
| Up calls: n / precision / recall | 21893 / 59.9% / 25.3% | |
| Down calls: n / precision / recall | 23004 / 59.4% / 26.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 13.49% (10.07% to 16.95%)
- Accuracy minus the best simple rule: 6.97% (5.10% to 9.02%)
- Brier improvement over base rate: 0.00521 (0.00143 to 0.00929)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -331.49 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -501.15 |
| Buy and hold | 65.4% | -26.3% | 2.62 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.1-0.2 | 5 | 0.188 | 0.400 |
| 0.2-0.3 | 1435 | 0.274 | 0.379 |
| 0.3-0.4 | 9694 | 0.361 | 0.389 |
| 0.4-0.5 | 42334 | 0.464 | 0.459 |
| 0.5-0.6 | 39273 | 0.535 | 0.536 |
| 0.6-0.7 | 9101 | 0.641 | 0.617 |
| 0.7-0.8 | 2228 | 0.733 | 0.685 |
| 0.8-0.9 | 67 | 0.816 | 0.612 |

## Most useful features (average gain)

- log_ret_1: 87.29
- lower_wick_pct: 71.11
- upper_wick_pct: 67.13
- ret_1: 58.84
- stoch_k: 53.09
- dist_ema9: 42.22
- btc_ret_1: 33.38
- atr_pct: 22.74

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 632 | 74.2% | 57.2% | 46.4% | 0.2500 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 672 | 51.9% | 66.8% | 43.0% | 0.2366 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 103 | 76.7% | 62.0% | 44.8% | 0.2367 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 796 | 73.3% | 65.8% | 43.3% | 0.2294 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 800 | 76.8% | 56.5% | 46.4% | 0.2510 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 799 | 52.2% | 62.4% | 44.8% | 0.2421 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 81 | 62.7% | 65.4% | 43.4% | 0.2339 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 452 | 67.0% | 51.9% | 49.1% | 0.2563 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 779 | 4.5% | 67.8% | 49.1% | 0.2468 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 4 | 0.9% | 58.2% | 48.7% | 0.2489 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 793 | 35.1% | 60.0% | 47.4% | 0.2463 | 0.2500 |
| 39 | 2026-09-16 to 2026-09-23 | 77 | 42.3% | 52.9% | 49.1% | 0.2508 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 286 | 6.7% | 58.7% | 50.1% | 0.2490 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 35 | 3.0% | 57.6% | 48.9% | 0.2492 | 0.2500 |
