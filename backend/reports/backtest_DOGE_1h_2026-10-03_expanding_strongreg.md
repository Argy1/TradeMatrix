# Backtest DOGE 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.9% | naive 48.4%, always-up 50.2% |
| Coverage (share of non-neutral calls) | 12.6% | 100% |
| Brier score (lower is better) | 0.2493 | base rate 0.2500 |
| Log loss | 0.6917 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1579 / 56.4% / 10.7% | |
| Down calls: n / precision / recall | 509 / 58.5% / 3.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.11% (-5.53% to 14.82%)
- Brier improvement over base rate: 0.00074 (0.00025 to 0.00129)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -71.1% | -83.4% | -1.33 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -10.37 |
| Buy and hold | -23.8% | -85.6% | 0.30 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 16 | 0.394 | 0.500 |
| 0.4-0.5 | 7768 | 0.477 | 0.482 |
| 0.5-0.6 | 8537 | 0.525 | 0.516 |
| 0.6-0.7 | 239 | 0.619 | 0.603 |

## Most useful features (average gain)

- dist_ema9: 69.58
- ret_3: 39.29
- log_ret_1: 26.85
- ret_1: 22.93
- ret_6: 20.22
- dist_ema21: 19.59
- btc_ret_1: 18.74
- btc_ret_6: 18.57

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 61 | 31.2% | 59.1% | 45.3% | 0.2465 | 0.2503 |
| 43 | 2024-11-14 to 2024-12-14 | 32 | 42.8% | 60.4% | 46.7% | 0.2460 | 0.2501 |
| 44 | 2024-12-14 to 2025-01-13 | 160 | 61.3% | 53.3% | 48.9% | 0.2491 | 0.2501 |
| 45 | 2025-01-13 to 2025-02-12 | 175 | 44.0% | 56.2% | 50.7% | 0.2484 | 0.2501 |
| 46 | 2025-02-12 to 2025-03-14 | 305 | 19.7% | 55.6% | 46.9% | 0.2489 | 0.2500 |
| 47 | 2025-03-14 to 2025-04-13 | 62 | 12.4% | 64.0% | 49.3% | 0.2498 | 0.2500 |
| 48 | 2025-04-13 to 2025-05-13 | 169 | 0.0% | n/a | 50.7% | 0.2506 | 0.2501 |
| 49 | 2025-05-13 to 2025-06-12 | 21 | 0.0% | n/a | 50.4% | 0.2500 | 0.2500 |
| 50 | 2025-06-12 to 2025-07-12 | 2 | 0.0% | n/a | 49.7% | 0.2500 | 0.2500 |
| 51 | 2025-07-12 to 2025-08-11 | 5 | 0.0% | n/a | 47.5% | 0.2498 | 0.2500 |
| 52 | 2025-08-11 to 2025-09-10 | 45 | 8.5% | 59.0% | 47.8% | 0.2485 | 0.2500 |
| 53 | 2025-09-10 to 2025-10-10 | 329 | 37.6% | 55.7% | 48.8% | 0.2493 | 0.2500 |
| 54 | 2025-10-10 to 2025-11-09 | 372 | 23.8% | 57.9% | 50.3% | 0.2490 | 0.2500 |
| 55 | 2025-11-09 to 2025-12-09 | 550 | 5.3% | 44.7% | 45.3% | 0.2499 | 0.2500 |
| 56 | 2025-12-09 to 2026-01-08 | 14 | 0.0% | n/a | 49.0% | 0.2498 | 0.2500 |
| 57 | 2026-01-08 to 2026-02-07 | 26 | 0.0% | n/a | 49.4% | 0.2502 | 0.2499 |
| 58 | 2026-02-07 to 2026-03-09 | 33 | 0.0% | n/a | 51.0% | 0.2502 | 0.2500 |
| 59 | 2026-03-09 to 2026-04-08 | 27 | 0.0% | n/a | 49.6% | 0.2512 | 0.2500 |
| 60 | 2026-04-08 to 2026-05-08 | 16 | 0.0% | n/a | 48.6% | 0.2507 | 0.2500 |
| 61 | 2026-05-08 to 2026-06-07 | 1 | 0.0% | n/a | 48.8% | 0.2503 | 0.2500 |
| 62 | 2026-06-07 to 2026-07-07 | 14 | 0.0% | n/a | 47.2% | 0.2491 | 0.2500 |
| 63 | 2026-07-07 to 2026-08-06 | 28 | 0.3% | 0.0% | 47.2% | 0.2482 | 0.2500 |
| 64 | 2026-08-06 to 2026-09-05 | 83 | 3.2% | 78.3% | 43.9% | 0.2480 | 0.2500 |
