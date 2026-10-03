# Backtest ADA 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.1% | naive 47.9%, always-up 48.3% |
| Coverage (share of non-neutral calls) | 17.9% | 100% |
| Brier score (lower is better) | 0.2491 | base rate 0.2498 |
| Log loss | 0.6914 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1014 / 53.9% / 6.8% | |
| Down calls: n / precision / recall | 1955 / 54.2% / 12.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.71% (4.72% to 10.92%)
- Brier improvement over base rate: 0.00067 (0.00007 to 0.00126)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -78.3% | -79.0% | -2.08 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -10.88 |
| Buy and hold | -40.0% | -89.3% | 0.20 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 3 | 0.394 | 0.333 |
| 0.4-0.5 | 12031 | 0.468 | 0.467 |
| 0.5-0.6 | 4423 | 0.530 | 0.521 |
| 0.6-0.7 | 103 | 0.615 | 0.631 |

## Most useful features (average gain)

- dist_ema9: 52.04
- ret_3: 25.46
- log_ret_1: 23.37
- btc_ret_1: 18.26
- dist_ema21: 17.77
- ret_1: 17.45
- stoch_k: 15.79
- btc_ret_6: 15.19

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 111 | 37.6% | 52.4% | 48.8% | 0.2499 | 0.2502 |
| 43 | 2024-11-14 to 2024-12-14 | 101 | 24.3% | 60.0% | 46.8% | 0.2464 | 0.2505 |
| 44 | 2024-12-14 to 2025-01-13 | 139 | 32.8% | 49.2% | 50.3% | 0.2531 | 0.2494 |
| 45 | 2025-01-13 to 2025-02-12 | 156 | 34.9% | 54.2% | 48.9% | 0.2491 | 0.2498 |
| 46 | 2025-02-12 to 2025-03-14 | 154 | 1.2% | 66.7% | 44.9% | 0.2469 | 0.2495 |
| 47 | 2025-03-14 to 2025-04-13 | 21 | 47.6% | 51.3% | 48.8% | 0.2503 | 0.2499 |
| 48 | 2025-04-13 to 2025-05-13 | 115 | 25.6% | 58.2% | 48.6% | 0.2486 | 0.2501 |
| 49 | 2025-05-13 to 2025-06-12 | 436 | 27.5% | 53.0% | 51.1% | 0.2495 | 0.2500 |
| 50 | 2025-06-12 to 2025-07-12 | 50 | 2.1% | 66.7% | 46.9% | 0.2488 | 0.2498 |
| 51 | 2025-07-12 to 2025-08-11 | 555 | 4.6% | 45.5% | 46.9% | 0.2496 | 0.2503 |
| 52 | 2025-08-11 to 2025-09-10 | 294 | 17.8% | 57.0% | 44.9% | 0.2491 | 0.2498 |
| 53 | 2025-09-10 to 2025-10-10 | 54 | 12.2% | 53.4% | 47.8% | 0.2484 | 0.2497 |
| 54 | 2025-10-10 to 2025-11-09 | 81 | 26.0% | 56.1% | 49.7% | 0.2497 | 0.2499 |
| 55 | 2025-11-09 to 2025-12-09 | 209 | 13.8% | 61.6% | 44.4% | 0.2471 | 0.2498 |
| 56 | 2025-12-09 to 2026-01-08 | 94 | 31.5% | 49.8% | 50.1% | 0.2515 | 0.2499 |
| 57 | 2026-01-08 to 2026-02-07 | 257 | 6.0% | 48.8% | 46.8% | 0.2498 | 0.2494 |
| 58 | 2026-02-07 to 2026-03-09 | 461 | 0.0% | n/a | 47.6% | 0.2485 | 0.2494 |
| 59 | 2026-03-09 to 2026-04-08 | 16 | 49.0% | 54.1% | 48.3% | 0.2485 | 0.2494 |
| 60 | 2026-04-08 to 2026-05-08 | 39 | 0.0% | n/a | 49.9% | 0.2504 | 0.2498 |
| 61 | 2026-05-08 to 2026-06-07 | 23 | 0.0% | n/a | 48.1% | 0.2487 | 0.2495 |
| 62 | 2026-06-07 to 2026-07-07 | 1 | 0.0% | n/a | 49.2% | 0.2493 | 0.2495 |
| 63 | 2026-07-07 to 2026-08-06 | 301 | 2.8% | 55.0% | 48.3% | 0.2484 | 0.2496 |
| 64 | 2026-08-06 to 2026-09-05 | 243 | 15.1% | 60.6% | 44.7% | 0.2481 | 0.2495 |
