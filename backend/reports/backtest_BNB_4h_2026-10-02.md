# Backtest BNB 4h (2026-10-02)

Out-of-sample period: 2024-11-10 to 2026-10-01, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 49.9% | naive 48.7%, always-up 51.0% |
| Coverage (share of non-neutral calls) | 30.7% | 100% |
| Brier score (lower is better) | 0.2525 | base rate 0.2501 |
| Log loss | 0.6983 | coin flip 0.6931 |
| Up calls: n / precision / recall | 549 / 49.9% / 13.0% | |
| Down calls: n / precision / recall | 721 / 49.9% / 17.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: -0.70% (-3.55% to 1.90%)
- Brier improvement over base rate: -0.00246 (-0.00464 to -0.00064)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -44.3% | -48.4% | -1.17 |
| Naive (hold after an up candle) | -94.7% | -94.9% | -4.04 |
| Buy and hold | 19.9% | -59.6% | 0.44 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 12 | 0.274 | 0.333 |
| 0.3-0.4 | 241 | 0.369 | 0.510 |
| 0.4-0.5 | 1141 | 0.463 | 0.518 |
| 0.5-0.6 | 2678 | 0.526 | 0.507 |
| 0.6-0.7 | 64 | 0.637 | 0.516 |
| 0.7-0.8 | 4 | 0.733 | 0.750 |

## Most useful features (average gain)

- ret_6: 5.96
- dist_ema50: 5.89
- dist_ema9: 5.84
- hour_sin: 5.83
- dist_ema21: 5.82
- atr_pct: 5.81
- bb_bandwidth: 5.76
- log_ret_1: 5.67

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2024-11-10 to 2024-12-10 | 5 | 0.0% | n/a | 43.3% | 0.2504 | 0.2510 |
| 2 | 2024-12-10 to 2025-01-09 | 100 | 0.0% | n/a | 42.2% | 0.2494 | 0.2491 |
| 3 | 2025-01-09 to 2025-02-08 | 104 | 0.0% | n/a | 53.3% | 0.2525 | 0.2518 |
| 4 | 2025-02-08 to 2025-03-10 | 206 | 100.0% | 50.0% | 54.4% | 0.2626 | 0.2502 |
| 5 | 2025-03-10 to 2025-04-09 | 19 | 8.3% | 40.0% | 49.4% | 0.2482 | 0.2505 |
| 6 | 2025-04-09 to 2025-05-09 | 46 | 87.8% | 47.5% | 50.6% | 0.2676 | 0.2495 |
| 7 | 2025-05-09 to 2025-06-08 | 179 | 21.7% | 48.7% | 52.2% | 0.2503 | 0.2501 |
| 8 | 2025-06-08 to 2025-07-08 | 21 | 0.0% | n/a | 48.9% | 0.2500 | 0.2501 |
| 9 | 2025-07-08 to 2025-08-07 | 30 | 16.7% | 50.0% | 51.1% | 0.2503 | 0.2497 |
| 10 | 2025-08-07 to 2025-09-06 | 2 | 0.0% | n/a | 52.2% | 0.2506 | 0.2498 |
| 11 | 2025-09-06 to 2025-10-06 | 85 | 0.0% | n/a | 56.7% | 0.2552 | 0.2482 |
| 12 | 2025-10-06 to 2025-11-05 | 1 | 100.0% | 48.9% | 43.9% | 0.2543 | 0.2503 |
| 13 | 2025-11-05 to 2025-12-05 | 5 | 0.0% | n/a | 52.2% | 0.2502 | 0.2499 |
| 14 | 2025-12-05 to 2026-01-04 | 114 | 0.0% | n/a | 46.1% | 0.2500 | 0.2496 |
| 15 | 2026-01-04 to 2026-02-03 | 274 | 73.3% | 46.2% | 43.9% | 0.2630 | 0.2510 |
| 16 | 2026-02-03 to 2026-03-05 | 173 | 100.0% | 52.2% | 52.8% | 0.2506 | 0.2508 |
| 17 | 2026-03-05 to 2026-04-04 | 9 | 0.0% | n/a | 46.1% | 0.2503 | 0.2514 |
| 18 | 2026-04-04 to 2026-05-04 | 7 | 97.8% | 50.6% | 46.7% | 0.2539 | 0.2501 |
| 19 | 2026-05-04 to 2026-06-03 | 2 | 100.0% | 53.9% | 50.0% | 0.2488 | 0.2492 |
| 20 | 2026-06-03 to 2026-07-03 | 5 | 0.0% | n/a | 47.2% | 0.2522 | 0.2505 |
| 21 | 2026-07-03 to 2026-08-02 | 2 | 0.0% | n/a | 46.1% | 0.2501 | 0.2502 |
| 22 | 2026-08-02 to 2026-09-01 | 22 | 0.0% | n/a | 48.9% | 0.2485 | 0.2490 |
| 23 | 2026-09-01 to 2026-10-01 | 34 | 0.0% | n/a | 42.8% | 0.2489 | 0.2495 |
