# Backtest TRX 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.0% | naive 50.4%, always-up 51.8% |
| Coverage (share of non-neutral calls) | 21.2% | 100% |
| Brier score (lower is better) | 0.2505 | base rate 0.2497 |
| Log loss | 0.6941 | coin flip 0.6931 |
| Up calls: n / precision / recall | 876 / 53.0% / 21.6% | |
| Down calls: n / precision / recall | 1 / 100.0% / 0.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.66% (2.58% to 4.68%)
- Brier improvement over base rate: -0.00073 (-0.00179 to 0.00011)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 23.2% | -50.0% | 0.45 |
| Naive (hold after an up candle) | -85.9% | -93.2% | -2.11 |
| Buy and hold | 113.1% | -51.1% | 0.99 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 1245 | 0.485 | 0.522 |
| 0.5-0.6 | 2890 | 0.533 | 0.517 |
| 0.6-0.7 | 5 | 0.603 | 0.600 |

## Most useful features (average gain)

- btc_ret_6: 12.15
- ret_6: 11.76
- log_ret_1: 10.53
- dist_ema21: 10.38
- dist_ema9: 10.31
- ret_1: 9.84
- ret_12: 9.73
- hour_cos: 9.09

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 3 | 0.0% | n/a | 53.3% | 0.2555 | 0.2462 |
| 37 | 2024-11-22 to 2024-12-22 | 6 | 100.0% | 54.4% | 49.4% | 0.2480 | 0.2482 |
| 38 | 2024-12-22 to 2025-01-21 | 5 | 100.0% | 51.7% | 47.8% | 0.2530 | 0.2499 |
| 39 | 2025-01-21 to 2025-02-20 | 12 | 0.0% | n/a | 47.2% | 0.2513 | 0.2517 |
| 40 | 2025-02-20 to 2025-03-22 | 88 | 0.0% | n/a | 50.0% | 0.2514 | 0.2476 |
| 41 | 2025-03-22 to 2025-04-21 | 1 | 0.0% | n/a | 51.1% | 0.2489 | 0.2489 |
| 42 | 2025-04-21 to 2025-05-21 | 8 | 0.0% | n/a | 50.0% | 0.2499 | 0.2502 |
| 43 | 2025-05-21 to 2025-06-20 | 104 | 11.7% | 52.4% | 47.2% | 0.2510 | 0.2517 |
| 44 | 2025-06-20 to 2025-07-20 | 98 | 0.0% | n/a | 50.0% | 0.2469 | 0.2464 |
| 45 | 2025-07-20 to 2025-08-19 | 27 | 100.0% | 55.0% | 51.1% | 0.2478 | 0.2480 |
| 46 | 2025-08-19 to 2025-09-18 | 259 | 75.6% | 52.9% | 51.7% | 0.2522 | 0.2495 |
| 47 | 2025-09-18 to 2025-10-18 | 770 | 0.0% | n/a | 53.3% | 0.2522 | 0.2510 |
| 48 | 2025-10-18 to 2025-11-17 | 1 | 0.0% | n/a | 45.0% | 0.2501 | 0.2517 |
| 49 | 2025-11-17 to 2025-12-17 | 3 | 0.0% | n/a | 49.4% | 0.2499 | 0.2514 |
| 50 | 2025-12-17 to 2026-01-16 | 83 | 0.0% | n/a | 52.8% | 0.2517 | 0.2505 |
| 51 | 2026-01-16 to 2026-02-15 | 402 | 0.0% | n/a | 52.2% | 0.2498 | 0.2517 |
| 52 | 2026-02-15 to 2026-03-17 | 21 | 0.0% | n/a | 56.1% | 0.2506 | 0.2486 |
| 53 | 2026-03-17 to 2026-04-16 | 1 | 0.0% | n/a | 51.7% | 0.2481 | 0.2481 |
| 54 | 2026-04-16 to 2026-05-16 | 1 | 100.0% | 51.1% | 48.3% | 0.2515 | 0.2501 |
| 55 | 2026-05-16 to 2026-06-15 | 35 | 0.0% | n/a | 52.8% | 0.2512 | 0.2518 |
| 56 | 2026-06-15 to 2026-07-15 | 1 | 0.0% | n/a | 51.1% | 0.2501 | 0.2512 |
| 57 | 2026-07-15 to 2026-08-14 | 151 | 0.0% | n/a | 45.6% | 0.2504 | 0.2510 |
| 58 | 2026-08-14 to 2026-09-13 | 1 | 0.0% | n/a | 52.8% | 0.2490 | 0.2481 |
