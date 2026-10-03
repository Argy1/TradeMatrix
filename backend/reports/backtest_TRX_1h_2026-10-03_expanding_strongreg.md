# Backtest TRX 1h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.8% | naive 50.5%, always-up 48.5% |
| Coverage (share of non-neutral calls) | 9.3% | 100% |
| Brier score (lower is better) | 0.2501 | base rate 0.2504 |
| Log loss | 0.6934 | coin flip 0.6931 |
| Up calls: n / precision / recall | 84 / 56.0% / 0.6% | |
| Down calls: n / precision / recall | 1453 / 53.7% / 9.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 13.80% (2.96% to 32.96%)
- Brier improvement over base rate: 0.00034 (-0.00031 to 0.00088)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -18.4% | -18.9% | -1.43 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -17.56 |
| Buy and hold | 110.4% | -52.6% | 1.07 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 13684 | 0.476 | 0.483 |
| 0.5-0.6 | 2876 | 0.516 | 0.497 |

## Most useful features (average gain)

- btc_ret_6: 22.11
- btc_rsi14: 19.04
- btc_ret_1: 16.10
- dist_ema21: 15.51
- dist_ema9: 15.07
- ret_3: 12.64
- hour_sin: 12.06
- upper_wick_pct: 11.44

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 7 | 100.0% | 53.5% | 49.9% | 0.2501 | 0.2515 |
| 43 | 2024-11-14 to 2024-12-14 | 1 | 0.0% | n/a | 49.6% | 0.2541 | 0.2491 |
| 44 | 2024-12-14 to 2025-01-13 | 532 | 12.4% | 53.9% | 48.6% | 0.2510 | 0.2505 |
| 45 | 2025-01-13 to 2025-02-12 | 798 | 0.0% | n/a | 51.0% | 0.2498 | 0.2498 |
| 46 | 2025-02-12 to 2025-03-14 | 71 | 0.0% | n/a | 50.6% | 0.2499 | 0.2506 |
| 47 | 2025-03-14 to 2025-04-13 | 10 | 0.0% | n/a | 53.5% | 0.2500 | 0.2502 |
| 48 | 2025-04-13 to 2025-05-13 | 3 | 0.0% | n/a | 49.7% | 0.2497 | 0.2507 |
| 49 | 2025-05-13 to 2025-06-12 | 24 | 0.1% | 100.0% | 48.6% | 0.2501 | 0.2501 |
| 50 | 2025-06-12 to 2025-07-12 | 58 | 0.0% | n/a | 48.6% | 0.2500 | 0.2501 |
| 51 | 2025-07-12 to 2025-08-11 | 272 | 0.0% | n/a | 49.7% | 0.2504 | 0.2508 |
| 52 | 2025-08-11 to 2025-09-10 | 167 | 0.0% | n/a | 48.9% | 0.2500 | 0.2503 |
| 53 | 2025-09-10 to 2025-10-10 | 11 | 0.0% | n/a | 51.0% | 0.2494 | 0.2511 |
| 54 | 2025-10-10 to 2025-11-09 | 202 | 1.0% | 57.1% | 49.9% | 0.2498 | 0.2506 |
| 55 | 2025-11-09 to 2025-12-09 | 4 | 0.0% | n/a | 51.7% | 0.2496 | 0.2506 |
| 56 | 2025-12-09 to 2026-01-08 | 73 | 0.0% | n/a | 51.8% | 0.2514 | 0.2500 |
| 57 | 2026-01-08 to 2026-02-07 | 450 | 0.0% | n/a | 47.8% | 0.2503 | 0.2506 |
| 58 | 2026-02-07 to 2026-03-09 | 2 | 0.0% | n/a | 54.6% | 0.2495 | 0.2508 |
| 59 | 2026-03-09 to 2026-04-08 | 21 | 0.0% | n/a | 49.9% | 0.2513 | 0.2503 |
| 60 | 2026-04-08 to 2026-05-08 | 1 | 0.0% | n/a | 48.3% | 0.2497 | 0.2504 |
| 61 | 2026-05-08 to 2026-06-07 | 413 | 0.0% | n/a | 51.1% | 0.2501 | 0.2504 |
| 62 | 2026-06-07 to 2026-07-07 | 161 | 0.0% | n/a | 51.9% | 0.2500 | 0.2502 |
| 63 | 2026-07-07 to 2026-08-06 | 10 | 0.0% | n/a | 53.5% | 0.2477 | 0.2511 |
| 64 | 2026-08-06 to 2026-09-05 | 1 | 100.0% | 54.0% | 52.6% | 0.2486 | 0.2507 |
