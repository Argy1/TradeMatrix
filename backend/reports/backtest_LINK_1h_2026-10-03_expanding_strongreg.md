# Backtest LINK 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.5% | naive 47.8%, always-up 47.4% |
| Coverage (share of non-neutral calls) | 27.0% | 100% |
| Brier score (lower is better) | 0.2486 | base rate 0.2498 |
| Log loss | 0.6903 | coin flip 0.6931 |
| Up calls: n / precision / recall | 352 / 49.4% / 2.2% | |
| Down calls: n / precision / recall | 4114 / 56.0% / 26.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 5.97% (2.49% to 9.02%)
- Brier improvement over base rate: 0.00116 (0.00066 to 0.00170)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -63.9% | -64.4% | -2.61 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -11.70 |
| Buy and hold | 2.9% | -76.8% | 0.46 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 217 | 0.393 | 0.410 |
| 0.4-0.5 | 13463 | 0.462 | 0.464 |
| 0.5-0.6 | 2841 | 0.523 | 0.525 |
| 0.6-0.7 | 39 | 0.615 | 0.538 |

## Most useful features (average gain)

- dist_ema9: 28.71
- log_ret_1: 28.44
- btc_ret_1: 20.48
- btc_ret_6: 20.27
- ret_3: 20.06
- ret_1: 16.47
- stoch_k: 13.68
- btc_rsi14: 11.69

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 18 | 18.5% | 48.9% | 48.1% | 0.2491 | 0.2500 |
| 43 | 2024-11-14 to 2024-12-14 | 58 | 13.3% | 51.0% | 50.6% | 0.2482 | 0.2501 |
| 44 | 2024-12-14 to 2025-01-13 | 43 | 25.0% | 54.4% | 47.5% | 0.2491 | 0.2498 |
| 45 | 2025-01-13 to 2025-02-12 | 205 | 28.3% | 52.9% | 47.6% | 0.2489 | 0.2498 |
| 46 | 2025-02-12 to 2025-03-14 | 312 | 31.4% | 56.2% | 47.2% | 0.2492 | 0.2499 |
| 47 | 2025-03-14 to 2025-04-13 | 105 | 3.9% | 53.6% | 44.6% | 0.2478 | 0.2498 |
| 48 | 2025-04-13 to 2025-05-13 | 65 | 28.9% | 60.1% | 47.4% | 0.2486 | 0.2498 |
| 49 | 2025-05-13 to 2025-06-12 | 64 | 34.9% | 52.6% | 48.5% | 0.2499 | 0.2499 |
| 50 | 2025-06-12 to 2025-07-12 | 59 | 0.4% | 66.7% | 47.8% | 0.2490 | 0.2498 |
| 51 | 2025-07-12 to 2025-08-11 | 181 | 5.6% | 55.0% | 47.2% | 0.2501 | 0.2501 |
| 52 | 2025-08-11 to 2025-09-10 | 114 | 6.7% | 54.2% | 48.3% | 0.2505 | 0.2498 |
| 53 | 2025-09-10 to 2025-10-10 | 196 | 0.4% | 33.3% | 48.1% | 0.2483 | 0.2496 |
| 54 | 2025-10-10 to 2025-11-09 | 18 | 0.0% | n/a | 47.1% | 0.2492 | 0.2498 |
| 55 | 2025-11-09 to 2025-12-09 | 37 | 12.9% | 53.8% | 45.0% | 0.2488 | 0.2499 |
| 56 | 2025-12-09 to 2026-01-08 | 62 | 11.0% | 65.8% | 47.1% | 0.2482 | 0.2496 |
| 57 | 2026-01-08 to 2026-02-07 | 461 | 17.2% | 54.8% | 48.2% | 0.2483 | 0.2494 |
| 58 | 2026-02-07 to 2026-03-09 | 162 | 36.8% | 59.6% | 48.1% | 0.2447 | 0.2491 |
| 59 | 2026-03-09 to 2026-04-08 | 96 | 86.1% | 56.1% | 47.9% | 0.2462 | 0.2492 |
| 60 | 2026-04-08 to 2026-05-08 | 58 | 91.2% | 57.1% | 51.2% | 0.2450 | 0.2491 |
| 61 | 2026-05-08 to 2026-06-07 | 614 | 94.0% | 53.9% | 49.2% | 0.2506 | 0.2496 |
| 62 | 2026-06-07 to 2026-07-07 | 131 | 40.8% | 59.2% | 46.4% | 0.2482 | 0.2498 |
| 63 | 2026-07-07 to 2026-08-06 | 89 | 31.7% | 50.4% | 48.9% | 0.2503 | 0.2500 |
| 64 | 2026-08-06 to 2026-09-05 | 191 | 1.2% | 33.3% | 47.1% | 0.2495 | 0.2505 |
