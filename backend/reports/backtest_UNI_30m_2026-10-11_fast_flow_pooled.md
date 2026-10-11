# Backtest UNI 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8509 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 50.9% | naive 49.0%, always-up 50.1%, always-down 49.9% |
| Flat candles (close equal to the previous close) | 2.6% | |
| Coverage (share of non-neutral calls) | 6.1% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2500 |
| Log loss | 0.6927 | coin flip 0.6931 |
| Up calls: n / precision / recall | 235 / 54.0% / 3.0% | |
| Down calls: n / precision / recall | 286 / 48.3% / 3.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 4.40% (-1.19% to 10.91%)
- Accuracy minus the best simple rule: 1.60% (-3.98% to 8.14%)
- Brier improvement over base rate: 0.00024 (-0.00027 to 0.00071)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -33.0% | -34.3% | -4.39 |
| Naive (hold after an up candle) | -99.8% | -99.8% | -17.41 |
| Buy and hold | 184.5% | -43.5% | 2.68 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 4 | 0.390 | 0.250 |
| 0.4-0.5 | 4313 | 0.479 | 0.482 |
| 0.5-0.6 | 4175 | 0.519 | 0.520 |
| 0.6-0.7 | 17 | 0.624 | 0.588 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 5.4% | 44.4% | 50.8% | 0.2506 | 0.2500 |
| 49 | 2026-04-17 to 2026-05-01 |  | 9.1% | 55.9% | 50.3% | 0.2506 | 0.2500 |
| 50 | 2026-05-01 to 2026-05-15 |  | 7.4% | 55.3% | 51.2% | 0.2495 | 0.2501 |
| 51 | 2026-05-15 to 2026-05-29 |  | 6.5% | 40.0% | 47.1% | 0.2516 | 0.2498 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.0% | n/a | 50.2% | 0.2491 | 0.2500 |
| 53 | 2026-06-12 to 2026-06-26 |  | 5.5% | 37.8% | 48.7% | 0.2508 | 0.2502 |
| 54 | 2026-06-26 to 2026-07-10 |  | 2.5% | 53.3% | 51.4% | 0.2504 | 0.2500 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.7% | 80.0% | 49.7% | 0.2489 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 1.2% | 62.5% | 46.0% | 0.2487 | 0.2499 |
| 57 | 2026-08-07 to 2026-08-21 |  | 19.8% | 51.5% | 48.0% | 0.2493 | 0.2501 |
| 58 | 2026-08-21 to 2026-09-04 |  | 4.3% | 51.7% | 46.2% | 0.2485 | 0.2501 |
| 59 | 2026-09-04 to 2026-09-18 |  | 9.7% | 50.8% | 47.8% | 0.2497 | 0.2500 |
| 60 | 2026-09-18 to 2026-10-02 |  | 7.4% | 56.0% | 49.3% | 0.2494 | 0.2499 |
