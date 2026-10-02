# Backtest ETH 1h (2026-10-02)

Out-of-sample period: 2025-05-05 to 2026-09-27, 17 walk-forward folds, 12240 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 57.2% | naive 48.1%, always-up 50.4% |
| Coverage (share of non-neutral calls) | 2.9% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2500 |
| Log loss | 0.6928 | coin flip 0.6931 |
| Up calls: n / precision / recall | 341 / 57.5% / 3.2% | |
| Down calls: n / precision / recall | 14 / 50.0% / 0.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 14.90% (3.47% to 28.79%)
- Brier improvement over base rate: 0.00022 (-0.00010 to 0.00053)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -27.5% | -28.6% | -1.94 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -13.71 |
| Buy and hold | 48.8% | -69.1% | 0.77 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 4965 | 0.481 | 0.491 |
| 0.5-0.6 | 7207 | 0.518 | 0.513 |
| 0.6-0.7 | 68 | 0.617 | 0.574 |

## Most useful features (average gain)

- bb_percent_b: 7.67
- dist_ema21: 7.55
- log_ret_1: 7.47
- stoch_k: 7.40
- dist_ema9: 7.28
- ret_24: 7.20
- ret_6: 6.97
- hour_cos: 6.92

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2025-05-05 to 2025-06-04 | 31 | 37.4% | 56.5% | 48.5% | 0.2494 | 0.2497 |
| 2 | 2025-06-04 to 2025-07-04 | 21 | 0.4% | 100.0% | 51.0% | 0.2489 | 0.2498 |
| 3 | 2025-07-04 to 2025-08-03 | 16 | 4.4% | 56.2% | 49.4% | 0.2491 | 0.2496 |
| 4 | 2025-08-03 to 2025-09-02 | 3 | 0.0% | n/a | 46.7% | 0.2498 | 0.2497 |
| 5 | 2025-09-02 to 2025-10-02 | 1 | 0.0% | n/a | 48.6% | 0.2503 | 0.2502 |
| 6 | 2025-10-02 to 2025-11-01 | 2 | 0.0% | n/a | 51.2% | 0.2510 | 0.2502 |
| 7 | 2025-11-01 to 2025-12-01 | 1 | 0.0% | n/a | 45.8% | 0.2502 | 0.2506 |
| 8 | 2025-12-01 to 2025-12-31 | 12 | 1.4% | 80.0% | 47.9% | 0.2486 | 0.2495 |
| 9 | 2025-12-31 to 2026-01-30 | 1 | 0.0% | n/a | 49.3% | 0.2506 | 0.2500 |
| 10 | 2026-01-30 to 2026-03-01 | 13 | 0.0% | n/a | 49.9% | 0.2490 | 0.2505 |
| 11 | 2026-03-01 to 2026-03-31 | 6 | 0.0% | n/a | 48.3% | 0.2505 | 0.2503 |
| 12 | 2026-03-31 to 2026-04-30 | 2 | 0.0% | n/a | 45.8% | 0.2512 | 0.2500 |
| 13 | 2026-04-30 to 2026-05-30 | 8 | 0.0% | n/a | 47.1% | 0.2497 | 0.2501 |
| 14 | 2026-05-30 to 2026-06-29 | 29 | 1.5% | 54.5% | 48.3% | 0.2491 | 0.2499 |
| 15 | 2026-06-29 to 2026-07-29 | 65 | 0.7% | 40.0% | 46.0% | 0.2494 | 0.2500 |
| 16 | 2026-07-29 to 2026-08-28 | 3 | 0.0% | n/a | 46.5% | 0.2504 | 0.2502 |
| 17 | 2026-08-28 to 2026-09-27 | 9 | 3.5% | 56.0% | 47.9% | 0.2497 | 0.2502 |
