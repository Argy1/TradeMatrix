# Backtest NEAR 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-28 to 2026-09-18, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.5% | naive 49.0%, always-up 48.0% |
| Coverage (share of non-neutral calls) | 8.4% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2496 |
| Log loss | 0.6921 | coin flip 0.6931 |
| Up calls: n / precision / recall | 220 / 57.7% / 1.6% | |
| Down calls: n / precision / recall | 1173 / 53.9% / 7.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.19% (0.27% to 16.79%)
- Brier improvement over base rate: 0.00016 (-0.00012 to 0.00048)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 3.2% | -22.2% | 0.19 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -9.45 |
| Buy and hold | -9.6% | -88.4% | 0.46 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 35 | 0.388 | 0.343 |
| 0.4-0.5 | 13665 | 0.472 | 0.477 |
| 0.5-0.6 | 2835 | 0.516 | 0.494 |
| 0.6-0.7 | 25 | 0.623 | 0.600 |

## Most useful features (average gain)

- dist_ema9: 44.02
- ret_3: 22.07
- btc_ret_6: 17.15
- btc_ret_1: 15.56
- dist_ema21: 15.53
- stoch_k: 13.74
- ret_6: 13.41
- log_ret_1: 11.29

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 2024-10-28 to 2024-11-27 | 23 | 2.5% | 77.8% | 48.6% | 0.2485 | 0.2504 |
| 42 | 2024-11-27 to 2024-12-27 | 461 | 8.2% | 59.3% | 47.9% | 0.2492 | 0.2501 |
| 43 | 2024-12-27 to 2025-01-26 | 146 | 35.4% | 54.9% | 46.8% | 0.2502 | 0.2499 |
| 44 | 2025-01-26 to 2025-02-25 | 104 | 1.9% | 42.9% | 48.8% | 0.2491 | 0.2490 |
| 45 | 2025-02-25 to 2025-03-27 | 86 | 0.8% | 83.3% | 49.6% | 0.2500 | 0.2499 |
| 46 | 2025-03-27 to 2025-04-26 | 8 | 0.0% | n/a | 48.3% | 0.2490 | 0.2493 |
| 47 | 2025-04-26 to 2025-05-26 | 22 | 0.0% | n/a | 47.8% | 0.2489 | 0.2496 |
| 48 | 2025-05-26 to 2025-06-25 | 41 | 0.0% | n/a | 50.3% | 0.2497 | 0.2493 |
| 49 | 2025-06-25 to 2025-07-25 | 34 | 0.0% | n/a | 49.9% | 0.2513 | 0.2505 |
| 50 | 2025-07-25 to 2025-08-24 | 73 | 0.0% | n/a | 48.1% | 0.2500 | 0.2498 |
| 51 | 2025-08-24 to 2025-09-23 | 24 | 0.0% | n/a | 50.1% | 0.2497 | 0.2496 |
| 52 | 2025-09-23 to 2025-10-23 | 182 | 0.0% | n/a | 50.4% | 0.2493 | 0.2497 |
| 53 | 2025-10-23 to 2025-11-22 | 25 | 0.0% | n/a | 49.7% | 0.2489 | 0.2491 |
| 54 | 2025-11-22 to 2025-12-22 | 32 | 14.0% | 52.5% | 48.5% | 0.2488 | 0.2493 |
| 55 | 2025-12-22 to 2026-01-21 | 166 | 48.1% | 53.5% | 49.4% | 0.2494 | 0.2495 |
| 56 | 2026-01-21 to 2026-02-20 | 175 | 0.0% | n/a | 46.0% | 0.2483 | 0.2490 |
| 57 | 2026-02-20 to 2026-03-22 | 18 | 2.5% | 38.9% | 52.2% | 0.2491 | 0.2494 |
| 58 | 2026-03-22 to 2026-04-21 | 44 | 0.0% | n/a | 50.4% | 0.2495 | 0.2491 |
| 59 | 2026-04-21 to 2026-05-21 | 35 | 0.0% | n/a | 50.3% | 0.2499 | 0.2497 |
| 60 | 2026-05-21 to 2026-06-20 | 3 | 0.0% | n/a | 46.2% | 0.2504 | 0.2503 |
| 61 | 2026-06-20 to 2026-07-20 | 2 | 0.0% | n/a | 49.2% | 0.2500 | 0.2494 |
| 62 | 2026-07-20 to 2026-08-19 | 555 | 37.5% | 58.9% | 49.7% | 0.2465 | 0.2486 |
| 63 | 2026-08-19 to 2026-09-18 | 529 | 42.5% | 50.7% | 49.2% | 0.2522 | 0.2510 |
