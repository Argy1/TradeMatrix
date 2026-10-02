# Backtest BTC 4h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.3% | naive 46.5%, always-up 50.6% |
| Coverage (share of non-neutral calls) | 22.9% | 100% |
| Brier score (lower is better) | 0.2499 | base rate 0.2500 |
| Log loss | 0.6930 | coin flip 0.6931 |
| Up calls: n / precision / recall | 704 / 52.8% / 17.7% | |
| Down calls: n / precision / recall | 245 / 54.7% / 6.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.96% (0.56% to 15.44%)
- Brier improvement over base rate: 0.00009 (-0.00100 to 0.00108)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -62.9% | -69.0% | -2.48 |
| Naive (hold after an up candle) | -96.7% | -97.2% | -5.31 |
| Buy and hold | 16.3% | -53.4% | 0.40 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 2083 | 0.475 | 0.499 |
| 0.5-0.6 | 2011 | 0.537 | 0.510 |
| 0.6-0.7 | 46 | 0.609 | 0.652 |

## Most useful features (average gain)

- log_ret_1: 23.21
- ret_1: 16.94
- upper_wick_pct: 10.29
- ret_6: 10.28
- vol_ratio_20: 9.61
- lower_wick_pct: 9.34
- dist_ema9: 8.86
- stoch_k: 8.71

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 158 | 21.1% | 55.3% | 47.8% | 0.2471 | 0.2480 |
| 37 | 2024-11-22 to 2024-12-22 | 246 | 57.8% | 59.6% | 42.2% | 0.2489 | 0.2495 |
| 38 | 2024-12-22 to 2025-01-21 | 83 | 44.4% | 60.0% | 42.8% | 0.2448 | 0.2487 |
| 39 | 2025-01-21 to 2025-02-20 | 49 | 46.1% | 53.0% | 41.7% | 0.2511 | 0.2508 |
| 40 | 2025-02-20 to 2025-03-22 | 138 | 0.6% | 100.0% | 51.1% | 0.2475 | 0.2508 |
| 41 | 2025-03-22 to 2025-04-21 | 56 | 39.4% | 59.2% | 48.3% | 0.2473 | 0.2503 |
| 42 | 2025-04-21 to 2025-05-21 | 184 | 36.7% | 48.5% | 45.6% | 0.2508 | 0.2492 |
| 43 | 2025-05-21 to 2025-06-20 | 609 | 33.3% | 55.0% | 42.8% | 0.2526 | 0.2519 |
| 44 | 2025-06-20 to 2025-07-20 | 85 | 18.9% | 50.0% | 46.1% | 0.2515 | 0.2479 |
| 45 | 2025-07-20 to 2025-08-19 | 31 | 28.9% | 51.9% | 49.4% | 0.2502 | 0.2501 |
| 46 | 2025-08-19 to 2025-09-18 | 33 | 34.4% | 50.0% | 48.3% | 0.2522 | 0.2511 |
| 47 | 2025-09-18 to 2025-10-18 | 93 | 10.0% | 33.3% | 50.6% | 0.2494 | 0.2512 |
| 48 | 2025-10-18 to 2025-11-17 | 66 | 2.8% | 20.0% | 50.0% | 0.2514 | 0.2502 |
| 49 | 2025-11-17 to 2025-12-17 | 35 | 0.0% | n/a | 52.8% | 0.2501 | 0.2502 |
| 50 | 2025-12-17 to 2026-01-16 | 1 | 0.0% | n/a | 45.0% | 0.2525 | 0.2479 |
| 51 | 2026-01-16 to 2026-02-15 | 1 | 100.0% | 45.6% | 47.8% | 0.2588 | 0.2515 |
| 52 | 2026-02-15 to 2026-03-17 | 1 | 0.0% | n/a | 46.7% | 0.2502 | 0.2496 |
| 53 | 2026-03-17 to 2026-04-16 | 21 | 0.0% | n/a | 47.2% | 0.2494 | 0.2506 |
| 54 | 2026-04-16 to 2026-05-16 | 32 | 0.0% | n/a | 46.7% | 0.2485 | 0.2504 |
| 55 | 2026-05-16 to 2026-06-15 | 32 | 2.2% | 50.0% | 44.4% | 0.2490 | 0.2507 |
| 56 | 2026-06-15 to 2026-07-15 | 83 | 6.7% | 66.7% | 42.2% | 0.2474 | 0.2507 |
| 57 | 2026-07-15 to 2026-08-14 | 78 | 36.7% | 63.6% | 44.4% | 0.2491 | 0.2503 |
| 58 | 2026-08-14 to 2026-09-13 | 27 | 7.2% | 53.8% | 46.7% | 0.2489 | 0.2491 |
