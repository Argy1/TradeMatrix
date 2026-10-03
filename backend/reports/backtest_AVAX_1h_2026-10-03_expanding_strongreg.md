# Backtest AVAX 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-06 to 2026-09-26, 24 walk-forward folds, 17280 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.2% | naive 48.1%, always-up 47.9% |
| Coverage (share of non-neutral calls) | 25.3% | 100% |
| Brier score (lower is better) | 0.2489 | base rate 0.2496 |
| Log loss | 0.6909 | coin flip 0.6931 |
| Up calls: n / precision / recall | 511 / 57.9% / 3.6% | |
| Down calls: n / precision / recall | 3865 / 54.9% / 23.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 10.61% (2.31% to 18.30%)
- Brier improvement over base rate: 0.00076 (0.00030 to 0.00123)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -34.6% | -46.3% | -0.81 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -11.74 |
| Buy and hold | -59.6% | -89.4% | -0.10 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 2 | 0.398 | 0.000 |
| 0.4-0.5 | 13694 | 0.464 | 0.466 |
| 0.5-0.6 | 3508 | 0.523 | 0.529 |
| 0.6-0.7 | 76 | 0.617 | 0.539 |

## Most useful features (average gain)

- ret_3: 36.42
- dist_ema9: 22.42
- log_ret_1: 22.19
- btc_ret_1: 18.72
- ret_6: 18.06
- ret_1: 16.43
- btc_ret_6: 16.08
- dist_ema21: 14.66

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 2024-10-06 to 2024-11-05 | 38 | 0.7% | 80.0% | 43.8% | 0.2481 | 0.2495 |
| 42 | 2024-11-05 to 2024-12-05 | 51 | 5.0% | 69.4% | 46.8% | 0.2494 | 0.2520 |
| 43 | 2024-12-05 to 2025-01-04 | 58 | 29.0% | 56.5% | 47.8% | 0.2495 | 0.2503 |
| 44 | 2025-01-04 to 2025-02-03 | 53 | 16.5% | 52.9% | 47.9% | 0.2507 | 0.2492 |
| 45 | 2025-02-03 to 2025-03-05 | 238 | 23.2% | 56.3% | 46.8% | 0.2491 | 0.2504 |
| 46 | 2025-03-05 to 2025-04-04 | 255 | 0.3% | 0.0% | 49.2% | 0.2493 | 0.2497 |
| 47 | 2025-04-04 to 2025-05-04 | 33 | 0.7% | 100.0% | 46.1% | 0.2480 | 0.2497 |
| 48 | 2025-05-04 to 2025-06-03 | 62 | 21.0% | 54.3% | 50.8% | 0.2487 | 0.2498 |
| 49 | 2025-06-03 to 2025-07-03 | 25 | 1.2% | 77.8% | 48.1% | 0.2482 | 0.2493 |
| 50 | 2025-07-03 to 2025-08-02 | 370 | 36.2% | 52.9% | 49.3% | 0.2514 | 0.2503 |
| 51 | 2025-08-02 to 2025-09-01 | 393 | 5.3% | 57.9% | 48.6% | 0.2487 | 0.2500 |
| 52 | 2025-09-01 to 2025-10-01 | 138 | 1.7% | 41.7% | 46.9% | 0.2493 | 0.2496 |
| 53 | 2025-10-01 to 2025-10-31 | 29 | 0.0% | n/a | 51.1% | 0.2490 | 0.2489 |
| 54 | 2025-10-31 to 2025-11-30 | 58 | 67.5% | 53.3% | 45.6% | 0.2511 | 0.2499 |
| 55 | 2025-11-30 to 2025-12-30 | 24 | 0.0% | n/a | 50.6% | 0.2495 | 0.2495 |
| 56 | 2025-12-30 to 2026-01-29 | 1 | 0.0% | n/a | 49.7% | 0.2475 | 0.2483 |
| 57 | 2026-01-29 to 2026-02-28 | 274 | 40.1% | 56.4% | 50.4% | 0.2474 | 0.2484 |
| 58 | 2026-02-28 to 2026-03-30 | 24 | 98.2% | 57.3% | 49.9% | 0.2441 | 0.2481 |
| 59 | 2026-03-30 to 2026-04-29 | 72 | 94.4% | 55.7% | 49.9% | 0.2475 | 0.2486 |
| 60 | 2026-04-29 to 2026-05-29 | 22 | 100.0% | 53.2% | 47.9% | 0.2500 | 0.2493 |
| 61 | 2026-05-29 to 2026-06-28 | 89 | 28.7% | 57.0% | 48.5% | 0.2482 | 0.2493 |
| 62 | 2026-06-28 to 2026-07-28 | 90 | 35.3% | 52.0% | 46.2% | 0.2495 | 0.2498 |
| 63 | 2026-07-28 to 2026-08-27 | 141 | 0.4% | 66.7% | 47.5% | 0.2494 | 0.2503 |
| 64 | 2026-08-27 to 2026-09-26 | 39 | 2.2% | 75.0% | 45.6% | 0.2489 | 0.2507 |
