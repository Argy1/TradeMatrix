# Backtest ETH 1h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.0% | naive 47.7%, always-up 50.5% |
| Coverage (share of non-neutral calls) | 16.7% | 100% |
| Brier score (lower is better) | 0.2490 | base rate 0.2500 |
| Log loss | 0.6912 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1649 / 55.2% / 10.9% | |
| Down calls: n / precision / recall | 1111 / 57.2% / 7.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 4.79% (0.00% to 8.80%)
- Brier improvement over base rate: 0.00094 (0.00030 to 0.00166)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -94.7% | -94.8% | -5.66 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -13.78 |
| Buy and hold | -5.3% | -69.1% | 0.29 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 83 | 0.390 | 0.325 |
| 0.4-0.5 | 6845 | 0.472 | 0.479 |
| 0.5-0.6 | 9413 | 0.527 | 0.523 |
| 0.6-0.7 | 219 | 0.617 | 0.612 |

## Most useful features (average gain)

- dist_ema9: 70.70
- ret_3: 36.02
- btc_ret_6: 22.34
- btc_ret_1: 18.70
- ret_6: 18.33
- rsi14: 16.13
- ret_1: 15.69
- log_ret_1: 14.36

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 354 | 48.8% | 59.8% | 44.0% | 0.2441 | 0.2499 |
| 43 | 2024-11-14 to 2024-12-14 | 111 | 57.6% | 56.9% | 47.1% | 0.2456 | 0.2498 |
| 44 | 2024-12-14 to 2025-01-13 | 136 | 57.6% | 56.1% | 48.3% | 0.2492 | 0.2502 |
| 45 | 2025-01-13 to 2025-02-12 | 320 | 39.4% | 59.9% | 45.7% | 0.2461 | 0.2500 |
| 46 | 2025-02-12 to 2025-03-14 | 233 | 41.5% | 53.5% | 47.5% | 0.2514 | 0.2498 |
| 47 | 2025-03-14 to 2025-04-13 | 430 | 1.0% | 28.6% | 48.2% | 0.2505 | 0.2501 |
| 48 | 2025-04-13 to 2025-05-13 | 572 | 0.0% | n/a | 47.9% | 0.2499 | 0.2497 |
| 49 | 2025-05-13 to 2025-06-12 | 1 | 0.0% | n/a | 49.9% | 0.2496 | 0.2497 |
| 50 | 2025-06-12 to 2025-07-12 | 19 | 0.0% | n/a | 51.1% | 0.2495 | 0.2499 |
| 51 | 2025-07-12 to 2025-08-11 | 254 | 19.2% | 57.2% | 47.8% | 0.2494 | 0.2497 |
| 52 | 2025-08-11 to 2025-09-10 | 16 | 16.2% | 55.6% | 46.8% | 0.2486 | 0.2499 |
| 53 | 2025-09-10 to 2025-10-10 | 306 | 29.6% | 55.4% | 50.3% | 0.2491 | 0.2501 |
| 54 | 2025-10-10 to 2025-11-09 | 35 | 6.8% | 49.0% | 49.4% | 0.2499 | 0.2502 |
| 55 | 2025-11-09 to 2025-12-09 | 321 | 18.3% | 56.8% | 46.9% | 0.2475 | 0.2499 |
| 56 | 2025-12-09 to 2026-01-08 | 19 | 0.0% | n/a | 48.2% | 0.2496 | 0.2499 |
| 57 | 2026-01-08 to 2026-02-07 | 53 | 29.4% | 50.0% | 50.1% | 0.2514 | 0.2504 |
| 58 | 2026-02-07 to 2026-03-09 | 532 | 0.7% | 40.0% | 47.1% | 0.2493 | 0.2502 |
| 59 | 2026-03-09 to 2026-04-08 | 62 | 10.1% | 52.1% | 49.3% | 0.2505 | 0.2500 |
| 60 | 2026-04-08 to 2026-05-08 | 43 | 0.0% | n/a | 47.2% | 0.2499 | 0.2500 |
| 61 | 2026-05-08 to 2026-06-07 | 34 | 0.0% | n/a | 47.5% | 0.2496 | 0.2502 |
| 62 | 2026-06-07 to 2026-07-07 | 300 | 0.0% | n/a | 46.9% | 0.2489 | 0.2501 |
| 63 | 2026-07-07 to 2026-08-06 | 101 | 6.9% | 56.0% | 46.4% | 0.2497 | 0.2500 |
| 64 | 2026-08-06 to 2026-09-05 | 87 | 0.0% | n/a | 43.5% | 0.2486 | 0.2499 |
