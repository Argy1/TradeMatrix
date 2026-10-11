# Backtest BCH 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8279 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.6% | naive 48.3%, reverse 51.7%, always-up 50.3%, always-down 49.7% |
| Flat candles (close equal to the previous close) | 5.2% | |
| Coverage (share of non-neutral calls) | 5.9% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2500 |
| Log loss | 0.6921 | coin flip 0.6931 |
| Up calls: n / precision / recall | 286 / 52.8% / 3.6% | |
| Down calls: n / precision / recall | 210 / 52.4% / 2.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 5.88% (-2.22% to 13.69%)
- Accuracy minus the best simple rule: 1.47% (-5.99% to 8.45%)
- Brier improvement over base rate: 0.00054 (-0.00005 to 0.00116)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -30.6% | -31.5% | -3.57 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -29.68 |
| Buy and hold | -29.4% | -62.5% | -0.53 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 1 | 0.394 | 0.000 |
| 0.4-0.5 | 3835 | 0.480 | 0.476 |
| 0.5-0.6 | 4431 | 0.520 | 0.525 |
| 0.6-0.7 | 12 | 0.617 | 0.667 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 4.0% | 40.7% | 49.8% | 0.2507 | 0.2500 |
| 49 | 2026-04-17 to 2026-05-01 |  | 6.5% | 45.5% | 47.2% | 0.2502 | 0.2498 |
| 50 | 2026-05-01 to 2026-05-15 |  | 5.1% | 63.3% | 45.5% | 0.2486 | 0.2500 |
| 51 | 2026-05-15 to 2026-05-29 |  | 10.4% | 44.1% | 52.0% | 0.2514 | 0.2500 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.6% | 50.0% | 48.3% | 0.2493 | 0.2499 |
| 53 | 2026-06-12 to 2026-06-26 |  | 5.4% | 52.8% | 46.2% | 0.2496 | 0.2501 |
| 54 | 2026-06-26 to 2026-07-10 |  | 3.1% | 23.8% | 48.5% | 0.2505 | 0.2502 |
| 55 | 2026-07-10 to 2026-07-24 |  | 1.0% | 71.4% | 45.9% | 0.2485 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 0.7% | 75.0% | 50.3% | 0.2496 | 0.2501 |
| 57 | 2026-08-07 to 2026-08-21 |  | 18.5% | 54.3% | 51.2% | 0.2495 | 0.2502 |
| 58 | 2026-08-21 to 2026-09-04 |  | 6.0% | 71.1% | 46.5% | 0.2471 | 0.2500 |
| 59 | 2026-09-04 to 2026-09-18 |  | 7.4% | 58.0% | 48.1% | 0.2497 | 0.2498 |
| 60 | 2026-09-18 to 2026-10-02 |  | 7.6% | 54.9% | 48.8% | 0.2483 | 0.2501 |
