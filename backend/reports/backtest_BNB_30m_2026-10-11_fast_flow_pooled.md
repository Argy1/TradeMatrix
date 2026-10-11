# Backtest BNB 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8707 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.5% | naive 48.6%, always-up 51.0%, always-down 49.0% |
| Flat candles (close equal to the previous close) | 0.3% | |
| Coverage (share of non-neutral calls) | 4.2% | 100% |
| Brier score (lower is better) | 0.2497 | base rate 0.2501 |
| Log loss | 0.6925 | coin flip 0.6931 |
| Up calls: n / precision / recall | 186 / 51.1% / 2.1% | |
| Down calls: n / precision / recall | 176 / 54.0% / 2.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.70% (-0.45% to 19.28%)
- Accuracy minus the best simple rule: 5.60% (-3.85% to 16.81%)
- Brier improvement over base rate: 0.00039 (-0.00041 to 0.00097)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -27.1% | -27.4% | -10.55 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -44.71 |
| Buy and hold | 31.2% | -26.8% | 1.59 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 3 | 0.391 | 0.667 |
| 0.4-0.5 | 3847 | 0.482 | 0.489 |
| 0.5-0.6 | 4857 | 0.518 | 0.527 |

## Most useful features (average gain)

- dist_ema9: 44.72
- ret_3: 41.67
- log_ret_1: 35.31
- ret_1: 33.70
- ret_6: 32.26
- hour_cos: 30.26
- hour_sin: 29.33
- btc_ret_1: 28.99

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 48 | 2026-04-03 to 2026-04-17 |  | 3.1% | 61.9% | 52.6% | 0.2495 | 0.2501 |
| 49 | 2026-04-17 to 2026-05-01 |  | 4.9% | 75.8% | 48.1% | 0.2483 | 0.2501 |
| 50 | 2026-05-01 to 2026-05-15 |  | 5.2% | 55.9% | 49.2% | 0.2495 | 0.2502 |
| 51 | 2026-05-15 to 2026-05-29 |  | 1.9% | 46.2% | 48.7% | 0.2501 | 0.2499 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.0% | n/a | 48.7% | 0.2500 | 0.2500 |
| 53 | 2026-06-12 to 2026-06-26 |  | 4.2% | 35.7% | 47.4% | 0.2500 | 0.2501 |
| 54 | 2026-06-26 to 2026-07-10 |  | 2.7% | 72.2% | 47.7% | 0.2483 | 0.2500 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.1% | 100.0% | 50.7% | 0.2494 | 0.2499 |
| 56 | 2026-07-24 to 2026-08-07 |  | 0.4% | 33.3% | 46.6% | 0.2494 | 0.2501 |
| 57 | 2026-08-07 to 2026-08-21 |  | 15.9% | 40.2% | 46.7% | 0.2536 | 0.2500 |
| 58 | 2026-08-21 to 2026-09-04 |  | 4.9% | 60.6% | 46.9% | 0.2486 | 0.2500 |
| 59 | 2026-09-04 to 2026-09-18 |  | 7.0% | 59.6% | 48.8% | 0.2491 | 0.2502 |
| 60 | 2026-09-18 to 2026-10-02 |  | 3.7% | 45.8% | 49.4% | 0.2499 | 0.2501 |
