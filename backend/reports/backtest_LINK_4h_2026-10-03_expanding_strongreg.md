# Backtest LINK 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 50.8% | naive 49.2%, always-up 49.0% |
| Coverage (share of non-neutral calls) | 14.3% | 100% |
| Brier score (lower is better) | 0.2508 | base rate 0.2500 |
| Log loss | 0.6948 | coin flip 0.6931 |
| Up calls: n / precision / recall | 363 / 49.3% / 8.8% | |
| Down calls: n / precision / recall | 230 / 53.0% / 5.8% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.60% (-1.76% to 23.11%)
- Brier improvement over base rate: -0.00085 (-0.00171 to 0.00000)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 15.0% | -28.8% | 0.40 |
| Naive (hold after an up candle) | -95.1% | -96.2% | -2.40 |
| Buy and hold | -0.7% | -76.5% | 0.43 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 5 | 0.389 | 0.600 |
| 0.4-0.5 | 2478 | 0.470 | 0.496 |
| 0.5-0.6 | 1657 | 0.527 | 0.482 |

## Most useful features (average gain)

- btc_ret_6: 13.07
- btc_ret_1: 12.51
- lower_wick_pct: 9.86
- upper_wick_pct: 9.77
- log_ret_1: 9.43
- ret_6: 9.27
- stoch_k: 8.98
- ret_1: 8.80

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 38 | 0.0% | n/a | 49.4% | 0.2511 | 0.2499 |
| 37 | 2024-11-22 to 2024-12-22 | 16 | 0.0% | n/a | 48.3% | 0.2490 | 0.2500 |
| 38 | 2024-12-22 to 2025-01-21 | 1 | 100.0% | 50.6% | 52.8% | 0.2533 | 0.2500 |
| 39 | 2025-01-21 to 2025-02-20 | 1 | 0.0% | n/a | 50.6% | 0.2519 | 0.2499 |
| 40 | 2025-02-20 to 2025-03-22 | 11 | 0.0% | n/a | 48.3% | 0.2493 | 0.2500 |
| 41 | 2025-03-22 to 2025-04-21 | 4 | 0.0% | n/a | 49.4% | 0.2485 | 0.2501 |
| 42 | 2025-04-21 to 2025-05-21 | 288 | 69.4% | 50.4% | 57.2% | 0.2542 | 0.2500 |
| 43 | 2025-05-21 to 2025-06-20 | 30 | 0.0% | n/a | 40.6% | 0.2496 | 0.2500 |
| 44 | 2025-06-20 to 2025-07-20 | 35 | 0.0% | n/a | 51.7% | 0.2513 | 0.2500 |
| 45 | 2025-07-20 to 2025-08-19 | 28 | 0.0% | n/a | 50.6% | 0.2498 | 0.2501 |
| 46 | 2025-08-19 to 2025-09-18 | 155 | 100.0% | 48.9% | 48.3% | 0.2549 | 0.2500 |
| 47 | 2025-09-18 to 2025-10-18 | 1 | 0.0% | n/a | 50.6% | 0.2517 | 0.2499 |
| 48 | 2025-10-18 to 2025-11-17 | 2 | 0.0% | n/a | 43.3% | 0.2516 | 0.2501 |
| 49 | 2025-11-17 to 2025-12-17 | 3 | 0.0% | n/a | 61.1% | 0.2513 | 0.2500 |
| 50 | 2025-12-17 to 2026-01-16 | 11 | 0.0% | n/a | 46.7% | 0.2534 | 0.2501 |
| 51 | 2026-01-16 to 2026-02-15 | 89 | 0.0% | n/a | 54.4% | 0.2538 | 0.2498 |
| 52 | 2026-02-15 to 2026-03-17 | 42 | 0.0% | n/a | 50.6% | 0.2514 | 0.2500 |
| 53 | 2026-03-17 to 2026-04-16 | 42 | 0.0% | n/a | 57.8% | 0.2471 | 0.2498 |
| 54 | 2026-04-16 to 2026-05-16 | 17 | 0.0% | n/a | 51.1% | 0.2481 | 0.2499 |
| 55 | 2026-05-16 to 2026-06-15 | 57 | 23.3% | 54.8% | 44.4% | 0.2492 | 0.2499 |
| 56 | 2026-06-15 to 2026-07-15 | 48 | 5.0% | 77.8% | 34.4% | 0.2472 | 0.2500 |
| 57 | 2026-07-15 to 2026-08-14 | 87 | 31.7% | 50.9% | 44.4% | 0.2502 | 0.2498 |
| 58 | 2026-08-14 to 2026-09-13 | 405 | 0.0% | n/a | 46.1% | 0.2510 | 0.2502 |
