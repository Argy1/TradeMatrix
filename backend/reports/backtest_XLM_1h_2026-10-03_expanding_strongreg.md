# Backtest XLM 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats both baselines, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.2% | naive 48.9%, always-up 47.3% |
| Coverage (share of non-neutral calls) | 37.1% | 100% |
| Brier score (lower is better) | 0.2486 | base rate 0.2494 |
| Log loss | 0.6904 | coin flip 0.6931 |
| Up calls: n / precision / recall | 708 / 56.8% / 5.1% | |
| Down calls: n / precision / recall | 5431 / 54.9% / 34.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.72% (5.55% to 7.84%)
- Brier improvement over base rate: 0.00076 (0.00028 to 0.00122)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -42.4% | -46.4% | -0.64 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -9.06 |
| Buy and hold | 98.5% | -76.6% | 0.86 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 3 | 0.284 | 0.333 |
| 0.3-0.4 | 347 | 0.380 | 0.435 |
| 0.4-0.5 | 12378 | 0.456 | 0.459 |
| 0.5-0.6 | 3730 | 0.527 | 0.518 |
| 0.6-0.7 | 102 | 0.622 | 0.627 |

## Most useful features (average gain)

- dist_ema9: 53.45
- dist_ema21: 37.98
- log_ret_1: 29.64
- ret_3: 26.32
- ret_1: 23.34
- btc_ret_1: 22.66
- dist_ema50: 18.45
- atr_pct: 17.85

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 72 | 63.1% | 58.4% | 46.0% | 0.2467 | 0.2494 |
| 43 | 2024-11-14 to 2024-12-14 | 106 | 55.8% | 52.7% | 47.4% | 0.2487 | 0.2508 |
| 44 | 2024-12-14 to 2025-01-13 | 365 | 25.0% | 52.2% | 47.2% | 0.2508 | 0.2489 |
| 45 | 2025-01-13 to 2025-02-12 | 80 | 49.2% | 56.2% | 48.5% | 0.2505 | 0.2495 |
| 46 | 2025-02-12 to 2025-03-14 | 62 | 27.6% | 58.3% | 47.4% | 0.2488 | 0.2501 |
| 47 | 2025-03-14 to 2025-04-13 | 93 | 32.4% | 54.9% | 48.1% | 0.2494 | 0.2498 |
| 48 | 2025-04-13 to 2025-05-13 | 108 | 2.5% | 55.6% | 47.5% | 0.2486 | 0.2501 |
| 49 | 2025-05-13 to 2025-06-12 | 112 | 17.9% | 52.7% | 48.9% | 0.2491 | 0.2503 |
| 50 | 2025-06-12 to 2025-07-12 | 59 | 15.0% | 54.6% | 52.5% | 0.2500 | 0.2499 |
| 51 | 2025-07-12 to 2025-08-11 | 120 | 0.0% | n/a | 48.9% | 0.2488 | 0.2501 |
| 52 | 2025-08-11 to 2025-09-10 | 128 | 9.3% | 58.2% | 49.0% | 0.2493 | 0.2497 |
| 53 | 2025-09-10 to 2025-10-10 | 68 | 19.7% | 56.3% | 50.7% | 0.2477 | 0.2491 |
| 54 | 2025-10-10 to 2025-11-09 | 257 | 29.4% | 58.0% | 50.3% | 0.2475 | 0.2492 |
| 55 | 2025-11-09 to 2025-12-09 | 206 | 35.1% | 55.7% | 49.3% | 0.2470 | 0.2490 |
| 56 | 2025-12-09 to 2026-01-08 | 238 | 49.3% | 53.2% | 50.4% | 0.2502 | 0.2494 |
| 57 | 2026-01-08 to 2026-02-07 | 41 | 28.1% | 59.9% | 51.4% | 0.2469 | 0.2486 |
| 58 | 2026-02-07 to 2026-03-09 | 114 | 0.0% | n/a | 49.9% | 0.2481 | 0.2488 |
| 59 | 2026-03-09 to 2026-04-08 | 17 | 89.2% | 53.9% | 46.8% | 0.2488 | 0.2489 |
| 60 | 2026-04-08 to 2026-05-08 | 21 | 0.0% | n/a | 50.6% | 0.2456 | 0.2478 |
| 61 | 2026-05-08 to 2026-06-07 | 1 | 100.0% | 53.6% | 51.0% | 0.2501 | 0.2490 |
| 62 | 2026-06-07 to 2026-07-07 | 1 | 100.0% | 54.4% | 47.5% | 0.2482 | 0.2487 |
| 63 | 2026-07-07 to 2026-08-06 | 38 | 48.5% | 58.2% | 49.7% | 0.2475 | 0.2489 |
| 64 | 2026-08-06 to 2026-09-05 | 164 | 55.6% | 53.8% | 47.1% | 0.2498 | 0.2496 |
