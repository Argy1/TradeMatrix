# Backtest DOGE 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8605 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.2% | naive 47.6%, reverse 52.4%, always-up 50.1%, always-down 49.9% |
| Flat candles (close equal to the previous close) | 1.5% | |
| Coverage (share of non-neutral calls) | 5.4% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2500 |
| Log loss | 0.6922 | coin flip 0.6931 |
| Up calls: n / precision / recall | 165 / 55.2% / 2.1% | |
| Down calls: n / precision / recall | 302 / 53.6% / 3.8% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.29% (-7.17% to 11.76%)
- Accuracy minus the best simple rule: -2.00% (-12.32% to 6.22%)
- Brier improvement over base rate: 0.00049 (-0.00006 to 0.00105)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -22.1% | -23.5% | -5.39 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -29.80 |
| Buy and hold | 3.3% | -42.1% | 0.41 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 2 | 0.388 | 0.000 |
| 0.4-0.5 | 4288 | 0.479 | 0.479 |
| 0.5-0.6 | 4312 | 0.518 | 0.524 |
| 0.6-0.7 | 3 | 0.622 | 0.667 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 4.9% | 48.5% | 49.6% | 0.2507 | 0.2500 |
| 49 | 2026-04-17 to 2026-05-01 |  | 10.3% | 58.0% | 47.0% | 0.2502 | 0.2501 |
| 50 | 2026-05-01 to 2026-05-15 |  | 8.2% | 60.4% | 46.5% | 0.2487 | 0.2500 |
| 51 | 2026-05-15 to 2026-05-29 |  | 2.7% | 41.2% | 49.8% | 0.2500 | 0.2498 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.1% | 0.0% | 46.4% | 0.2485 | 0.2502 |
| 53 | 2026-06-12 to 2026-06-26 |  | 5.2% | 42.9% | 48.6% | 0.2487 | 0.2499 |
| 54 | 2026-06-26 to 2026-07-10 |  | 2.2% | 66.7% | 50.0% | 0.2498 | 0.2499 |
| 55 | 2026-07-10 to 2026-07-24 |  | 1.0% | 42.9% | 44.3% | 0.2491 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 1.3% | 77.8% | 44.5% | 0.2486 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 16.4% | 49.1% | 46.0% | 0.2510 | 0.2500 |
| 58 | 2026-08-21 to 2026-09-04 |  | 6.2% | 61.9% | 46.4% | 0.2476 | 0.2501 |
| 59 | 2026-09-04 to 2026-09-18 |  | 6.5% | 59.1% | 51.1% | 0.2506 | 0.2501 |
| 60 | 2026-09-18 to 2026-10-02 |  | 5.1% | 52.9% | 48.1% | 0.2502 | 0.2501 |
