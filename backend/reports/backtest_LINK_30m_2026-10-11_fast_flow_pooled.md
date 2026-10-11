# Backtest LINK 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8303 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.2% | naive 48.8%, reverse 51.2%, always-up 50.4%, always-down 49.6% |
| Flat candles (close equal to the previous close) | 5.0% | |
| Coverage (share of non-neutral calls) | 5.0% | 100% |
| Brier score (lower is better) | 0.2496 | base rate 0.2500 |
| Log loss | 0.6923 | coin flip 0.6931 |
| Up calls: n / precision / recall | 131 / 55.0% / 1.7% | |
| Down calls: n / precision / recall | 277 / 52.3% / 3.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.93% (1.23% to 13.22%)
- Accuracy minus the best simple rule: 3.74% (-1.85% to 9.83%)
- Brier improvement over base rate: 0.00045 (0.00003 to 0.00083)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -19.2% | -20.5% | -5.07 |
| Naive (hold after an up candle) | -99.8% | -99.8% | -27.17 |
| Buy and hold | 62.8% | -35.1% | 1.86 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 4 | 0.392 | 0.250 |
| 0.4-0.5 | 4283 | 0.479 | 0.483 |
| 0.5-0.6 | 4012 | 0.517 | 0.527 |
| 0.6-0.7 | 4 | 0.617 | 1.000 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 6.0% | 59.5% | 47.6% | 0.2490 | 0.2500 |
| 49 | 2026-04-17 to 2026-05-01 |  | 7.6% | 62.5% | 46.8% | 0.2487 | 0.2499 |
| 50 | 2026-05-01 to 2026-05-15 |  | 9.1% | 56.4% | 49.6% | 0.2494 | 0.2501 |
| 51 | 2026-05-15 to 2026-05-29 |  | 4.6% | 39.3% | 48.7% | 0.2510 | 0.2498 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.0% | n/a | 50.8% | 0.2486 | 0.2501 |
| 53 | 2026-06-12 to 2026-06-26 |  | 5.7% | 41.7% | 48.8% | 0.2498 | 0.2500 |
| 54 | 2026-06-26 to 2026-07-10 |  | 3.1% | 52.4% | 49.1% | 0.2496 | 0.2500 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.9% | 80.0% | 48.1% | 0.2494 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 1.6% | 63.6% | 49.3% | 0.2491 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 10.1% | 50.0% | 48.6% | 0.2498 | 0.2501 |
| 58 | 2026-08-21 to 2026-09-04 |  | 5.5% | 54.3% | 47.2% | 0.2495 | 0.2501 |
| 59 | 2026-09-04 to 2026-09-18 |  | 6.7% | 51.1% | 50.0% | 0.2510 | 0.2501 |
| 60 | 2026-09-18 to 2026-10-02 |  | 4.0% | 55.6% | 49.3% | 0.2498 | 0.2501 |
