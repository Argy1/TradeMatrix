# Backtest BCH 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.0% | naive 47.7%, always-up 48.4% |
| Coverage (share of non-neutral calls) | 15.4% | 100% |
| Brier score (lower is better) | 0.2492 | base rate 0.2498 |
| Log loss | 0.6916 | coin flip 0.6931 |
| Up calls: n / precision / recall | 983 / 55.6% / 6.8% | |
| Down calls: n / precision / recall | 1574 / 56.2% / 10.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 11.03% (8.94% to 13.31%)
- Brier improvement over base rate: 0.00056 (0.00018 to 0.00099)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -71.0% | -72.3% | -2.53 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -12.76 |
| Buy and hold | -30.0% | -72.7% | 0.14 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 17 | 0.387 | 0.412 |
| 0.4-0.5 | 12186 | 0.471 | 0.473 |
| 0.5-0.6 | 4169 | 0.528 | 0.512 |
| 0.6-0.7 | 188 | 0.624 | 0.569 |

## Most useful features (average gain)

- dist_ema9: 67.99
- ret_3: 33.18
- dist_ema21: 23.00
- btc_ret_6: 18.04
- btc_ret_1: 17.93
- ret_1: 14.12
- rsi14: 14.05
- bb_percent_b: 13.66

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 127 | 57.9% | 53.5% | 46.2% | 0.2508 | 0.2500 |
| 43 | 2024-11-14 to 2024-12-14 | 178 | 40.4% | 60.5% | 47.9% | 0.2467 | 0.2504 |
| 44 | 2024-12-14 to 2025-01-13 | 171 | 34.0% | 56.7% | 46.7% | 0.2476 | 0.2499 |
| 45 | 2025-01-13 to 2025-02-12 | 209 | 35.8% | 55.8% | 47.1% | 0.2492 | 0.2503 |
| 46 | 2025-02-12 to 2025-03-14 | 407 | 12.9% | 51.6% | 49.0% | 0.2502 | 0.2492 |
| 47 | 2025-03-14 to 2025-04-13 | 334 | 0.4% | 66.7% | 45.1% | 0.2491 | 0.2497 |
| 48 | 2025-04-13 to 2025-05-13 | 29 | 0.0% | n/a | 48.3% | 0.2493 | 0.2498 |
| 49 | 2025-05-13 to 2025-06-12 | 6 | 0.0% | n/a | 52.1% | 0.2498 | 0.2500 |
| 50 | 2025-06-12 to 2025-07-12 | 251 | 0.4% | 66.7% | 51.9% | 0.2492 | 0.2497 |
| 51 | 2025-07-12 to 2025-08-11 | 777 | 1.7% | 58.3% | 47.5% | 0.2500 | 0.2500 |
| 52 | 2025-08-11 to 2025-09-10 | 23 | 0.0% | n/a | 43.9% | 0.2494 | 0.2497 |
| 53 | 2025-09-10 to 2025-10-10 | 36 | 0.0% | n/a | 50.1% | 0.2485 | 0.2493 |
| 54 | 2025-10-10 to 2025-11-09 | 25 | 0.0% | n/a | 46.2% | 0.2484 | 0.2496 |
| 55 | 2025-11-09 to 2025-12-09 | 82 | 20.1% | 60.7% | 46.7% | 0.2495 | 0.2492 |
| 56 | 2025-12-09 to 2026-01-08 | 177 | 49.0% | 52.4% | 45.0% | 0.2508 | 0.2503 |
| 57 | 2026-01-08 to 2026-02-07 | 318 | 16.8% | 57.9% | 46.9% | 0.2484 | 0.2495 |
| 58 | 2026-02-07 to 2026-03-09 | 17 | 0.0% | n/a | 48.2% | 0.2495 | 0.2494 |
| 59 | 2026-03-09 to 2026-04-08 | 461 | 42.5% | 55.2% | 46.2% | 0.2505 | 0.2500 |
| 60 | 2026-04-08 to 2026-05-08 | 19 | 0.0% | n/a | 49.0% | 0.2488 | 0.2494 |
| 61 | 2026-05-08 to 2026-06-07 | 53 | 0.8% | 66.7% | 48.2% | 0.2484 | 0.2494 |
| 62 | 2026-06-07 to 2026-07-07 | 205 | 20.1% | 56.6% | 48.2% | 0.2500 | 0.2505 |
| 63 | 2026-07-07 to 2026-08-06 | 25 | 7.8% | 58.9% | 46.4% | 0.2485 | 0.2494 |
| 64 | 2026-08-06 to 2026-09-05 | 60 | 14.3% | 57.3% | 49.7% | 0.2494 | 0.2500 |
