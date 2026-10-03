# Backtest NEAR 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-06 to 2026-09-26, 24 walk-forward folds, 4320 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.0% | naive 48.7%, always-up 48.4% |
| Coverage (share of non-neutral calls) | 16.1% | 100% |
| Brier score (lower is better) | 0.2500 | base rate 0.2498 |
| Log loss | 0.6931 | coin flip 0.6931 |
| Up calls: n / precision / recall | 74 / 45.9% / 1.6% | |
| Down calls: n / precision / recall | 622 / 52.7% / 14.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: -7.78% (-20.30% to 3.26%)
- Brier improvement over base rate: -0.00013 (-0.00083 to 0.00057)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -40.6% | -41.3% | -1.69 |
| Naive (hold after an up candle) | -93.8% | -96.6% | -1.66 |
| Buy and hold | 0.1% | -88.2% | 0.51 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 26 | 0.377 | 0.346 |
| 0.4-0.5 | 3319 | 0.468 | 0.483 |
| 0.5-0.6 | 961 | 0.520 | 0.493 |
| 0.6-0.7 | 14 | 0.615 | 0.500 |

## Most useful features (average gain)

- btc_ret_1: 13.47
- log_ret_1: 11.52
- dist_ema9: 10.66
- btc_ret_6: 9.81
- ret_1: 9.13
- macd_pct: 8.67
- btc_rsi14: 8.67
- lower_wick_pct: 8.64

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 34 | 2024-10-06 to 2024-11-05 | 48 | 0.0% | n/a | 47.8% | 0.2494 | 0.2501 |
| 35 | 2024-11-05 to 2024-12-05 | 56 | 0.0% | n/a | 38.9% | 0.2482 | 0.2504 |
| 36 | 2024-12-05 to 2025-01-04 | 2 | 0.0% | n/a | 46.1% | 0.2512 | 0.2495 |
| 37 | 2025-01-04 to 2025-02-03 | 431 | 55.0% | 54.5% | 50.0% | 0.2494 | 0.2497 |
| 38 | 2025-02-03 to 2025-03-05 | 364 | 15.6% | 53.6% | 51.1% | 0.2471 | 0.2499 |
| 39 | 2025-03-05 to 2025-04-04 | 61 | 18.9% | 61.8% | 53.3% | 0.2508 | 0.2499 |
| 40 | 2025-04-04 to 2025-05-04 | 252 | 15.0% | 55.6% | 50.6% | 0.2470 | 0.2500 |
| 41 | 2025-05-04 to 2025-06-03 | 734 | 34.4% | 54.8% | 50.0% | 0.2474 | 0.2499 |
| 42 | 2025-06-03 to 2025-07-03 | 133 | 15.0% | 44.4% | 45.0% | 0.2523 | 0.2498 |
| 43 | 2025-07-03 to 2025-08-02 | 369 | 0.0% | n/a | 48.3% | 0.2490 | 0.2497 |
| 44 | 2025-08-02 to 2025-09-01 | 24 | 0.0% | n/a | 52.8% | 0.2517 | 0.2502 |
| 45 | 2025-09-01 to 2025-10-01 | 1 | 0.0% | n/a | 46.1% | 0.2504 | 0.2500 |
| 46 | 2025-10-01 to 2025-10-31 | 3 | 0.0% | n/a | 46.7% | 0.2492 | 0.2497 |
| 47 | 2025-10-31 to 2025-11-30 | 1 | 0.0% | n/a | 51.7% | 0.2496 | 0.2498 |
| 48 | 2025-11-30 to 2025-12-30 | 87 | 0.0% | n/a | 52.8% | 0.2488 | 0.2496 |
| 49 | 2025-12-30 to 2026-01-29 | 168 | 100.0% | 50.0% | 44.4% | 0.2527 | 0.2500 |
| 50 | 2026-01-29 to 2026-02-28 | 1 | 0.0% | n/a | 49.4% | 0.2496 | 0.2494 |
| 51 | 2026-02-28 to 2026-03-30 | 35 | 100.0% | 55.6% | 41.7% | 0.2466 | 0.2493 |
| 52 | 2026-03-30 to 2026-04-29 | 33 | 2.2% | 0.0% | 52.2% | 0.2516 | 0.2501 |
| 53 | 2026-04-29 to 2026-05-29 | 58 | 0.6% | 0.0% | 46.7% | 0.2521 | 0.2504 |
| 54 | 2026-05-29 to 2026-06-28 | 120 | 6.1% | 27.3% | 54.4% | 0.2506 | 0.2494 |
| 55 | 2026-06-28 to 2026-07-28 | 122 | 0.0% | n/a | 46.7% | 0.2490 | 0.2492 |
| 56 | 2026-07-28 to 2026-08-27 | 1 | 0.0% | n/a | 47.8% | 0.2513 | 0.2499 |
| 57 | 2026-08-27 to 2026-09-26 | 153 | 23.9% | 41.9% | 53.3% | 0.2543 | 0.2505 |
