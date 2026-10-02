# Backtest BTC 1h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.4% | naive 48.1%, always-up 50.4% |
| Coverage (share of non-neutral calls) | 17.9% | 100% |
| Brier score (lower is better) | 0.2489 | base rate 0.2500 |
| Log loss | 0.6910 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1712 / 56.6% / 11.6% | |
| Down calls: n / precision / recall | 1256 / 53.7% / 8.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.93% (3.40% to 10.17%)
- Brier improvement over base rate: 0.00108 (0.00057 to 0.00164)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -94.1% | -94.2% | -8.06 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -21.07 |
| Buy and hold | 21.5% | -53.7% | 0.45 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 2 | 0.396 | 0.500 |
| 0.4-0.5 | 7499 | 0.471 | 0.473 |
| 0.5-0.6 | 8852 | 0.528 | 0.529 |
| 0.6-0.7 | 207 | 0.612 | 0.556 |

## Most useful features (average gain)

- dist_ema9: 60.65
- ret_3: 48.84
- ret_6: 23.17
- log_ret_1: 19.48
- lower_wick_pct: 17.81
- stoch_k: 16.85
- ret_1: 16.41
- upper_wick_pct: 13.66

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 162 | 40.4% | 54.0% | 45.4% | 0.2493 | 0.2494 |
| 43 | 2024-11-14 to 2024-12-14 | 94 | 27.9% | 61.7% | 45.8% | 0.2460 | 0.2498 |
| 44 | 2024-12-14 to 2025-01-13 | 132 | 46.4% | 56.6% | 48.2% | 0.2484 | 0.2499 |
| 45 | 2025-01-13 to 2025-02-12 | 79 | 34.4% | 60.1% | 46.8% | 0.2462 | 0.2499 |
| 46 | 2025-02-12 to 2025-03-14 | 249 | 36.2% | 54.8% | 46.9% | 0.2499 | 0.2499 |
| 47 | 2025-03-14 to 2025-04-13 | 248 | 21.2% | 58.2% | 47.9% | 0.2476 | 0.2502 |
| 48 | 2025-04-13 to 2025-05-13 | 87 | 3.9% | 57.1% | 47.6% | 0.2486 | 0.2500 |
| 49 | 2025-05-13 to 2025-06-12 | 23 | 4.2% | 43.3% | 51.0% | 0.2504 | 0.2500 |
| 50 | 2025-06-12 to 2025-07-12 | 80 | 3.6% | 53.8% | 51.7% | 0.2492 | 0.2499 |
| 51 | 2025-07-12 to 2025-08-11 | 90 | 0.0% | n/a | 47.5% | 0.2494 | 0.2501 |
| 52 | 2025-08-11 to 2025-09-10 | 3 | 0.0% | n/a | 48.5% | 0.2497 | 0.2501 |
| 53 | 2025-09-10 to 2025-10-10 | 18 | 40.0% | 52.1% | 51.7% | 0.2497 | 0.2499 |
| 54 | 2025-10-10 to 2025-11-09 | 105 | 42.1% | 53.5% | 51.7% | 0.2511 | 0.2502 |
| 55 | 2025-11-09 to 2025-12-09 | 779 | 7.6% | 63.6% | 44.4% | 0.2465 | 0.2500 |
| 56 | 2025-12-09 to 2026-01-08 | 18 | 0.0% | n/a | 47.9% | 0.2500 | 0.2500 |
| 57 | 2026-01-08 to 2026-02-07 | 32 | 4.0% | 37.9% | 48.9% | 0.2496 | 0.2506 |
| 58 | 2026-02-07 to 2026-03-09 | 232 | 17.1% | 49.6% | 46.5% | 0.2498 | 0.2500 |
| 59 | 2026-03-09 to 2026-04-08 | 46 | 3.8% | 55.6% | 48.6% | 0.2491 | 0.2500 |
| 60 | 2026-04-08 to 2026-05-08 | 60 | 6.9% | 52.0% | 48.3% | 0.2491 | 0.2498 |
| 61 | 2026-05-08 to 2026-06-07 | 52 | 19.7% | 57.0% | 48.9% | 0.2495 | 0.2504 |
| 62 | 2026-06-07 to 2026-07-07 | 65 | 16.1% | 60.3% | 46.7% | 0.2468 | 0.2502 |
| 63 | 2026-07-07 to 2026-08-06 | 66 | 33.5% | 51.0% | 47.8% | 0.2497 | 0.2500 |
| 64 | 2026-08-06 to 2026-09-05 | 566 | 3.1% | 68.2% | 47.1% | 0.2491 | 0.2498 |
