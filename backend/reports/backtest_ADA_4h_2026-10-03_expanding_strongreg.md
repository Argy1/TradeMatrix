# Backtest ADA 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.2% | naive 49.4%, always-up 48.3% |
| Coverage (share of non-neutral calls) | 20.0% | 100% |
| Brier score (lower is better) | 0.2497 | base rate 0.2500 |
| Log loss | 0.6925 | coin flip 0.6931 |
| Up calls: n / precision / recall | 444 / 52.3% / 11.6% | |
| Down calls: n / precision / recall | 382 / 56.5% / 10.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.05% (-11.02% to 22.75%)
- Brier improvement over base rate: 0.00027 (-0.00101 to 0.00154)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 55.1% | -41.6% | 0.81 |
| Naive (hold after an up candle) | -90.0% | -94.6% | -1.54 |
| Buy and hold | -41.3% | -89.1% | 0.17 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 2560 | 0.468 | 0.466 |
| 0.5-0.6 | 1509 | 0.532 | 0.506 |
| 0.6-0.7 | 71 | 0.628 | 0.592 |

## Most useful features (average gain)

- btc_ret_6: 14.56
- btc_ret_1: 12.80
- ret_6: 11.50
- log_ret_1: 11.25
- dist_ema9: 10.23
- ret_3: 10.06
- ret_1: 9.67
- lower_wick_pct: 9.42

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 108 | 43.9% | 64.6% | 45.0% | 0.2421 | 0.2503 |
| 37 | 2024-11-22 to 2024-12-22 | 115 | 93.3% | 50.0% | 45.0% | 0.2575 | 0.2499 |
| 38 | 2024-12-22 to 2025-01-21 | 7 | 0.0% | n/a | 50.0% | 0.2497 | 0.2501 |
| 39 | 2025-01-21 to 2025-02-20 | 140 | 0.0% | n/a | 50.0% | 0.2495 | 0.2499 |
| 40 | 2025-02-20 to 2025-03-22 | 81 | 0.0% | n/a | 55.6% | 0.2485 | 0.2500 |
| 41 | 2025-03-22 to 2025-04-21 | 1 | 0.0% | n/a | 54.4% | 0.2495 | 0.2500 |
| 42 | 2025-04-21 to 2025-05-21 | 360 | 4.4% | 62.5% | 49.4% | 0.2487 | 0.2500 |
| 43 | 2025-05-21 to 2025-06-20 | 109 | 16.1% | 58.6% | 49.4% | 0.2496 | 0.2500 |
| 44 | 2025-06-20 to 2025-07-20 | 128 | 0.6% | 100.0% | 47.2% | 0.2498 | 0.2500 |
| 45 | 2025-07-20 to 2025-08-19 | 144 | 0.6% | 0.0% | 50.6% | 0.2491 | 0.2501 |
| 46 | 2025-08-19 to 2025-09-18 | 27 | 100.0% | 48.9% | 50.6% | 0.2556 | 0.2500 |
| 47 | 2025-09-18 to 2025-10-18 | 3 | 0.0% | n/a | 56.1% | 0.2512 | 0.2500 |
| 48 | 2025-10-18 to 2025-11-17 | 2 | 0.0% | n/a | 45.6% | 0.2504 | 0.2500 |
| 49 | 2025-11-17 to 2025-12-17 | 1 | 0.0% | n/a | 53.9% | 0.2496 | 0.2500 |
| 50 | 2025-12-17 to 2026-01-16 | 14 | 0.0% | n/a | 43.9% | 0.2526 | 0.2500 |
| 51 | 2026-01-16 to 2026-02-15 | 140 | 0.0% | n/a | 46.7% | 0.2500 | 0.2499 |
| 52 | 2026-02-15 to 2026-03-17 | 34 | 0.0% | n/a | 48.9% | 0.2489 | 0.2500 |
| 53 | 2026-03-17 to 2026-04-16 | 192 | 0.0% | n/a | 56.1% | 0.2480 | 0.2498 |
| 54 | 2026-04-16 to 2026-05-16 | 70 | 0.0% | n/a | 50.0% | 0.2520 | 0.2500 |
| 55 | 2026-05-16 to 2026-06-15 | 15 | 0.0% | n/a | 46.7% | 0.2464 | 0.2496 |
| 56 | 2026-06-15 to 2026-07-15 | 35 | 100.0% | 57.8% | 46.7% | 0.2441 | 0.2496 |
| 57 | 2026-07-15 to 2026-08-14 | 297 | 100.0% | 54.4% | 49.4% | 0.2500 | 0.2497 |
| 58 | 2026-08-14 to 2026-09-13 | 10 | 0.0% | n/a | 45.0% | 0.2500 | 0.2499 |
