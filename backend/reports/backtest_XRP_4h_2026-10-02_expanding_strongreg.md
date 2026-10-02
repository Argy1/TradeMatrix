# Backtest XRP 4h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.7% | naive 48.4%, always-up 49.5% |
| Coverage (share of non-neutral calls) | 23.2% | 100% |
| Brier score (lower is better) | 0.2504 | base rate 0.2500 |
| Log loss | 0.6940 | coin flip 0.6931 |
| Up calls: n / precision / recall | 651 / 51.9% / 16.5% | |
| Down calls: n / precision / recall | 311 / 54.3% / 8.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.39% (3.23% to 17.79%)
- Brier improvement over base rate: -0.00041 (-0.00108 to 0.00022)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 39.1% | -32.0% | 0.62 |
| Naive (hold after an up candle) | -89.6% | -95.0% | -1.66 |
| Buy and hold | 156.1% | -72.5% | 1.01 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 2375 | 0.475 | 0.494 |
| 0.5-0.6 | 1765 | 0.534 | 0.496 |

## Most useful features (average gain)

- dist_ema9: 16.16
- log_ret_1: 14.46
- btc_ret_1: 13.81
- ret_6: 13.27
- ret_3: 12.95
- ret_1: 12.06
- btc_ret_6: 11.86
- hour_cos: 11.85

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 93 | 0.0% | n/a | 43.3% | 0.2512 | 0.2496 |
| 37 | 2024-11-22 to 2024-12-22 | 64 | 53.9% | 53.6% | 51.1% | 0.2487 | 0.2499 |
| 38 | 2024-12-22 to 2025-01-21 | 20 | 100.0% | 52.2% | 46.1% | 0.2517 | 0.2499 |
| 39 | 2025-01-21 to 2025-02-20 | 14 | 0.0% | n/a | 43.9% | 0.2503 | 0.2501 |
| 40 | 2025-02-20 to 2025-03-22 | 48 | 19.4% | 51.4% | 54.4% | 0.2501 | 0.2500 |
| 41 | 2025-03-22 to 2025-04-21 | 55 | 7.2% | 61.5% | 48.9% | 0.2477 | 0.2502 |
| 42 | 2025-04-21 to 2025-05-21 | 69 | 4.4% | 87.5% | 45.0% | 0.2511 | 0.2499 |
| 43 | 2025-05-21 to 2025-06-20 | 28 | 2.2% | 75.0% | 52.8% | 0.2502 | 0.2502 |
| 44 | 2025-06-20 to 2025-07-20 | 56 | 0.0% | n/a | 49.4% | 0.2486 | 0.2494 |
| 45 | 2025-07-20 to 2025-08-19 | 431 | 82.2% | 51.4% | 51.7% | 0.2538 | 0.2501 |
| 46 | 2025-08-19 to 2025-09-18 | 15 | 100.0% | 48.9% | 46.7% | 0.2538 | 0.2501 |
| 47 | 2025-09-18 to 2025-10-18 | 1 | 0.0% | n/a | 51.1% | 0.2493 | 0.2501 |
| 48 | 2025-10-18 to 2025-11-17 | 136 | 7.2% | 53.8% | 50.0% | 0.2531 | 0.2497 |
| 49 | 2025-11-17 to 2025-12-17 | 179 | 0.0% | n/a | 48.9% | 0.2509 | 0.2502 |
| 50 | 2025-12-17 to 2026-01-16 | 20 | 0.0% | n/a | 46.7% | 0.2510 | 0.2499 |
| 51 | 2026-01-16 to 2026-02-15 | 3 | 0.0% | n/a | 50.0% | 0.2512 | 0.2503 |
| 52 | 2026-02-15 to 2026-03-17 | 133 | 0.0% | n/a | 47.2% | 0.2498 | 0.2501 |
| 53 | 2026-03-17 to 2026-04-16 | 7 | 0.0% | n/a | 48.9% | 0.2494 | 0.2501 |
| 54 | 2026-04-16 to 2026-05-16 | 27 | 0.0% | n/a | 48.9% | 0.2502 | 0.2500 |
| 55 | 2026-05-16 to 2026-06-15 | 42 | 0.0% | n/a | 44.4% | 0.2497 | 0.2504 |
| 56 | 2026-06-15 to 2026-07-15 | 86 | 70.0% | 57.1% | 46.7% | 0.2482 | 0.2501 |
| 57 | 2026-07-15 to 2026-08-14 | 47 | 87.8% | 51.9% | 47.8% | 0.2509 | 0.2501 |
| 58 | 2026-08-14 to 2026-09-13 | 162 | 0.0% | n/a | 48.9% | 0.2490 | 0.2501 |
