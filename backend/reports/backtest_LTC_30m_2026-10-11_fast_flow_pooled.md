# Backtest LTC 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8439 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.9% | naive 48.4%, reverse 51.6%, always-up 51.4%, always-down 48.6% |
| Flat candles (close equal to the previous close) | 3.4% | |
| Coverage (share of non-neutral calls) | 4.5% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2501 |
| Log loss | 0.6921 | coin flip 0.6931 |
| Up calls: n / precision / recall | 134 / 64.2% / 2.0% | |
| Down calls: n / precision / recall | 245 / 51.4% / 3.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 11.90% (4.06% to 20.53%)
- Accuracy minus the best simple rule: 7.87% (0.00% to 16.93%)
- Brier improvement over base rate: 0.00062 (0.00000 to 0.00116)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -14.7% | -16.0% | -4.23 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -35.33 |
| Buy and hold | 31.2% | -34.7% | 1.28 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 2 | 0.387 | 0.000 |
| 0.4-0.5 | 4192 | 0.480 | 0.491 |
| 0.5-0.6 | 4243 | 0.517 | 0.537 |
| 0.6-0.7 | 2 | 0.620 | 1.000 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 4.3% | 57.1% | 50.9% | 0.2498 | 0.2500 |
| 49 | 2026-04-17 to 2026-05-01 |  | 6.0% | 45.0% | 47.0% | 0.2497 | 0.2501 |
| 50 | 2026-05-01 to 2026-05-15 |  | 5.5% | 61.1% | 47.9% | 0.2486 | 0.2502 |
| 51 | 2026-05-15 to 2026-05-29 |  | 2.4% | 37.5% | 48.7% | 0.2493 | 0.2501 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.3% | 100.0% | 52.1% | 0.2488 | 0.2500 |
| 53 | 2026-06-12 to 2026-06-26 |  | 5.5% | 52.8% | 47.7% | 0.2501 | 0.2501 |
| 54 | 2026-06-26 to 2026-07-10 |  | 3.4% | 42.9% | 48.8% | 0.2514 | 0.2502 |
| 55 | 2026-07-10 to 2026-07-24 |  | 1.0% | 57.1% | 49.3% | 0.2491 | 0.2501 |
| 56 | 2026-07-24 to 2026-08-07 |  | 0.6% | 75.0% | 47.5% | 0.2479 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 14.9% | 53.3% | 47.2% | 0.2519 | 0.2501 |
| 58 | 2026-08-21 to 2026-09-04 |  | 5.5% | 62.2% | 48.0% | 0.2488 | 0.2501 |
| 59 | 2026-09-04 to 2026-09-18 |  | 6.1% | 65.0% | 47.8% | 0.2489 | 0.2500 |
| 60 | 2026-09-18 to 2026-10-02 |  | 3.0% | 75.0% | 46.2% | 0.2485 | 0.2502 |
