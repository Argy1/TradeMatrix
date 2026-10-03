# Backtest DOT 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.0% | naive 49.1%, always-up 47.8% |
| Coverage (share of non-neutral calls) | 15.7% | 100% |
| Brier score (lower is better) | 0.2501 | base rate 0.2498 |
| Log loss | 0.6934 | coin flip 0.6931 |
| Up calls: n / precision / recall | 212 / 54.2% / 5.8% | |
| Down calls: n / precision / recall | 438 / 56.8% / 11.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.15% (1.47% to 13.70%)
- Brier improvement over base rate: -0.00026 (-0.00175 to 0.00127)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 11.2% | -28.1% | 0.34 |
| Naive (hold after an up candle) | -96.3% | -97.4% | -2.64 |
| Buy and hold | -75.8% | -93.4% | -0.43 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 88 | 0.378 | 0.420 |
| 0.4-0.5 | 2565 | 0.465 | 0.480 |
| 0.5-0.6 | 1467 | 0.522 | 0.476 |
| 0.6-0.7 | 20 | 0.616 | 0.550 |

## Most useful features (average gain)

- btc_ret_1: 13.14
- log_ret_1: 11.90
- btc_ret_6: 10.61
- ret_6: 9.61
- dist_ema21: 9.11
- lower_wick_pct: 8.93
- ret_1: 8.75
- rsi14: 8.73

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 274 | 33.3% | 63.3% | 43.9% | 0.2458 | 0.2503 |
| 37 | 2024-11-22 to 2024-12-22 | 383 | 50.0% | 50.0% | 47.2% | 0.2548 | 0.2497 |
| 38 | 2024-12-22 to 2025-01-21 | 81 | 9.4% | 52.9% | 53.9% | 0.2492 | 0.2499 |
| 39 | 2025-01-21 to 2025-02-20 | 29 | 15.0% | 66.7% | 49.4% | 0.2508 | 0.2500 |
| 40 | 2025-02-20 to 2025-03-22 | 244 | 19.4% | 57.1% | 52.2% | 0.2496 | 0.2500 |
| 41 | 2025-03-22 to 2025-04-21 | 211 | 24.4% | 50.0% | 47.8% | 0.2528 | 0.2498 |
| 42 | 2025-04-21 to 2025-05-21 | 679 | 27.8% | 48.0% | 52.8% | 0.2536 | 0.2501 |
| 43 | 2025-05-21 to 2025-06-20 | 19 | 0.0% | n/a | 43.9% | 0.2505 | 0.2498 |
| 44 | 2025-06-20 to 2025-07-20 | 45 | 0.0% | n/a | 49.4% | 0.2517 | 0.2501 |
| 45 | 2025-07-20 to 2025-08-19 | 18 | 0.0% | n/a | 50.6% | 0.2500 | 0.2500 |
| 46 | 2025-08-19 to 2025-09-18 | 1 | 0.0% | n/a | 53.9% | 0.2502 | 0.2501 |
| 47 | 2025-09-18 to 2025-10-18 | 1 | 0.0% | n/a | 50.6% | 0.2512 | 0.2497 |
| 48 | 2025-10-18 to 2025-11-17 | 6 | 0.0% | n/a | 42.2% | 0.2507 | 0.2502 |
| 49 | 2025-11-17 to 2025-12-17 | 5 | 0.0% | n/a | 58.3% | 0.2521 | 0.2496 |
| 50 | 2025-12-17 to 2026-01-16 | 9 | 0.0% | n/a | 46.1% | 0.2544 | 0.2501 |
| 51 | 2026-01-16 to 2026-02-15 | 2 | 0.0% | n/a | 51.1% | 0.2495 | 0.2496 |
| 52 | 2026-02-15 to 2026-03-17 | 2 | 0.0% | n/a | 52.2% | 0.2493 | 0.2499 |
| 53 | 2026-03-17 to 2026-04-16 | 36 | 0.0% | n/a | 48.3% | 0.2444 | 0.2494 |
| 54 | 2026-04-16 to 2026-05-16 | 1 | 0.0% | n/a | 45.6% | 0.2505 | 0.2499 |
| 55 | 2026-05-16 to 2026-06-15 | 532 | 0.0% | n/a | 42.2% | 0.2459 | 0.2494 |
| 56 | 2026-06-15 to 2026-07-15 | 139 | 40.6% | 71.2% | 44.4% | 0.2417 | 0.2493 |
| 57 | 2026-07-15 to 2026-08-14 | 165 | 75.6% | 60.3% | 52.2% | 0.2436 | 0.2491 |
| 58 | 2026-08-14 to 2026-09-13 | 204 | 65.6% | 45.8% | 50.0% | 0.2600 | 0.2504 |
