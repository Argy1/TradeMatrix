# Backtest ETH 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8728 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.5% | naive 48.2%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 0.1% | |
| Coverage (share of non-neutral calls) | 4.9% | 100% |
| Brier score (lower is better) | 0.2494 | base rate 0.2500 |
| Log loss | 0.6920 | coin flip 0.6931 |
| Up calls: n / precision / recall | 206 / 57.8% / 2.7% | |
| Down calls: n / precision / recall | 221 / 53.4% / 2.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 11.73% (5.33% to 19.75%)
- Accuracy minus the best simple rule: 8.93% (2.88% to 16.81%)
- Brier improvement over base rate: 0.00054 (0.00019 to 0.00092)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -25.3% | -26.0% | -7.80 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -34.80 |
| Buy and hold | 30.8% | -37.9% | 1.31 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 3 | 0.388 | 0.333 |
| 0.4-0.5 | 4008 | 0.481 | 0.481 |
| 0.5-0.6 | 4716 | 0.518 | 0.514 |
| 0.6-0.7 | 1 | 0.624 | 1.000 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 4.2% | 60.7% | 47.2% | 0.2489 | 0.2500 |
| 49 | 2026-04-17 to 2026-05-01 |  | 7.4% | 56.0% | 44.1% | 0.2485 | 0.2500 |
| 50 | 2026-05-01 to 2026-05-15 |  | 5.8% | 53.8% | 50.4% | 0.2497 | 0.2500 |
| 51 | 2026-05-15 to 2026-05-29 |  | 4.2% | 57.1% | 49.0% | 0.2507 | 0.2499 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.4% | 100.0% | 48.7% | 0.2489 | 0.2499 |
| 53 | 2026-06-12 to 2026-06-26 |  | 3.4% | 47.8% | 48.1% | 0.2494 | 0.2498 |
| 54 | 2026-06-26 to 2026-07-10 |  | 1.9% | 46.2% | 49.9% | 0.2500 | 0.2500 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.6% | 75.0% | 47.2% | 0.2497 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 1.5% | 60.0% | 49.1% | 0.2490 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 19.3% | 53.8% | 46.7% | 0.2498 | 0.2500 |
| 58 | 2026-08-21 to 2026-09-04 |  | 4.8% | 62.5% | 46.1% | 0.2482 | 0.2500 |
| 59 | 2026-09-04 to 2026-09-18 |  | 6.4% | 55.8% | 51.5% | 0.2500 | 0.2500 |
| 60 | 2026-09-18 to 2026-10-02 |  | 3.6% | 50.0% | 48.4% | 0.2499 | 0.2501 |
