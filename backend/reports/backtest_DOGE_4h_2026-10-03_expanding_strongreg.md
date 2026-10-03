# Backtest DOGE 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 50.6% | naive 49.5%, always-up 49.4% |
| Coverage (share of non-neutral calls) | 19.3% | 100% |
| Brier score (lower is better) | 0.2508 | base rate 0.2500 |
| Log loss | 0.6947 | coin flip 0.6931 |
| Up calls: n / precision / recall | 506 / 50.8% / 12.6% | |
| Down calls: n / precision / recall | 294 / 50.3% / 7.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: -5.49% (-18.06% to 3.73%)
- Brier improvement over base rate: -0.00077 (-0.00192 to 0.00054)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -36.1% | -67.1% | -0.31 |
| Naive (hold after an up candle) | -87.3% | -95.4% | -1.40 |
| Buy and hold | -40.2% | -85.4% | 0.13 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 1989 | 0.470 | 0.488 |
| 0.5-0.6 | 2067 | 0.529 | 0.495 |
| 0.6-0.7 | 84 | 0.627 | 0.619 |

## Most useful features (average gain)

- log_ret_1: 16.25
- btc_ret_1: 14.98
- ret_6: 14.59
- btc_ret_6: 13.74
- ret_1: 13.46
- dist_ema9: 12.45
- hour_sin: 9.90
- rsi14: 9.67

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 139 | 49.4% | 62.9% | 45.6% | 0.2415 | 0.2503 |
| 37 | 2024-11-22 to 2024-12-22 | 140 | 81.1% | 49.3% | 47.2% | 0.2556 | 0.2500 |
| 38 | 2024-12-22 to 2025-01-21 | 37 | 26.1% | 53.2% | 51.1% | 0.2499 | 0.2501 |
| 39 | 2025-01-21 to 2025-02-20 | 147 | 0.0% | n/a | 48.9% | 0.2481 | 0.2500 |
| 40 | 2025-02-20 to 2025-03-22 | 39 | 37.2% | 49.3% | 51.1% | 0.2520 | 0.2500 |
| 41 | 2025-03-22 to 2025-04-21 | 54 | 13.9% | 40.0% | 52.2% | 0.2516 | 0.2500 |
| 42 | 2025-04-21 to 2025-05-21 | 791 | 1.1% | 0.0% | 51.7% | 0.2519 | 0.2499 |
| 43 | 2025-05-21 to 2025-06-20 | 1 | 0.0% | n/a | 48.3% | 0.2529 | 0.2501 |
| 44 | 2025-06-20 to 2025-07-20 | 4 | 0.0% | n/a | 48.3% | 0.2541 | 0.2499 |
| 45 | 2025-07-20 to 2025-08-19 | 1 | 0.0% | n/a | 51.7% | 0.2496 | 0.2500 |
| 46 | 2025-08-19 to 2025-09-18 | 1 | 0.0% | n/a | 51.7% | 0.2490 | 0.2499 |
| 47 | 2025-09-18 to 2025-10-18 | 1 | 100.0% | 47.8% | 53.9% | 0.2556 | 0.2500 |
| 48 | 2025-10-18 to 2025-11-17 | 1 | 0.0% | n/a | 45.6% | 0.2497 | 0.2500 |
| 49 | 2025-11-17 to 2025-12-17 | 3 | 0.0% | n/a | 57.8% | 0.2522 | 0.2501 |
| 50 | 2025-12-17 to 2026-01-16 | 1 | 0.0% | n/a | 50.0% | 0.2510 | 0.2500 |
| 51 | 2026-01-16 to 2026-02-15 | 56 | 10.6% | 42.1% | 50.0% | 0.2526 | 0.2501 |
| 52 | 2026-02-15 to 2026-03-17 | 352 | 0.0% | n/a | 52.2% | 0.2496 | 0.2501 |
| 53 | 2026-03-17 to 2026-04-16 | 64 | 0.0% | n/a | 46.1% | 0.2500 | 0.2500 |
| 54 | 2026-04-16 to 2026-05-16 | 1 | 0.0% | n/a | 52.2% | 0.2511 | 0.2499 |
| 55 | 2026-05-16 to 2026-06-15 | 50 | 0.0% | n/a | 44.4% | 0.2519 | 0.2501 |
| 56 | 2026-06-15 to 2026-07-15 | 58 | 0.0% | n/a | 44.4% | 0.2456 | 0.2500 |
| 57 | 2026-07-15 to 2026-08-14 | 3 | 100.0% | 52.8% | 44.4% | 0.2517 | 0.2500 |
| 58 | 2026-08-14 to 2026-09-13 | 29 | 25.0% | 44.4% | 49.4% | 0.2510 | 0.2500 |
