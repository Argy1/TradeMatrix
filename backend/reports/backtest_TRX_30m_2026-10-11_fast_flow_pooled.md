# Backtest TRX 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 7503 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 51.2% | naive 49.8%, always-up 52.1%, always-down 47.9% |
| Flat candles (close equal to the previous close) | 14.1% | |
| Coverage (share of non-neutral calls) | 5.6% | 100% |
| Brier score (lower is better) | 0.2501 | base rate 0.2501 |
| Log loss | 0.6934 | coin flip 0.6931 |
| Up calls: n / precision / recall | 402 / 51.0% / 5.2% | |
| Down calls: n / precision / recall | 14 / 57.1% / 0.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 0.34% (-14.02% to 12.27%)
- Accuracy minus the best simple rule: -2.63% (-17.34% to 8.95%)
- Brier improvement over base rate: 0.00003 (-0.00065 to 0.00066)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -52.1% | -52.1% | -25.13 |
| Naive (hold after an up candle) | -99.8% | -99.8% | -78.40 |
| Buy and hold | 6.6% | -17.1% | 0.80 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 1877 | 0.488 | 0.526 |
| 0.5-0.6 | 5623 | 0.523 | 0.519 |
| 0.6-0.7 | 3 | 0.615 | 0.333 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 0.7% | 80.0% | 49.1% | 0.2492 | 0.2502 |
| 49 | 2026-04-17 to 2026-05-01 |  | 5.5% | 52.8% | 50.6% | 0.2500 | 0.2501 |
| 50 | 2026-05-01 to 2026-05-15 |  | 2.8% | 52.6% | 53.7% | 0.2507 | 0.2502 |
| 51 | 2026-05-15 to 2026-05-29 |  | 1.3% | 71.4% | 53.0% | 0.2503 | 0.2502 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.0% | n/a | 49.5% | 0.2502 | 0.2499 |
| 53 | 2026-06-12 to 2026-06-26 |  | 0.0% | n/a | 49.1% | 0.2491 | 0.2506 |
| 54 | 2026-06-26 to 2026-07-10 |  | 0.4% | 0.0% | 47.0% | 0.2503 | 0.2502 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.0% | n/a | 44.5% | 0.2489 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 0.0% | n/a | 49.3% | 0.2500 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 28.1% | 52.6% | 44.7% | 0.2502 | 0.2501 |
| 58 | 2026-08-21 to 2026-09-04 |  | 1.9% | 50.0% | 52.9% | 0.2519 | 0.2499 |
| 59 | 2026-09-04 to 2026-09-18 |  | 15.0% | 51.2% | 49.8% | 0.2483 | 0.2504 |
| 60 | 2026-09-18 to 2026-10-02 |  | 17.1% | 46.9% | 53.6% | 0.2524 | 0.2499 |
