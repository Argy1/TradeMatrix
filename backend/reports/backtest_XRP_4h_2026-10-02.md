# Backtest XRP 4h (2026-10-02)

Out-of-sample period: 2024-11-10 to 2026-10-01, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.3% | naive 48.5%, always-up 49.5% |
| Coverage (share of non-neutral calls) | 38.3% | 100% |
| Brier score (lower is better) | 0.2520 | base rate 0.2499 |
| Log loss | 0.6972 | coin flip 0.6931 |
| Up calls: n / precision / recall | 586 / 51.2% / 14.6% | |
| Down calls: n / precision / recall | 998 / 52.9% / 25.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: -1.22% (-10.75% to 6.35%)
- Brier improvement over base rate: -0.00208 (-0.00368 to -0.00058)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 91.4% | -63.4% | 0.97 |
| Naive (hold after an up candle) | -89.3% | -95.0% | -1.63 |
| Buy and hold | 154.2% | -72.5% | 1.01 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 206 | 0.379 | 0.456 |
| 0.4-0.5 | 1750 | 0.450 | 0.500 |
| 0.5-0.6 | 2140 | 0.530 | 0.492 |
| 0.6-0.7 | 37 | 0.631 | 0.622 |
| 0.7-0.8 | 7 | 0.719 | 0.429 |

## Most useful features (average gain)

- log_ret_1: 6.86
- dist_ema9: 6.44
- dist_ema21: 6.42
- ret_1: 6.18
- stoch_k: 5.75
- bb_percent_b: 5.55
- macd_pct: 5.53
- ret_12: 5.46

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2024-11-10 to 2024-12-10 | 1 | 100.0% | 57.8% | 47.8% | 0.2444 | 0.2493 |
| 2 | 2024-12-10 to 2025-01-09 | 17 | 41.1% | 54.1% | 48.3% | 0.2507 | 0.2500 |
| 3 | 2025-01-09 to 2025-02-08 | 64 | 0.6% | 0.0% | 47.2% | 0.2500 | 0.2500 |
| 4 | 2025-02-08 to 2025-03-10 | 32 | 0.0% | n/a | 48.9% | 0.2525 | 0.2500 |
| 5 | 2025-03-10 to 2025-04-09 | 46 | 0.0% | n/a | 51.7% | 0.2510 | 0.2511 |
| 6 | 2025-04-09 to 2025-05-09 | 4 | 100.0% | 51.1% | 47.2% | 0.2543 | 0.2502 |
| 7 | 2025-05-09 to 2025-06-08 | 114 | 42.8% | 64.9% | 48.9% | 0.2432 | 0.2501 |
| 8 | 2025-06-08 to 2025-07-08 | 128 | 47.8% | 48.8% | 50.0% | 0.2560 | 0.2500 |
| 9 | 2025-07-08 to 2025-08-07 | 54 | 0.0% | n/a | 51.1% | 0.2463 | 0.2486 |
| 10 | 2025-08-07 to 2025-09-06 | 156 | 0.0% | n/a | 48.3% | 0.2532 | 0.2510 |
| 11 | 2025-09-06 to 2025-10-06 | 52 | 40.0% | 52.8% | 48.3% | 0.2538 | 0.2497 |
| 12 | 2025-10-06 to 2025-11-05 | 1 | 0.0% | n/a | 52.8% | 0.2500 | 0.2500 |
| 13 | 2025-11-05 to 2025-12-05 | 80 | 52.8% | 51.6% | 47.8% | 0.2559 | 0.2503 |
| 14 | 2025-12-05 to 2026-01-04 | 91 | 0.0% | n/a | 48.3% | 0.2559 | 0.2492 |
| 15 | 2026-01-04 to 2026-02-03 | 23 | 100.0% | 42.8% | 47.2% | 0.2611 | 0.2502 |
| 16 | 2026-02-03 to 2026-03-05 | 6 | 100.0% | 52.8% | 48.3% | 0.2517 | 0.2501 |
| 17 | 2026-03-05 to 2026-04-04 | 38 | 77.2% | 53.2% | 47.2% | 0.2507 | 0.2499 |
| 18 | 2026-04-04 to 2026-05-04 | 36 | 65.6% | 50.8% | 48.9% | 0.2528 | 0.2501 |
| 19 | 2026-05-04 to 2026-06-03 | 45 | 1.1% | 0.0% | 46.7% | 0.2515 | 0.2495 |
| 20 | 2026-06-03 to 2026-07-03 | 49 | 100.0% | 53.3% | 46.1% | 0.2570 | 0.2499 |
| 21 | 2026-07-03 to 2026-08-02 | 2 | 0.0% | n/a | 48.3% | 0.2503 | 0.2500 |
| 22 | 2026-08-02 to 2026-09-01 | 205 | 6.7% | 50.0% | 47.2% | 0.2512 | 0.2498 |
| 23 | 2026-09-01 to 2026-10-01 | 36 | 4.4% | 62.5% | 48.9% | 0.2529 | 0.2495 |
