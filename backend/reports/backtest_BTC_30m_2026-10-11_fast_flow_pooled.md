# Backtest BTC 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8729 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 51.4% | naive 48.2%, reverse 51.8%, always-up 50.4%, always-down 49.6% |
| Flat candles (close equal to the previous close) | 0.1% | |
| Coverage (share of non-neutral calls) | 4.0% | 100% |
| Brier score (lower is better) | 0.2496 | base rate 0.2500 |
| Log loss | 0.6924 | coin flip 0.6931 |
| Up calls: n / precision / recall | 289 / 50.2% / 3.3% | |
| Down calls: n / precision / recall | 57 / 57.9% / 0.8% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 0.32% (-11.16% to 8.93%)
- Accuracy minus the best simple rule: -3.35% (-15.71% to 5.96%)
- Brier improvement over base rate: 0.00038 (-0.00007 to 0.00081)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -30.4% | -30.6% | -11.79 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -46.29 |
| Buy and hold | 27.0% | -29.5% | 1.43 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 3082 | 0.485 | 0.478 |
| 0.5-0.6 | 5645 | 0.521 | 0.518 |
| 0.6-0.7 | 2 | 0.604 | 0.500 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 3.9% | 50.0% | 50.9% | 0.2500 | 0.2501 |
| 49 | 2026-04-17 to 2026-05-01 |  | 6.4% | 62.8% | 48.7% | 0.2484 | 0.2500 |
| 50 | 2026-05-01 to 2026-05-15 |  | 3.9% | 53.8% | 50.7% | 0.2499 | 0.2501 |
| 51 | 2026-05-15 to 2026-05-29 |  | 4.2% | 50.0% | 49.0% | 0.2506 | 0.2500 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.4% | 0.0% | 46.3% | 0.2496 | 0.2498 |
| 53 | 2026-06-12 to 2026-06-26 |  | 0.7% | 60.0% | 48.4% | 0.2496 | 0.2500 |
| 54 | 2026-06-26 to 2026-07-10 |  | 0.4% | 66.7% | 48.8% | 0.2495 | 0.2500 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.0% | n/a | 47.5% | 0.2493 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 0.0% | n/a | 46.9% | 0.2498 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 17.7% | 45.8% | 46.4% | 0.2516 | 0.2500 |
| 58 | 2026-08-21 to 2026-09-04 |  | 0.4% | 33.3% | 46.4% | 0.2488 | 0.2501 |
| 59 | 2026-09-04 to 2026-09-18 |  | 8.5% | 49.1% | 49.2% | 0.2496 | 0.2500 |
| 60 | 2026-09-18 to 2026-10-02 |  | 5.1% | 64.7% | 48.1% | 0.2488 | 0.2502 |
