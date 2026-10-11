# Backtest ADA 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8280 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.8% | naive 48.6%, always-up 49.0%, always-down 51.0% |
| Flat candles (close equal to the previous close) | 5.2% | |
| Coverage (share of non-neutral calls) | 5.1% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2499 |
| Log loss | 0.6921 | coin flip 0.6931 |
| Up calls: n / precision / recall | 169 / 52.7% / 2.2% | |
| Down calls: n / precision / recall | 255 / 52.9% / 3.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 5.55% (-1.25% to 11.93%)
- Accuracy minus the best simple rule: 2.52% (-3.87% to 8.57%)
- Brier improvement over base rate: 0.00048 (0.00011 to 0.00086)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -23.0% | -23.5% | -3.58 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -24.49 |
| Buy and hold | 1.5% | -51.7% | 0.41 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 3 | 0.398 | 0.667 |
| 0.4-0.5 | 4061 | 0.480 | 0.465 |
| 0.5-0.6 | 4211 | 0.518 | 0.512 |
| 0.6-0.7 | 5 | 0.619 | 0.800 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 4.2% | 57.7% | 49.7% | 0.2487 | 0.2499 |
| 49 | 2026-04-17 to 2026-05-01 |  | 9.1% | 50.0% | 48.4% | 0.2497 | 0.2499 |
| 50 | 2026-05-01 to 2026-05-15 |  | 6.0% | 62.2% | 48.7% | 0.2484 | 0.2500 |
| 51 | 2026-05-15 to 2026-05-29 |  | 2.7% | 58.8% | 46.2% | 0.2492 | 0.2498 |
| 52 | 2026-05-29 to 2026-06-12 |  | 2.1% | 28.6% | 51.1% | 0.2506 | 0.2499 |
| 53 | 2026-06-12 to 2026-06-26 |  | 4.3% | 48.1% | 49.5% | 0.2497 | 0.2498 |
| 54 | 2026-06-26 to 2026-07-10 |  | 2.2% | 46.7% | 51.7% | 0.2493 | 0.2499 |
| 55 | 2026-07-10 to 2026-07-24 |  | 1.5% | 66.7% | 48.0% | 0.2500 | 0.2499 |
| 56 | 2026-07-24 to 2026-08-07 |  | 1.0% | 71.4% | 49.1% | 0.2496 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 14.6% | 47.8% | 45.4% | 0.2502 | 0.2499 |
| 58 | 2026-08-21 to 2026-09-04 |  | 6.2% | 47.6% | 47.0% | 0.2490 | 0.2500 |
| 59 | 2026-09-04 to 2026-09-18 |  | 7.0% | 68.9% | 47.2% | 0.2486 | 0.2500 |
| 60 | 2026-09-18 to 2026-10-02 |  | 5.5% | 48.6% | 48.9% | 0.2501 | 0.2500 |
