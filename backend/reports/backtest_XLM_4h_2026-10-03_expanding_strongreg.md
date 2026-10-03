# Backtest XLM 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.8% | naive 47.7%, always-up 47.0% |
| Coverage (share of non-neutral calls) | 30.9% | 100% |
| Brier score (lower is better) | 0.2490 | base rate 0.2496 |
| Log loss | 0.6911 | coin flip 0.6931 |
| Up calls: n / precision / recall | 157 / 57.3% / 4.6% | |
| Down calls: n / precision / recall | 1123 / 55.6% / 28.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 11.15% (5.02% to 18.45%)
- Brier improvement over base rate: 0.00062 (-0.00065 to 0.00191)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 42.9% | -29.2% | 0.66 |
| Naive (hold after an up candle) | -96.5% | -98.7% | -2.04 |
| Buy and hold | 89.8% | -76.6% | 0.83 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 175 | 0.390 | 0.371 |
| 0.4-0.5 | 2577 | 0.457 | 0.462 |
| 0.5-0.6 | 1370 | 0.520 | 0.495 |
| 0.6-0.7 | 18 | 0.613 | 0.722 |

## Most useful features (average gain)

- ret_6: 13.18
- btc_ret_6: 12.15
- log_ret_1: 11.17
- ret_1: 10.73
- btc_ret_1: 9.66
- vol_ratio_20: 8.99
- lower_wick_pct: 8.65
- dist_ema50: 7.91

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 55 | 0.0% | n/a | 42.2% | 0.2500 | 0.2504 |
| 37 | 2024-11-22 to 2024-12-22 | 36 | 45.6% | 57.3% | 43.3% | 0.2523 | 0.2498 |
| 38 | 2024-12-22 to 2025-01-21 | 1 | 0.0% | n/a | 46.7% | 0.2524 | 0.2497 |
| 39 | 2025-01-21 to 2025-02-20 | 147 | 10.0% | 55.6% | 43.9% | 0.2464 | 0.2497 |
| 40 | 2025-02-20 to 2025-03-22 | 61 | 37.8% | 63.2% | 46.1% | 0.2473 | 0.2498 |
| 41 | 2025-03-22 to 2025-04-21 | 21 | 0.0% | n/a | 47.2% | 0.2494 | 0.2499 |
| 42 | 2025-04-21 to 2025-05-21 | 641 | 37.2% | 47.8% | 51.1% | 0.2532 | 0.2503 |
| 43 | 2025-05-21 to 2025-06-20 | 52 | 8.9% | 37.5% | 52.8% | 0.2531 | 0.2495 |
| 44 | 2025-06-20 to 2025-07-20 | 159 | 0.0% | n/a | 46.1% | 0.2500 | 0.2507 |
| 45 | 2025-07-20 to 2025-08-19 | 96 | 11.1% | 60.0% | 50.6% | 0.2520 | 0.2494 |
| 46 | 2025-08-19 to 2025-09-18 | 13 | 0.0% | n/a | 48.3% | 0.2514 | 0.2497 |
| 47 | 2025-09-18 to 2025-10-18 | 135 | 12.2% | 72.7% | 53.9% | 0.2480 | 0.2497 |
| 48 | 2025-10-18 to 2025-11-17 | 60 | 10.6% | 63.2% | 46.7% | 0.2480 | 0.2495 |
| 49 | 2025-11-17 to 2025-12-17 | 179 | 42.2% | 57.9% | 54.4% | 0.2433 | 0.2490 |
| 50 | 2025-12-17 to 2026-01-16 | 73 | 90.0% | 50.0% | 50.0% | 0.2566 | 0.2503 |
| 51 | 2026-01-16 to 2026-02-15 | 380 | 1.1% | 100.0% | 47.8% | 0.2479 | 0.2494 |
| 52 | 2026-02-15 to 2026-03-17 | 24 | 0.0% | n/a | 45.6% | 0.2502 | 0.2500 |
| 53 | 2026-03-17 to 2026-04-16 | 135 | 0.0% | n/a | 53.9% | 0.2467 | 0.2488 |
| 54 | 2026-04-16 to 2026-05-16 | 11 | 96.7% | 54.6% | 50.0% | 0.2473 | 0.2493 |
| 55 | 2026-05-16 to 2026-06-15 | 93 | 73.3% | 56.8% | 41.1% | 0.2417 | 0.2490 |
| 56 | 2026-06-15 to 2026-07-15 | 173 | 67.2% | 56.2% | 51.1% | 0.2450 | 0.2489 |
| 57 | 2026-07-15 to 2026-08-14 | 121 | 97.8% | 57.4% | 42.2% | 0.2441 | 0.2488 |
| 58 | 2026-08-14 to 2026-09-13 | 177 | 69.4% | 56.0% | 42.8% | 0.2507 | 0.2498 |
