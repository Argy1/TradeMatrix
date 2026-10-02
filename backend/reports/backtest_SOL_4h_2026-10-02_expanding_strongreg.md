# Backtest SOL 4h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 47.9% | naive 49.7%, always-up 49.4% |
| Coverage (share of non-neutral calls) | 25.3% | 100% |
| Brier score (lower is better) | 0.2514 | base rate 0.2500 |
| Log loss | 0.6960 | coin flip 0.6931 |
| Up calls: n / precision / recall | 597 / 44.9% / 13.1% | |
| Down calls: n / precision / recall | 452 / 51.8% / 11.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: -0.23% (-6.39% to 5.77%)
- Brier improvement over base rate: -0.00144 (-0.00315 to -0.00003)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -70.9% | -74.2% | -1.92 |
| Naive (hold after an up candle) | -91.2% | -92.8% | -2.12 |
| Buy and hold | -40.5% | -78.5% | 0.02 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 2445 | 0.474 | 0.486 |
| 0.5-0.6 | 1662 | 0.531 | 0.506 |
| 0.6-0.7 | 33 | 0.637 | 0.485 |

## Most useful features (average gain)

- btc_ret_6: 13.63
- btc_ret_1: 12.54
- log_ret_1: 10.69
- ret_6: 10.65
- ret_1: 9.99
- dist_ema9: 8.98
- ret_3: 8.95
- lower_wick_pct: 8.67

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 203 | 8.9% | 56.2% | 45.0% | 0.2465 | 0.2502 |
| 37 | 2024-11-22 to 2024-12-22 | 91 | 51.7% | 51.6% | 48.9% | 0.2555 | 0.2500 |
| 38 | 2024-12-22 to 2025-01-21 | 161 | 15.0% | 40.7% | 53.9% | 0.2506 | 0.2500 |
| 39 | 2025-01-21 to 2025-02-20 | 154 | 0.0% | n/a | 47.2% | 0.2491 | 0.2500 |
| 40 | 2025-02-20 to 2025-03-22 | 45 | 51.1% | 50.0% | 54.4% | 0.2523 | 0.2500 |
| 41 | 2025-03-22 to 2025-04-21 | 66 | 0.0% | n/a | 50.0% | 0.2502 | 0.2500 |
| 42 | 2025-04-21 to 2025-05-21 | 129 | 0.0% | n/a | 49.4% | 0.2489 | 0.2499 |
| 43 | 2025-05-21 to 2025-06-20 | 1 | 100.0% | 44.4% | 53.9% | 0.2601 | 0.2499 |
| 44 | 2025-06-20 to 2025-07-20 | 103 | 0.0% | n/a | 49.4% | 0.2498 | 0.2500 |
| 45 | 2025-07-20 to 2025-08-19 | 10 | 0.0% | n/a | 51.7% | 0.2502 | 0.2500 |
| 46 | 2025-08-19 to 2025-09-18 | 7 | 0.0% | n/a | 55.0% | 0.2476 | 0.2499 |
| 47 | 2025-09-18 to 2025-10-18 | 246 | 100.0% | 40.6% | 52.8% | 0.2625 | 0.2500 |
| 48 | 2025-10-18 to 2025-11-17 | 1 | 0.0% | n/a | 48.9% | 0.2501 | 0.2500 |
| 49 | 2025-11-17 to 2025-12-17 | 1 | 0.0% | n/a | 51.1% | 0.2508 | 0.2500 |
| 50 | 2025-12-17 to 2026-01-16 | 1 | 0.0% | n/a | 48.9% | 0.2506 | 0.2498 |
| 51 | 2026-01-16 to 2026-02-15 | 38 | 56.1% | 46.5% | 44.4% | 0.2574 | 0.2500 |
| 52 | 2026-02-15 to 2026-03-17 | 103 | 0.0% | n/a | 55.0% | 0.2499 | 0.2500 |
| 53 | 2026-03-17 to 2026-04-16 | 89 | 0.0% | n/a | 52.2% | 0.2494 | 0.2500 |
| 54 | 2026-04-16 to 2026-05-16 | 1 | 0.0% | n/a | 51.1% | 0.2510 | 0.2500 |
| 55 | 2026-05-16 to 2026-06-15 | 8 | 0.0% | n/a | 48.9% | 0.2482 | 0.2500 |
| 56 | 2026-06-15 to 2026-07-15 | 31 | 100.0% | 52.2% | 40.0% | 0.2509 | 0.2500 |
| 57 | 2026-07-15 to 2026-08-14 | 56 | 100.0% | 52.2% | 43.3% | 0.2504 | 0.2500 |
| 58 | 2026-08-14 to 2026-09-13 | 1 | 0.0% | n/a | 47.8% | 0.2507 | 0.2500 |
