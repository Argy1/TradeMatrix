# Backtest UNI 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-01 to 2026-09-21, 24 walk-forward folds, 17280 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.6% | naive 48.5%, always-up 48.9% |
| Coverage (share of non-neutral calls) | 6.1% | 100% |
| Brier score (lower is better) | 0.2494 | base rate 0.2499 |
| Log loss | 0.6920 | coin flip 0.6931 |
| Up calls: n / precision / recall | 294 / 54.8% / 1.9% | |
| Down calls: n / precision / recall | 760 / 53.2% / 4.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.36% (-1.30% to 8.88%)
- Brier improvement over base rate: 0.00048 (0.00020 to 0.00074)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -26.8% | -34.2% | -0.70 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -8.70 |
| Buy and hold | 21.9% | -87.8% | 0.61 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 7 | 0.396 | 0.429 |
| 0.4-0.5 | 13013 | 0.478 | 0.479 |
| 0.5-0.6 | 4253 | 0.520 | 0.520 |
| 0.6-0.7 | 7 | 0.610 | 0.571 |

## Most useful features (average gain)

- dist_ema9: 37.17
- ret_3: 28.58
- btc_ret_1: 16.78
- btc_ret_6: 16.36
- dist_ema21: 16.16
- log_ret_1: 14.18
- btc_rsi14: 13.26
- ret_6: 13.21

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 2024-10-01 to 2024-10-31 | 146 | 0.4% | 33.3% | 45.3% | 0.2489 | 0.2499 |
| 42 | 2024-10-31 to 2024-11-30 | 144 | 17.8% | 53.1% | 48.9% | 0.2492 | 0.2502 |
| 43 | 2024-11-30 to 2024-12-30 | 132 | 1.9% | 50.0% | 50.6% | 0.2481 | 0.2499 |
| 44 | 2024-12-30 to 2025-01-29 | 383 | 14.7% | 53.8% | 47.2% | 0.2483 | 0.2498 |
| 45 | 2025-01-29 to 2025-02-28 | 227 | 33.1% | 54.2% | 46.5% | 0.2485 | 0.2496 |
| 46 | 2025-02-28 to 2025-03-30 | 566 | 21.9% | 58.2% | 48.9% | 0.2502 | 0.2500 |
| 47 | 2025-03-30 to 2025-04-29 | 42 | 12.9% | 48.4% | 48.9% | 0.2496 | 0.2498 |
| 48 | 2025-04-29 to 2025-05-29 | 36 | 0.0% | n/a | 49.4% | 0.2492 | 0.2498 |
| 49 | 2025-05-29 to 2025-06-28 | 44 | 0.0% | n/a | 48.9% | 0.2500 | 0.2498 |
| 50 | 2025-06-28 to 2025-07-28 | 49 | 0.0% | n/a | 51.5% | 0.2497 | 0.2498 |
| 51 | 2025-07-28 to 2025-08-27 | 32 | 0.0% | n/a | 47.4% | 0.2499 | 0.2500 |
| 52 | 2025-08-27 to 2025-09-26 | 1 | 0.0% | n/a | 47.6% | 0.2497 | 0.2497 |
| 53 | 2025-09-26 to 2025-10-26 | 619 | 9.3% | 53.7% | 49.7% | 0.2488 | 0.2500 |
| 54 | 2025-10-26 to 2025-11-25 | 395 | 12.4% | 53.9% | 48.6% | 0.2490 | 0.2496 |
| 55 | 2025-11-25 to 2025-12-25 | 263 | 0.0% | n/a | 49.2% | 0.2492 | 0.2498 |
| 56 | 2025-12-25 to 2026-01-24 | 245 | 16.0% | 48.7% | 46.2% | 0.2507 | 0.2502 |
| 57 | 2026-01-24 to 2026-02-23 | 226 | 0.8% | 50.0% | 47.5% | 0.2506 | 0.2495 |
| 58 | 2026-02-23 to 2026-03-25 | 176 | 1.7% | 41.7% | 47.1% | 0.2492 | 0.2497 |
| 59 | 2026-03-25 to 2026-04-24 | 34 | 0.0% | n/a | 49.7% | 0.2494 | 0.2496 |
| 60 | 2026-04-24 to 2026-05-24 | 32 | 0.0% | n/a | 50.3% | 0.2499 | 0.2499 |
| 61 | 2026-05-24 to 2026-06-23 | 16 | 0.0% | n/a | 50.0% | 0.2497 | 0.2501 |
| 62 | 2026-06-23 to 2026-07-23 | 3 | 0.0% | n/a | 46.9% | 0.2499 | 0.2499 |
| 63 | 2026-07-23 to 2026-08-22 | 144 | 0.7% | 40.0% | 48.6% | 0.2493 | 0.2502 |
| 64 | 2026-08-22 to 2026-09-21 | 49 | 2.8% | 80.0% | 48.1% | 0.2488 | 0.2504 |
