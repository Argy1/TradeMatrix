# Backtest ETH 4h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-23 to 2026-09-13, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 51.3% | naive 48.4%, always-up 50.8% |
| Coverage (share of non-neutral calls) | 23.7% | 100% |
| Brier score (lower is better) | 0.2510 | base rate 0.2500 |
| Log loss | 0.6951 | coin flip 0.6931 |
| Up calls: n / precision / recall | 745 / 49.7% / 17.6% | |
| Down calls: n / precision / recall | 237 / 56.5% / 6.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.47% (2.17% to 11.58%)
- Brier improvement over base rate: -0.00102 (-0.00236 to 0.00020)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -61.0% | -67.6% | -1.46 |
| Naive (hold after an up candle) | -91.0% | -93.3% | -2.52 |
| Buy and hold | -2.1% | -68.0% | 0.32 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 8 | 0.388 | 0.250 |
| 0.4-0.5 | 1777 | 0.475 | 0.497 |
| 0.5-0.6 | 2308 | 0.535 | 0.517 |
| 0.6-0.7 | 47 | 0.629 | 0.511 |

## Most useful features (average gain)

- log_ret_1: 17.06
- ret_6: 13.17
- btc_ret_1: 13.15
- btc_ret_6: 11.90
- ret_1: 11.55
- lower_wick_pct: 10.00
- upper_wick_pct: 9.70
- vol_ratio_20: 8.70

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 2024-10-23 to 2024-11-22 | 21 | 0.0% | n/a | 46.7% | 0.2510 | 0.2482 |
| 37 | 2024-11-22 to 2024-12-22 | 72 | 62.2% | 51.8% | 52.2% | 0.2550 | 0.2500 |
| 38 | 2024-12-22 to 2025-01-21 | 165 | 30.0% | 53.7% | 50.0% | 0.2512 | 0.2504 |
| 39 | 2025-01-21 to 2025-02-20 | 114 | 5.0% | 77.8% | 47.8% | 0.2469 | 0.2511 |
| 40 | 2025-02-20 to 2025-03-22 | 98 | 35.0% | 50.8% | 52.2% | 0.2483 | 0.2506 |
| 41 | 2025-03-22 to 2025-04-21 | 518 | 25.0% | 64.4% | 55.6% | 0.2480 | 0.2505 |
| 42 | 2025-04-21 to 2025-05-21 | 158 | 12.2% | 54.5% | 50.6% | 0.2527 | 0.2488 |
| 43 | 2025-05-21 to 2025-06-20 | 44 | 33.9% | 47.5% | 43.9% | 0.2549 | 0.2508 |
| 44 | 2025-06-20 to 2025-07-20 | 20 | 0.0% | n/a | 47.2% | 0.2491 | 0.2491 |
| 45 | 2025-07-20 to 2025-08-19 | 84 | 0.0% | n/a | 52.8% | 0.2477 | 0.2485 |
| 46 | 2025-08-19 to 2025-09-18 | 33 | 100.0% | 52.2% | 51.7% | 0.2535 | 0.2496 |
| 47 | 2025-09-18 to 2025-10-18 | 221 | 65.0% | 49.6% | 51.7% | 0.2564 | 0.2511 |
| 48 | 2025-10-18 to 2025-11-17 | 45 | 0.0% | n/a | 44.4% | 0.2503 | 0.2501 |
| 49 | 2025-11-17 to 2025-12-17 | 100 | 0.0% | n/a | 52.2% | 0.2494 | 0.2495 |
| 50 | 2025-12-17 to 2026-01-16 | 15 | 0.0% | n/a | 48.9% | 0.2483 | 0.2488 |
| 51 | 2026-01-16 to 2026-02-15 | 29 | 100.0% | 43.3% | 45.6% | 0.2614 | 0.2517 |
| 52 | 2026-02-15 to 2026-03-17 | 22 | 0.0% | n/a | 50.0% | 0.2527 | 0.2492 |
| 53 | 2026-03-17 to 2026-04-16 | 1 | 0.0% | n/a | 48.3% | 0.2507 | 0.2508 |
| 54 | 2026-04-16 to 2026-05-16 | 10 | 0.0% | n/a | 44.4% | 0.2497 | 0.2500 |
| 55 | 2026-05-16 to 2026-06-15 | 10 | 0.0% | n/a | 44.4% | 0.2490 | 0.2509 |
| 56 | 2026-06-15 to 2026-07-15 | 110 | 38.9% | 54.3% | 42.2% | 0.2499 | 0.2497 |
| 57 | 2026-07-15 to 2026-08-14 | 171 | 25.6% | 56.5% | 44.4% | 0.2496 | 0.2502 |
| 58 | 2026-08-14 to 2026-09-13 | 157 | 12.8% | 60.9% | 45.6% | 0.2468 | 0.2493 |
