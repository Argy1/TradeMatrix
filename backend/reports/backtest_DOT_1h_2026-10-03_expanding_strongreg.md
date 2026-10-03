# Backtest DOT 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.7% | naive 48.3%, always-up 47.7% |
| Coverage (share of non-neutral calls) | 22.5% | 100% |
| Brier score (lower is better) | 0.2485 | base rate 0.2497 |
| Log loss | 0.6902 | coin flip 0.6931 |
| Up calls: n / precision / recall | 709 / 54.9% / 4.9% | |
| Down calls: n / precision / recall | 3021 / 57.1% / 19.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.61% (6.02% to 11.08%)
- Brier improvement over base rate: 0.00111 (0.00050 to 0.00175)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -57.0% | -61.3% | -1.50 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -12.61 |
| Buy and hold | -79.4% | -93.6% | -0.50 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 288 | 0.384 | 0.392 |
| 0.4-0.5 | 11431 | 0.466 | 0.462 |
| 0.5-0.6 | 4791 | 0.523 | 0.516 |
| 0.6-0.7 | 50 | 0.610 | 0.580 |

## Most useful features (average gain)

- ret_3: 38.70
- dist_ema9: 33.65
- btc_ret_1: 23.25
- btc_ret_6: 16.15
- log_ret_1: 15.16
- ret_1: 13.85
- upper_wick_pct: 12.15
- ret_6: 11.77

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 53 | 32.4% | 53.6% | 49.3% | 0.2504 | 0.2501 |
| 43 | 2024-11-14 to 2024-12-14 | 134 | 22.6% | 57.7% | 48.2% | 0.2481 | 0.2505 |
| 44 | 2024-12-14 to 2025-01-13 | 218 | 27.1% | 53.3% | 46.7% | 0.2509 | 0.2496 |
| 45 | 2025-01-13 to 2025-02-12 | 32 | 38.3% | 51.4% | 47.6% | 0.2509 | 0.2501 |
| 46 | 2025-02-12 to 2025-03-14 | 54 | 0.0% | n/a | 47.5% | 0.2494 | 0.2502 |
| 47 | 2025-03-14 to 2025-04-13 | 110 | 0.0% | n/a | 49.0% | 0.2498 | 0.2497 |
| 48 | 2025-04-13 to 2025-05-13 | 34 | 0.0% | n/a | 48.3% | 0.2494 | 0.2500 |
| 49 | 2025-05-13 to 2025-06-12 | 40 | 2.8% | 45.0% | 48.6% | 0.2491 | 0.2499 |
| 50 | 2025-06-12 to 2025-07-12 | 33 | 0.0% | n/a | 51.7% | 0.2498 | 0.2498 |
| 51 | 2025-07-12 to 2025-08-11 | 239 | 0.0% | n/a | 47.5% | 0.2508 | 0.2502 |
| 52 | 2025-08-11 to 2025-09-10 | 22 | 0.0% | n/a | 49.6% | 0.2500 | 0.2499 |
| 53 | 2025-09-10 to 2025-10-10 | 19 | 0.0% | n/a | 48.9% | 0.2492 | 0.2497 |
| 54 | 2025-10-10 to 2025-11-09 | 14 | 0.0% | n/a | 49.4% | 0.2502 | 0.2501 |
| 55 | 2025-11-09 to 2025-12-09 | 62 | 1.7% | 58.3% | 42.5% | 0.2472 | 0.2494 |
| 56 | 2025-12-09 to 2026-01-08 | 285 | 37.4% | 57.2% | 49.9% | 0.2479 | 0.2496 |
| 57 | 2026-01-08 to 2026-02-07 | 497 | 25.0% | 60.0% | 47.2% | 0.2463 | 0.2490 |
| 58 | 2026-02-07 to 2026-03-09 | 151 | 51.8% | 54.4% | 48.2% | 0.2488 | 0.2496 |
| 59 | 2026-03-09 to 2026-04-08 | 166 | 49.9% | 57.4% | 48.2% | 0.2472 | 0.2493 |
| 60 | 2026-04-08 to 2026-05-08 | 27 | 2.4% | 64.7% | 50.1% | 0.2467 | 0.2490 |
| 61 | 2026-05-08 to 2026-06-07 | 511 | 62.4% | 53.9% | 48.1% | 0.2494 | 0.2496 |
| 62 | 2026-06-07 to 2026-07-07 | 283 | 39.9% | 61.0% | 49.2% | 0.2452 | 0.2490 |
| 63 | 2026-07-07 to 2026-08-06 | 179 | 55.7% | 60.6% | 44.4% | 0.2436 | 0.2488 |
| 64 | 2026-08-06 to 2026-09-05 | 93 | 68.9% | 58.9% | 50.1% | 0.2463 | 0.2490 |
