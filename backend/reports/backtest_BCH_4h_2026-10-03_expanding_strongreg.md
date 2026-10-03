# Backtest BCH 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.1% | naive 47.9%, always-up 48.5% |
| Coverage (share of non-neutral calls) | 13.7% | 100% |
| Brier score (lower is better) | 0.2500 | base rate 0.2499 |
| Log loss | 0.6932 | coin flip 0.6931 |
| Up calls: n / precision / recall | 132 / 49.2% / 3.2% | |
| Down calls: n / precision / recall | 435 / 54.3% / 11.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.71% (-1.35% to 18.60%)
- Brier improvement over base rate: -0.00008 (-0.00089 to 0.00069)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -20.3% | -24.6% | -0.65 |
| Naive (hold after an up candle) | -95.4% | -96.2% | -2.75 |
| Buy and hold | -35.6% | -72.0% | 0.08 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 71 | 0.382 | 0.380 |
| 0.4-0.5 | 2302 | 0.472 | 0.479 |
| 0.5-0.6 | 1750 | 0.520 | 0.498 |
| 0.6-0.7 | 17 | 0.617 | 0.412 |

## Most useful features (average gain)

- dist_ema21: 16.81
- dist_ema9: 14.72
- rsi14: 13.72
- stoch_k: 13.07
- ret_6: 12.86
- ret_1: 12.13
- log_ret_1: 11.93
- btc_ret_6: 10.28

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 6 | 0.0% | n/a | 45.6% | 0.2503 | 0.2502 |
| 37 | 2024-11-22 to 2024-12-22 | 76 | 0.0% | n/a | 48.9% | 0.2505 | 0.2499 |
| 38 | 2024-12-22 to 2025-01-21 | 475 | 0.0% | n/a | 55.0% | 0.2505 | 0.2502 |
| 39 | 2025-01-21 to 2025-02-20 | 25 | 0.0% | n/a | 46.1% | 0.2498 | 0.2498 |
| 40 | 2025-02-20 to 2025-03-22 | 42 | 0.0% | n/a | 50.0% | 0.2498 | 0.2502 |
| 41 | 2025-03-22 to 2025-04-21 | 24 | 6.7% | 41.7% | 52.8% | 0.2510 | 0.2501 |
| 42 | 2025-04-21 to 2025-05-21 | 232 | 6.1% | 63.6% | 45.6% | 0.2503 | 0.2500 |
| 43 | 2025-05-21 to 2025-06-20 | 24 | 0.0% | n/a | 48.3% | 0.2500 | 0.2499 |
| 44 | 2025-06-20 to 2025-07-20 | 3 | 0.0% | n/a | 42.8% | 0.2498 | 0.2501 |
| 45 | 2025-07-20 to 2025-08-19 | 150 | 0.0% | n/a | 49.4% | 0.2510 | 0.2500 |
| 46 | 2025-08-19 to 2025-09-18 | 13 | 0.0% | n/a | 45.6% | 0.2511 | 0.2500 |
| 47 | 2025-09-18 to 2025-10-18 | 64 | 23.3% | 50.0% | 50.0% | 0.2505 | 0.2498 |
| 48 | 2025-10-18 to 2025-11-17 | 94 | 46.1% | 42.2% | 52.8% | 0.2564 | 0.2501 |
| 49 | 2025-11-17 to 2025-12-17 | 204 | 0.6% | 100.0% | 52.2% | 0.2491 | 0.2499 |
| 50 | 2025-12-17 to 2026-01-16 | 3 | 0.0% | n/a | 41.7% | 0.2503 | 0.2500 |
| 51 | 2026-01-16 to 2026-02-15 | 202 | 46.7% | 50.0% | 53.3% | 0.2513 | 0.2496 |
| 52 | 2026-02-15 to 2026-03-17 | 179 | 57.8% | 57.7% | 45.6% | 0.2454 | 0.2499 |
| 53 | 2026-03-17 to 2026-04-16 | 189 | 47.2% | 55.3% | 48.3% | 0.2470 | 0.2498 |
| 54 | 2026-04-16 to 2026-05-16 | 184 | 41.7% | 58.7% | 48.9% | 0.2487 | 0.2498 |
| 55 | 2026-05-16 to 2026-06-15 | 87 | 38.9% | 55.7% | 48.3% | 0.2494 | 0.2498 |
| 56 | 2026-06-15 to 2026-07-15 | 49 | 0.0% | n/a | 42.2% | 0.2521 | 0.2501 |
| 57 | 2026-07-15 to 2026-08-14 | 28 | 0.0% | n/a | 45.6% | 0.2475 | 0.2494 |
| 58 | 2026-08-14 to 2026-09-13 | 30 | 0.0% | n/a | 43.9% | 0.2482 | 0.2496 |
