# Backtest XRP 1h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.8% | naive 48.8%, always-up 49.8% |
| Coverage (share of non-neutral calls) | 14.3% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2500 |
| Log loss | 0.6921 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1353 / 56.5% / 9.3% | |
| Down calls: n / precision / recall | 1017 / 52.6% / 6.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.05% (2.01% to 9.76%)
- Brier improvement over base rate: 0.00058 (0.00011 to 0.00107)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -56.0% | -70.3% | -0.87 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -10.01 |
| Buy and hold | 161.5% | -72.9% | 1.02 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 33 | 0.394 | 0.424 |
| 0.4-0.5 | 9356 | 0.473 | 0.482 |
| 0.5-0.6 | 6969 | 0.527 | 0.515 |
| 0.6-0.7 | 202 | 0.620 | 0.624 |

## Most useful features (average gain)

- dist_ema9: 63.18
- dist_ema21: 38.74
- stoch_k: 33.24
- ret_3: 21.27
- ret_6: 21.09
- bb_percent_b: 18.98
- log_ret_1: 18.40
- hour_sin: 17.20

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 106 | 44.3% | 56.1% | 47.4% | 0.2478 | 0.2499 |
| 43 | 2024-11-14 to 2024-12-14 | 226 | 40.8% | 55.8% | 47.4% | 0.2473 | 0.2497 |
| 44 | 2024-12-14 to 2025-01-13 | 783 | 47.8% | 55.5% | 47.2% | 0.2497 | 0.2500 |
| 45 | 2025-01-13 to 2025-02-12 | 519 | 34.4% | 58.9% | 50.4% | 0.2495 | 0.2501 |
| 46 | 2025-02-12 to 2025-03-14 | 81 | 16.9% | 64.8% | 46.0% | 0.2466 | 0.2499 |
| 47 | 2025-03-14 to 2025-04-13 | 70 | 36.2% | 53.3% | 48.9% | 0.2496 | 0.2502 |
| 48 | 2025-04-13 to 2025-05-13 | 221 | 18.8% | 56.3% | 46.4% | 0.2473 | 0.2500 |
| 49 | 2025-05-13 to 2025-06-12 | 131 | 37.5% | 53.7% | 50.8% | 0.2511 | 0.2500 |
| 50 | 2025-06-12 to 2025-07-12 | 95 | 3.1% | 59.1% | 50.0% | 0.2502 | 0.2498 |
| 51 | 2025-07-12 to 2025-08-11 | 303 | 0.0% | n/a | 53.1% | 0.2499 | 0.2499 |
| 52 | 2025-08-11 to 2025-09-10 | 14 | 0.0% | n/a | 49.9% | 0.2488 | 0.2498 |
| 53 | 2025-09-10 to 2025-10-10 | 3 | 0.0% | n/a | 46.5% | 0.2503 | 0.2501 |
| 54 | 2025-10-10 to 2025-11-09 | 52 | 15.8% | 40.4% | 49.6% | 0.2508 | 0.2499 |
| 55 | 2025-11-09 to 2025-12-09 | 132 | 5.0% | 41.7% | 49.2% | 0.2503 | 0.2502 |
| 56 | 2025-12-09 to 2026-01-08 | 277 | 2.6% | 68.4% | 51.0% | 0.2507 | 0.2500 |
| 57 | 2026-01-08 to 2026-02-07 | 1 | 0.0% | n/a | 49.7% | 0.2492 | 0.2504 |
| 58 | 2026-02-07 to 2026-03-09 | 2 | 0.0% | n/a | 50.1% | 0.2492 | 0.2503 |
| 59 | 2026-03-09 to 2026-04-08 | 16 | 13.9% | 51.0% | 47.6% | 0.2505 | 0.2501 |
| 60 | 2026-04-08 to 2026-05-08 | 27 | 0.0% | n/a | 47.1% | 0.2506 | 0.2500 |
| 61 | 2026-05-08 to 2026-06-07 | 33 | 0.0% | n/a | 50.3% | 0.2490 | 0.2502 |
| 62 | 2026-06-07 to 2026-07-07 | 30 | 0.0% | n/a | 48.9% | 0.2494 | 0.2501 |
| 63 | 2026-07-07 to 2026-08-06 | 66 | 11.9% | 48.8% | 47.2% | 0.2490 | 0.2501 |
| 64 | 2026-08-06 to 2026-09-05 | 86 | 0.0% | n/a | 47.4% | 0.2508 | 0.2499 |
