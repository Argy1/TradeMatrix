# Backtest BTC 4h (2026-10-02)

Out-of-sample period: 2024-11-10 to 2026-10-01, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 49.3% | naive 46.5%, always-up 50.7% |
| Coverage (share of non-neutral calls) | 36.4% | 100% |
| Brier score (lower is better) | 0.2521 | base rate 0.2500 |
| Log loss | 0.6974 | coin flip 0.6931 |
| Up calls: n / precision / recall | 964 / 50.4% / 23.2% | |
| Down calls: n / precision / recall | 542 / 47.4% / 12.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 4.86% (1.04% to 9.89%)
- Brier improvement over base rate: -0.00206 (-0.00386 to -0.00045)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -36.7% | -46.7% | -1.24 |
| Naive (hold after an up candle) | -96.9% | -97.2% | -5.50 |
| Buy and hold | 4.9% | -53.4% | 0.28 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 23 | 0.379 | 0.609 |
| 0.4-0.5 | 1901 | 0.464 | 0.500 |
| 0.5-0.6 | 2017 | 0.545 | 0.510 |
| 0.6-0.7 | 199 | 0.607 | 0.528 |

## Most useful features (average gain)

- log_ret_1: 7.03
- ret_1: 5.96
- vol_ratio_20: 5.94
- dist_ema9: 5.85
- ret_6: 5.85
- stoch_k: 5.77
- hour_sin: 5.66
- bb_percent_b: 5.59

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2024-11-10 to 2024-12-10 | 13 | 34.4% | 58.1% | 43.3% | 0.2475 | 0.2481 |
| 2 | 2024-12-10 to 2025-01-09 | 1 | 0.0% | n/a | 37.8% | 0.2500 | 0.2497 |
| 3 | 2025-01-09 to 2025-02-08 | 42 | 27.2% | 49.0% | 47.2% | 0.2488 | 0.2495 |
| 4 | 2025-02-08 to 2025-03-10 | 52 | 10.0% | 44.4% | 45.0% | 0.2485 | 0.2513 |
| 5 | 2025-03-10 to 2025-04-09 | 43 | 67.2% | 49.6% | 53.9% | 0.2523 | 0.2515 |
| 6 | 2025-04-09 to 2025-05-09 | 9 | 100.0% | 43.9% | 45.6% | 0.2600 | 0.2481 |
| 7 | 2025-05-09 to 2025-06-08 | 51 | 100.0% | 46.1% | 41.7% | 0.2596 | 0.2515 |
| 8 | 2025-06-08 to 2025-07-08 | 6 | 0.0% | n/a | 44.4% | 0.2519 | 0.2500 |
| 9 | 2025-07-08 to 2025-08-07 | 1 | 100.0% | 53.9% | 47.8% | 0.2487 | 0.2491 |
| 10 | 2025-08-07 to 2025-09-06 | 215 | 0.0% | n/a | 50.6% | 0.2497 | 0.2508 |
| 11 | 2025-09-06 to 2025-10-06 | 10 | 2.8% | 80.0% | 51.7% | 0.2500 | 0.2504 |
| 12 | 2025-10-06 to 2025-11-05 | 143 | 0.0% | n/a | 46.7% | 0.2519 | 0.2505 |
| 13 | 2025-11-05 to 2025-12-05 | 8 | 0.0% | n/a | 56.1% | 0.2510 | 0.2505 |
| 14 | 2025-12-05 to 2026-01-04 | 5 | 0.0% | n/a | 45.6% | 0.2465 | 0.2490 |
| 15 | 2026-01-04 to 2026-02-03 | 20 | 100.0% | 47.8% | 44.4% | 0.2650 | 0.2502 |
| 16 | 2026-02-03 to 2026-03-05 | 4 | 100.0% | 50.0% | 46.1% | 0.2531 | 0.2500 |
| 17 | 2026-03-05 to 2026-04-04 | 10 | 0.0% | n/a | 51.1% | 0.2510 | 0.2501 |
| 18 | 2026-04-04 to 2026-05-04 | 5 | 0.0% | n/a | 43.9% | 0.2506 | 0.2499 |
| 19 | 2026-05-04 to 2026-06-03 | 35 | 58.3% | 43.8% | 45.6% | 0.2560 | 0.2501 |
| 20 | 2026-06-03 to 2026-07-03 | 21 | 0.0% | n/a | 43.9% | 0.2490 | 0.2502 |
| 21 | 2026-07-03 to 2026-08-02 | 1 | 0.0% | n/a | 42.8% | 0.2530 | 0.2500 |
| 22 | 2026-08-02 to 2026-09-01 | 79 | 36.7% | 50.0% | 47.8% | 0.2531 | 0.2503 |
| 23 | 2026-09-01 to 2026-10-01 | 51 | 100.0% | 53.9% | 47.2% | 0.2514 | 0.2503 |
