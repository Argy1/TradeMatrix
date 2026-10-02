# Backtest BTC 1h (2026-10-02)

Out-of-sample period: 2025-05-05 to 2026-09-27, 17 walk-forward folds, 12240 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.7% | naive 48.4%, always-up 50.2% |
| Coverage (share of non-neutral calls) | 12.9% | 100% |
| Brier score (lower is better) | 0.2501 | base rate 0.2500 |
| Log loss | 0.6934 | coin flip 0.6931 |
| Up calls: n / precision / recall | 583 / 54.4% / 5.2% | |
| Down calls: n / precision / recall | 999 / 51.8% / 8.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.71% (2.86% to 17.94%)
- Brier improvement over base rate: -0.00013 (-0.00088 to 0.00052)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -72.0% | -72.1% | -7.43 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -22.93 |
| Buy and hold | -10.1% | -53.7% | 0.02 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 81 | 0.379 | 0.407 |
| 0.4-0.5 | 5827 | 0.476 | 0.494 |
| 0.5-0.6 | 6324 | 0.523 | 0.510 |
| 0.6-0.7 | 8 | 0.608 | 0.625 |

## Most useful features (average gain)

- stoch_k: 7.32
- ret_3: 6.83
- lower_wick_pct: 6.64
- dist_ema9: 6.54
- log_ret_1: 6.45
- ret_24: 6.25
- ret_1: 6.25
- macd_pct: 6.24

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2025-05-05 to 2025-06-04 | 17 | 5.8% | 52.4% | 50.4% | 0.2489 | 0.2499 |
| 2 | 2025-06-04 to 2025-07-04 | 59 | 6.9% | 60.0% | 51.2% | 0.2497 | 0.2501 |
| 3 | 2025-07-04 to 2025-08-03 | 71 | 2.2% | 50.0% | 49.4% | 0.2494 | 0.2498 |
| 4 | 2025-08-03 to 2025-09-02 | 29 | 0.0% | n/a | 46.5% | 0.2499 | 0.2501 |
| 5 | 2025-09-02 to 2025-10-02 | 74 | 31.8% | 55.5% | 50.4% | 0.2503 | 0.2499 |
| 6 | 2025-10-02 to 2025-11-01 | 52 | 19.6% | 53.2% | 54.2% | 0.2502 | 0.2500 |
| 7 | 2025-11-01 to 2025-12-01 | 18 | 25.6% | 54.3% | 44.9% | 0.2496 | 0.2500 |
| 8 | 2025-12-01 to 2025-12-31 | 3 | 0.0% | n/a | 47.1% | 0.2500 | 0.2499 |
| 9 | 2025-12-31 to 2026-01-30 | 28 | 19.0% | 54.7% | 49.3% | 0.2500 | 0.2501 |
| 10 | 2026-01-30 to 2026-03-01 | 29 | 44.2% | 48.7% | 46.2% | 0.2538 | 0.2501 |
| 11 | 2026-03-01 to 2026-03-31 | 3 | 0.0% | n/a | 47.8% | 0.2510 | 0.2500 |
| 12 | 2026-03-31 to 2026-04-30 | 7 | 0.0% | n/a | 48.3% | 0.2505 | 0.2500 |
| 13 | 2026-04-30 to 2026-05-30 | 39 | 0.7% | 100.0% | 49.0% | 0.2491 | 0.2500 |
| 14 | 2026-05-30 to 2026-06-29 | 26 | 15.3% | 56.4% | 46.8% | 0.2473 | 0.2499 |
| 15 | 2026-06-29 to 2026-07-29 | 18 | 48.6% | 50.0% | 47.5% | 0.2533 | 0.2500 |
| 16 | 2026-07-29 to 2026-08-28 | 3 | 0.0% | n/a | 47.9% | 0.2499 | 0.2501 |
| 17 | 2026-08-28 to 2026-09-27 | 63 | 0.0% | n/a | 45.4% | 0.2495 | 0.2501 |
