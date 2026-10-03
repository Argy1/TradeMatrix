# Backtest LTC 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.0% | naive 47.7%, always-up 49.7% |
| Coverage (share of non-neutral calls) | 11.9% | 100% |
| Brier score (lower is better) | 0.2494 | base rate 0.2500 |
| Log loss | 0.6920 | coin flip 0.6931 |
| Up calls: n / precision / recall | 826 / 55.9% / 5.6% | |
| Down calls: n / precision / recall | 1150 / 54.3% / 7.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.15% (2.93% to 9.11%)
- Brier improvement over base rate: 0.00057 (0.00021 to 0.00096)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -67.9% | -68.5% | -2.50 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -13.34 |
| Buy and hold | -19.9% | -72.6% | 0.25 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 24 | 0.392 | 0.458 |
| 0.4-0.5 | 9061 | 0.475 | 0.481 |
| 0.5-0.6 | 7472 | 0.524 | 0.517 |
| 0.6-0.7 | 3 | 0.610 | 0.667 |

## Most useful features (average gain)

- dist_ema9: 50.10
- ret_3: 43.88
- log_ret_1: 34.13
- dist_ema21: 27.49
- ret_6: 27.29
- ret_1: 27.24
- stoch_k: 21.23
- btc_ret_1: 19.77

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 70 | 29.0% | 57.9% | 46.0% | 0.2503 | 0.2500 |
| 43 | 2024-11-14 to 2024-12-14 | 425 | 1.1% | 50.0% | 46.2% | 0.2483 | 0.2500 |
| 44 | 2024-12-14 to 2025-01-13 | 25 | 36.0% | 55.2% | 49.7% | 0.2504 | 0.2500 |
| 45 | 2025-01-13 to 2025-02-12 | 49 | 32.4% | 54.1% | 50.4% | 0.2505 | 0.2500 |
| 46 | 2025-02-12 to 2025-03-14 | 117 | 5.6% | 52.5% | 43.9% | 0.2481 | 0.2500 |
| 47 | 2025-03-14 to 2025-04-13 | 40 | 20.1% | 51.7% | 46.8% | 0.2506 | 0.2500 |
| 48 | 2025-04-13 to 2025-05-13 | 39 | 0.0% | n/a | 47.6% | 0.2504 | 0.2500 |
| 49 | 2025-05-13 to 2025-06-12 | 23 | 0.0% | n/a | 47.4% | 0.2490 | 0.2500 |
| 50 | 2025-06-12 to 2025-07-12 | 23 | 7.8% | 62.5% | 46.9% | 0.2488 | 0.2500 |
| 51 | 2025-07-12 to 2025-08-11 | 82 | 7.4% | 66.0% | 49.3% | 0.2483 | 0.2500 |
| 52 | 2025-08-11 to 2025-09-10 | 57 | 13.5% | 52.6% | 46.7% | 0.2479 | 0.2500 |
| 53 | 2025-09-10 to 2025-10-10 | 32 | 24.3% | 53.1% | 48.9% | 0.2502 | 0.2500 |
| 54 | 2025-10-10 to 2025-11-09 | 550 | 32.8% | 52.5% | 50.1% | 0.2492 | 0.2500 |
| 55 | 2025-11-09 to 2025-12-09 | 607 | 1.5% | 45.5% | 45.8% | 0.2481 | 0.2500 |
| 56 | 2025-12-09 to 2026-01-08 | 15 | 12.2% | 59.1% | 50.0% | 0.2501 | 0.2500 |
| 57 | 2026-01-08 to 2026-02-07 | 45 | 4.9% | 37.1% | 50.8% | 0.2508 | 0.2500 |
| 58 | 2026-02-07 to 2026-03-09 | 796 | 0.0% | n/a | 48.5% | 0.2492 | 0.2500 |
| 59 | 2026-03-09 to 2026-04-08 | 42 | 0.0% | n/a | 46.7% | 0.2489 | 0.2500 |
| 60 | 2026-04-08 to 2026-05-08 | 16 | 5.3% | 55.3% | 48.3% | 0.2504 | 0.2500 |
| 61 | 2026-05-08 to 2026-06-07 | 164 | 0.0% | n/a | 46.7% | 0.2482 | 0.2500 |
| 62 | 2026-06-07 to 2026-07-07 | 106 | 30.7% | 57.5% | 49.4% | 0.2501 | 0.2500 |
| 63 | 2026-07-07 to 2026-08-06 | 67 | 3.1% | 50.0% | 46.7% | 0.2496 | 0.2500 |
| 64 | 2026-08-06 to 2026-09-05 | 329 | 6.9% | 58.0% | 43.9% | 0.2496 | 0.2501 |
