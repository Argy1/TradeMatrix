# Backtest AVAX 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-14 to 2026-09-04, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.4% | naive 49.3%, always-up 47.3% |
| Coverage (share of non-neutral calls) | 24.2% | 100% |
| Brier score (lower is better) | 0.2497 | base rate 0.2495 |
| Log loss | 0.6926 | coin flip 0.6931 |
| Up calls: n / precision / recall | 97 / 56.7% / 2.8% | |
| Down calls: n / precision / recall | 903 / 51.9% / 21.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 5.58% (1.19% to 9.97%)
- Brier improvement over base rate: -0.00016 (-0.00111 to 0.00069)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 9.8% | -15.4% | 0.40 |
| Naive (hold after an up candle) | -95.3% | -95.6% | -2.59 |
| Buy and hold | -74.7% | -89.4% | -0.41 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 21 | 0.368 | 0.619 |
| 0.4-0.5 | 3123 | 0.462 | 0.465 |
| 0.5-0.6 | 974 | 0.514 | 0.494 |
| 0.6-0.7 | 21 | 0.615 | 0.571 |
| 0.7-0.8 | 1 | 0.713 | 0.000 |

## Most useful features (average gain)

- log_ret_1: 12.98
- btc_ret_1: 12.77
- btc_ret_6: 12.04
- ret_1: 11.55
- ret_3: 10.28
- dist_ema9: 10.18
- ret_6: 9.17
- atr_pct: 8.22

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | 2024-10-14 to 2024-11-13 | 165 | 20.0% | 58.3% | 47.8% | 0.2493 | 0.2501 |
| 36 | 2024-11-13 to 2024-12-13 | 357 | 28.9% | 57.7% | 43.9% | 0.2487 | 0.2502 |
| 37 | 2024-12-13 to 2025-01-12 | 325 | 0.0% | n/a | 51.7% | 0.2502 | 0.2491 |
| 38 | 2025-01-12 to 2025-02-11 | 122 | 44.4% | 57.5% | 46.7% | 0.2482 | 0.2497 |
| 39 | 2025-02-11 to 2025-03-13 | 66 | 2.2% | 50.0% | 52.2% | 0.2495 | 0.2494 |
| 40 | 2025-03-13 to 2025-04-12 | 442 | 34.4% | 46.8% | 51.1% | 0.2526 | 0.2502 |
| 41 | 2025-04-12 to 2025-05-12 | 14 | 0.0% | n/a | 51.1% | 0.2500 | 0.2500 |
| 42 | 2025-05-12 to 2025-06-11 | 1 | 0.0% | n/a | 50.0% | 0.2500 | 0.2491 |
| 43 | 2025-06-11 to 2025-07-11 | 42 | 0.0% | n/a | 49.4% | 0.2493 | 0.2494 |
| 44 | 2025-07-11 to 2025-08-10 | 345 | 35.6% | 48.4% | 53.9% | 0.2509 | 0.2498 |
| 45 | 2025-08-10 to 2025-09-09 | 505 | 0.0% | n/a | 55.6% | 0.2501 | 0.2500 |
| 46 | 2025-09-09 to 2025-10-09 | 1 | 0.0% | n/a | 55.0% | 0.2478 | 0.2488 |
| 47 | 2025-10-09 to 2025-11-08 | 1 | 0.0% | n/a | 43.3% | 0.2502 | 0.2496 |
| 48 | 2025-11-08 to 2025-12-08 | 2 | 0.0% | n/a | 47.2% | 0.2512 | 0.2499 |
| 49 | 2025-12-08 to 2026-01-07 | 104 | 0.0% | n/a | 51.7% | 0.2493 | 0.2500 |
| 50 | 2026-01-07 to 2026-02-06 | 94 | 0.0% | n/a | 50.0% | 0.2470 | 0.2483 |
| 51 | 2026-02-06 to 2026-03-08 | 147 | 14.4% | 57.7% | 48.9% | 0.2477 | 0.2490 |
| 52 | 2026-03-08 to 2026-04-07 | 187 | 100.0% | 52.8% | 50.0% | 0.2498 | 0.2495 |
| 53 | 2026-04-07 to 2026-05-07 | 133 | 100.0% | 52.2% | 47.8% | 0.2504 | 0.2496 |
| 54 | 2026-05-07 to 2026-06-06 | 40 | 0.0% | n/a | 49.4% | 0.2451 | 0.2482 |
| 55 | 2026-06-06 to 2026-07-06 | 11 | 100.0% | 50.0% | 41.7% | 0.2530 | 0.2502 |
| 56 | 2026-07-06 to 2026-08-05 | 56 | 23.9% | 69.8% | 48.9% | 0.2445 | 0.2485 |
| 57 | 2026-08-05 to 2026-09-04 | 178 | 51.7% | 44.1% | 45.6% | 0.2582 | 0.2506 |
