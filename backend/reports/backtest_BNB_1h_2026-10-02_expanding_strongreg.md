# Backtest BNB 1h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.5% | naive 48.6%, always-up 51.4% |
| Coverage (share of non-neutral calls) | 15.0% | 100% |
| Brier score (lower is better) | 0.2493 | base rate 0.2499 |
| Log loss | 0.6917 | coin flip 0.6931 |
| Up calls: n / precision / recall | 2129 / 57.1% / 14.3% | |
| Down calls: n / precision / recall | 347 / 52.7% / 2.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.55% (3.46% to 11.30%)
- Brier improvement over base rate: 0.00065 (0.00016 to 0.00112)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -92.9% | -93.0% | -4.86 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -18.09 |
| Buy and hold | 27.6% | -60.4% | 0.51 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 2 | 0.399 | 1.000 |
| 0.4-0.5 | 5517 | 0.482 | 0.490 |
| 0.5-0.6 | 10861 | 0.529 | 0.526 |
| 0.6-0.7 | 180 | 0.613 | 0.544 |

## Most useful features (average gain)

- dist_ema9: 42.94
- ret_3: 25.67
- log_ret_1: 22.00
- ret_1: 20.73
- btc_ret_1: 19.28
- btc_ret_6: 18.75
- dist_ema21: 18.33
- bb_percent_b: 18.29

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 172 | 28.5% | 50.7% | 49.2% | 0.2491 | 0.2500 |
| 43 | 2024-11-14 to 2024-12-14 | 181 | 16.1% | 69.0% | 45.0% | 0.2472 | 0.2499 |
| 44 | 2024-12-14 to 2025-01-13 | 77 | 27.6% | 51.8% | 48.6% | 0.2504 | 0.2500 |
| 45 | 2025-01-13 to 2025-02-12 | 86 | 21.1% | 59.2% | 51.4% | 0.2485 | 0.2500 |
| 46 | 2025-02-12 to 2025-03-14 | 114 | 6.0% | 62.8% | 47.8% | 0.2483 | 0.2500 |
| 47 | 2025-03-14 to 2025-04-13 | 32 | 6.9% | 68.0% | 50.0% | 0.2491 | 0.2500 |
| 48 | 2025-04-13 to 2025-05-13 | 160 | 26.0% | 56.7% | 47.6% | 0.2480 | 0.2499 |
| 49 | 2025-05-13 to 2025-06-12 | 76 | 37.1% | 53.6% | 51.2% | 0.2493 | 0.2498 |
| 50 | 2025-06-12 to 2025-07-12 | 77 | 14.9% | 60.7% | 51.4% | 0.2482 | 0.2498 |
| 51 | 2025-07-12 to 2025-08-11 | 352 | 37.4% | 56.9% | 48.6% | 0.2485 | 0.2499 |
| 52 | 2025-08-11 to 2025-09-10 | 23 | 21.8% | 58.0% | 44.3% | 0.2472 | 0.2498 |
| 53 | 2025-09-10 to 2025-10-10 | 42 | 16.9% | 62.3% | 48.6% | 0.2482 | 0.2498 |
| 54 | 2025-10-10 to 2025-11-09 | 115 | 54.4% | 54.6% | 48.9% | 0.2503 | 0.2499 |
| 55 | 2025-11-09 to 2025-12-09 | 40 | 14.4% | 57.7% | 48.3% | 0.2488 | 0.2499 |
| 56 | 2025-12-09 to 2026-01-08 | 31 | 4.7% | 52.9% | 47.1% | 0.2496 | 0.2499 |
| 57 | 2026-01-08 to 2026-02-07 | 182 | 7.9% | 45.6% | 49.0% | 0.2521 | 0.2504 |
| 58 | 2026-02-07 to 2026-03-09 | 126 | 0.0% | n/a | 50.8% | 0.2500 | 0.2501 |
| 59 | 2026-03-09 to 2026-04-08 | 35 | 0.0% | n/a | 46.4% | 0.2516 | 0.2498 |
| 60 | 2026-04-08 to 2026-05-08 | 1 | 0.0% | n/a | 46.7% | 0.2497 | 0.2498 |
| 61 | 2026-05-08 to 2026-06-07 | 228 | 1.7% | 58.3% | 50.6% | 0.2512 | 0.2501 |
| 62 | 2026-06-07 to 2026-07-07 | 27 | 0.0% | n/a | 50.8% | 0.2494 | 0.2499 |
| 63 | 2026-07-07 to 2026-08-06 | 57 | 0.0% | n/a | 47.8% | 0.2495 | 0.2498 |
| 64 | 2026-08-06 to 2026-09-05 | 39 | 0.4% | 33.3% | 48.5% | 0.2489 | 0.2498 |
