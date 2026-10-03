# Backtest LTC 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 50.4% | naive 48.8%, always-up 50.9% |
| Coverage (share of non-neutral calls) | 6.9% | 100% |
| Brier score (lower is better) | 0.2508 | base rate 0.2499 |
| Log loss | 0.6948 | coin flip 0.6931 |
| Up calls: n / precision / recall | 193 / 50.3% / 4.6% | |
| Down calls: n / precision / recall | 91 / 50.5% / 2.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: -1.39% (-17.64% to 10.42%)
- Brier improvement over base rate: -0.00091 (-0.00168 to -0.00024)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -10.6% | -20.0% | -0.45 |
| Naive (hold after an up candle) | -90.9% | -94.2% | -2.17 |
| Buy and hold | -21.2% | -72.1% | 0.23 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 1484 | 0.479 | 0.520 |
| 0.5-0.6 | 2656 | 0.522 | 0.503 |

## Most useful features (average gain)

- dist_ema9: 14.65
- btc_ret_1: 14.29
- dist_ema21: 12.70
- log_ret_1: 12.10
- ret_6: 11.97
- stoch_k: 11.07
- ret_1: 10.75
- btc_ret_6: 10.42

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 25 | 0.0% | n/a | 49.4% | 0.2506 | 0.2493 |
| 37 | 2024-11-22 to 2024-12-22 | 291 | 0.0% | n/a | 50.0% | 0.2499 | 0.2498 |
| 38 | 2024-12-22 to 2025-01-21 | 1 | 0.0% | n/a | 50.0% | 0.2498 | 0.2498 |
| 39 | 2025-01-21 to 2025-02-20 | 5 | 0.0% | n/a | 52.2% | 0.2501 | 0.2505 |
| 40 | 2025-02-20 to 2025-03-22 | 53 | 0.0% | n/a | 51.1% | 0.2505 | 0.2501 |
| 41 | 2025-03-22 to 2025-04-21 | 17 | 0.0% | n/a | 55.6% | 0.2507 | 0.2504 |
| 42 | 2025-04-21 to 2025-05-21 | 24 | 0.0% | n/a | 45.0% | 0.2504 | 0.2494 |
| 43 | 2025-05-21 to 2025-06-20 | 9 | 0.0% | n/a | 45.0% | 0.2512 | 0.2507 |
| 44 | 2025-06-20 to 2025-07-20 | 30 | 0.0% | n/a | 49.4% | 0.2514 | 0.2490 |
| 45 | 2025-07-20 to 2025-08-19 | 717 | 0.0% | n/a | 50.6% | 0.2489 | 0.2495 |
| 46 | 2025-08-19 to 2025-09-18 | 16 | 100.0% | 50.6% | 46.1% | 0.2529 | 0.2500 |
| 47 | 2025-09-18 to 2025-10-18 | 2 | 0.0% | n/a | 55.0% | 0.2501 | 0.2503 |
| 48 | 2025-10-18 to 2025-11-17 | 1 | 0.0% | n/a | 46.7% | 0.2496 | 0.2496 |
| 49 | 2025-11-17 to 2025-12-17 | 323 | 2.2% | 25.0% | 50.0% | 0.2511 | 0.2506 |
| 50 | 2025-12-17 to 2026-01-16 | 9 | 0.0% | n/a | 43.3% | 0.2521 | 0.2496 |
| 51 | 2026-01-16 to 2026-02-15 | 2 | 0.0% | n/a | 45.6% | 0.2533 | 0.2510 |
| 52 | 2026-02-15 to 2026-03-17 | 15 | 0.0% | n/a | 51.7% | 0.2523 | 0.2497 |
| 53 | 2026-03-17 to 2026-04-16 | 459 | 0.0% | n/a | 50.0% | 0.2501 | 0.2501 |
| 54 | 2026-04-16 to 2026-05-16 | 14 | 0.0% | n/a | 50.0% | 0.2495 | 0.2497 |
| 55 | 2026-05-16 to 2026-06-15 | 118 | 5.0% | 55.6% | 42.2% | 0.2528 | 0.2513 |
| 56 | 2026-06-15 to 2026-07-15 | 107 | 50.6% | 50.5% | 48.9% | 0.2559 | 0.2491 |
| 57 | 2026-07-15 to 2026-08-14 | 233 | 0.0% | n/a | 48.3% | 0.2494 | 0.2497 |
| 58 | 2026-08-14 to 2026-09-13 | 24 | 0.0% | n/a | 46.1% | 0.2466 | 0.2491 |
