# Backtest BNB 4h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.3% | naive 48.9%, always-up 51.0% |
| Coverage (share of non-neutral calls) | 22.8% | 100% |
| Brier score (lower is better) | 0.2506 | base rate 0.2499 |
| Log loss | 0.6944 | coin flip 0.6931 |
| Up calls: n / precision / recall | 840 / 51.8% / 20.6% | |
| Down calls: n / precision / recall | 103 / 56.3% / 2.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.87% (-0.35% to 9.07%)
- Brier improvement over base rate: -0.00065 (-0.00161 to 0.00027)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -37.0% | -54.9% | -0.65 |
| Naive (hold after an up candle) | -94.0% | -94.4% | -3.83 |
| Buy and hold | 23.8% | -59.6% | 0.48 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 1736 | 0.479 | 0.507 |
| 0.5-0.6 | 2381 | 0.537 | 0.513 |
| 0.6-0.7 | 23 | 0.624 | 0.522 |

## Most useful features (average gain)

- btc_ret_1: 14.81
- btc_ret_6: 14.46
- ret_6: 11.61
- log_ret_1: 10.53
- ret_1: 10.03
- lower_wick_pct: 9.14
- dist_ema9: 8.94
- adx14: 8.86

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 106 | 21.1% | 55.3% | 42.2% | 0.2472 | 0.2501 |
| 37 | 2024-11-22 to 2024-12-22 | 58 | 26.7% | 54.2% | 48.9% | 0.2498 | 0.2493 |
| 38 | 2024-12-22 to 2025-01-21 | 228 | 12.8% | 69.6% | 44.4% | 0.2481 | 0.2493 |
| 39 | 2025-01-21 to 2025-02-20 | 59 | 25.6% | 54.3% | 53.3% | 0.2512 | 0.2522 |
| 40 | 2025-02-20 to 2025-03-22 | 73 | 22.8% | 53.7% | 51.1% | 0.2502 | 0.2495 |
| 41 | 2025-03-22 to 2025-04-21 | 77 | 26.1% | 51.1% | 53.9% | 0.2509 | 0.2503 |
| 42 | 2025-04-21 to 2025-05-21 | 208 | 6.1% | 54.5% | 48.9% | 0.2468 | 0.2503 |
| 43 | 2025-05-21 to 2025-06-20 | 185 | 43.9% | 44.3% | 52.8% | 0.2557 | 0.2508 |
| 44 | 2025-06-20 to 2025-07-20 | 550 | 0.0% | n/a | 48.3% | 0.2505 | 0.2483 |
| 45 | 2025-07-20 to 2025-08-19 | 92 | 0.0% | n/a | 52.8% | 0.2484 | 0.2488 |
| 46 | 2025-08-19 to 2025-09-18 | 2 | 100.0% | 55.0% | 51.7% | 0.2478 | 0.2487 |
| 47 | 2025-09-18 to 2025-10-18 | 1 | 100.0% | 53.9% | 51.7% | 0.2489 | 0.2491 |
| 48 | 2025-10-18 to 2025-11-17 | 3 | 100.0% | 51.1% | 46.7% | 0.2538 | 0.2499 |
| 49 | 2025-11-17 to 2025-12-17 | 1 | 0.0% | n/a | 52.2% | 0.2510 | 0.2512 |
| 50 | 2025-12-17 to 2026-01-16 | 11 | 0.0% | n/a | 44.4% | 0.2510 | 0.2486 |
| 51 | 2026-01-16 to 2026-02-15 | 83 | 38.9% | 42.9% | 47.8% | 0.2573 | 0.2522 |
| 52 | 2026-02-15 to 2026-03-17 | 159 | 0.0% | n/a | 48.3% | 0.2504 | 0.2501 |
| 53 | 2026-03-17 to 2026-04-16 | 41 | 0.0% | n/a | 46.7% | 0.2491 | 0.2516 |
| 54 | 2026-04-16 to 2026-05-16 | 1 | 0.0% | n/a | 47.8% | 0.2525 | 0.2488 |
| 55 | 2026-05-16 to 2026-06-15 | 3 | 0.0% | n/a | 52.2% | 0.2508 | 0.2504 |
| 56 | 2026-06-15 to 2026-07-15 | 16 | 0.0% | n/a | 46.7% | 0.2505 | 0.2504 |
| 57 | 2026-07-15 to 2026-08-14 | 4 | 0.0% | n/a | 47.8% | 0.2524 | 0.2492 |
| 58 | 2026-08-14 to 2026-09-13 | 1 | 0.0% | n/a | 44.4% | 0.2495 | 0.2496 |
