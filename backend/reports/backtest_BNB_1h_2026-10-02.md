# Backtest BNB 1h (2026-10-02)

Out-of-sample period: 2025-05-05 to 2026-09-27, 17 walk-forward folds, 12240 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.6% | naive 48.7%, always-up 51.5% |
| Coverage (share of non-neutral calls) | 9.2% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2499 |
| Log loss | 0.6929 | coin flip 0.6931 |
| Up calls: n / precision / recall | 669 / 55.9% / 5.9% | |
| Down calls: n / precision / recall | 461 / 55.1% / 4.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.98% (-2.54% to 10.94%)
- Brier improvement over base rate: 0.00011 (-0.00083 to 0.00084)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -59.4% | -59.5% | -3.42 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -19.28 |
| Buy and hold | 30.1% | -60.4% | 0.63 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 43 | 0.383 | 0.465 |
| 0.4-0.5 | 3841 | 0.481 | 0.493 |
| 0.5-0.6 | 8127 | 0.519 | 0.525 |
| 0.6-0.7 | 203 | 0.634 | 0.532 |
| 0.7-0.8 | 26 | 0.728 | 0.462 |

## Most useful features (average gain)

- dist_ema21: 8.03
- ret_3: 7.41
- dist_ema9: 7.23
- rsi14: 6.82
- dist_ema50: 6.74
- hour_cos: 6.65
- log_ret_1: 6.63
- ret_1: 6.53

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2025-05-05 to 2025-06-04 | 16 | 3.8% | 51.9% | 52.5% | 0.2496 | 0.2495 |
| 2 | 2025-06-04 to 2025-07-04 | 110 | 0.0% | n/a | 51.5% | 0.2495 | 0.2496 |
| 3 | 2025-07-04 to 2025-08-03 | 1 | 0.0% | n/a | 48.9% | 0.2494 | 0.2495 |
| 4 | 2025-08-03 to 2025-09-02 | 74 | 0.0% | n/a | 43.6% | 0.2495 | 0.2494 |
| 5 | 2025-09-02 to 2025-10-02 | 123 | 3.1% | 72.7% | 48.9% | 0.2477 | 0.2488 |
| 6 | 2025-10-02 to 2025-11-01 | 71 | 34.7% | 61.2% | 49.0% | 0.2464 | 0.2496 |
| 7 | 2025-11-01 to 2025-12-01 | 75 | 57.9% | 54.7% | 47.5% | 0.2567 | 0.2508 |
| 8 | 2025-12-01 to 2025-12-31 | 3 | 0.0% | n/a | 46.8% | 0.2497 | 0.2499 |
| 9 | 2025-12-31 to 2026-01-30 | 10 | 0.0% | n/a | 48.8% | 0.2502 | 0.2508 |
| 10 | 2026-01-30 to 2026-03-01 | 18 | 37.4% | 54.3% | 51.7% | 0.2500 | 0.2516 |
| 11 | 2026-03-01 to 2026-03-31 | 1 | 0.0% | n/a | 46.5% | 0.2500 | 0.2500 |
| 12 | 2026-03-31 to 2026-04-30 | 66 | 1.5% | 45.5% | 47.9% | 0.2488 | 0.2499 |
| 13 | 2026-04-30 to 2026-05-30 | 16 | 0.0% | n/a | 48.9% | 0.2489 | 0.2499 |
| 14 | 2026-05-30 to 2026-06-29 | 13 | 0.0% | n/a | 48.6% | 0.2498 | 0.2500 |
| 15 | 2026-06-29 to 2026-07-29 | 27 | 16.5% | 50.4% | 49.0% | 0.2505 | 0.2498 |
| 16 | 2026-07-29 to 2026-08-28 | 14 | 2.1% | 40.0% | 52.2% | 0.2506 | 0.2500 |
| 17 | 2026-08-28 to 2026-09-27 | 42 | 0.0% | n/a | 46.1% | 0.2499 | 0.2498 |
