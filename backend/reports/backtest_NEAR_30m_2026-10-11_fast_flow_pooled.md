# Backtest NEAR 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8347 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.5% | naive 48.0%, always-up 50.4%, always-down 49.6% |
| Flat candles (close equal to the previous close) | 4.5% | |
| Coverage (share of non-neutral calls) | 6.4% | 100% |
| Brier score (lower is better) | 0.2499 | base rate 0.2500 |
| Log loss | 0.6929 | coin flip 0.6931 |
| Up calls: n / precision / recall | 223 / 56.1% / 3.0% | |
| Down calls: n / precision / recall | 308 / 51.6% / 3.8% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.52% (2.34% to 10.72%)
- Accuracy minus the best simple rule: 3.11% (-1.01% to 7.02%)
- Brier improvement over base rate: 0.00015 (-0.00042 to 0.00066)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -19.8% | -25.1% | -1.76 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -17.47 |
| Buy and hold | 298.3% | -49.5% | 3.03 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 5 | 0.392 | 0.800 |
| 0.4-0.5 | 4151 | 0.479 | 0.486 |
| 0.5-0.6 | 4180 | 0.520 | 0.521 |
| 0.6-0.7 | 11 | 0.609 | 0.909 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 7.9% | 46.8% | 48.8% | 0.2510 | 0.2501 |
| 49 | 2026-04-17 to 2026-05-01 |  | 10.1% | 51.7% | 48.8% | 0.2505 | 0.2500 |
| 50 | 2026-05-01 to 2026-05-15 |  | 10.1% | 64.1% | 48.5% | 0.2489 | 0.2501 |
| 51 | 2026-05-15 to 2026-05-29 |  | 3.7% | 41.7% | 47.3% | 0.2499 | 0.2501 |
| 52 | 2026-05-29 to 2026-06-12 |  | 2.7% | 55.6% | 48.1% | 0.2501 | 0.2498 |
| 53 | 2026-06-12 to 2026-06-26 |  | 4.8% | 48.4% | 47.6% | 0.2500 | 0.2499 |
| 54 | 2026-06-26 to 2026-07-10 |  | 2.5% | 64.7% | 48.4% | 0.2486 | 0.2499 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.7% | 50.0% | 47.2% | 0.2497 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 0.9% | 60.0% | 44.8% | 0.2493 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 18.5% | 45.5% | 50.5% | 0.2525 | 0.2501 |
| 58 | 2026-08-21 to 2026-09-04 |  | 5.7% | 60.5% | 44.9% | 0.2485 | 0.2501 |
| 59 | 2026-09-04 to 2026-09-18 |  | 7.6% | 57.1% | 49.2% | 0.2494 | 0.2501 |
| 60 | 2026-09-18 to 2026-10-02 |  | 7.9% | 62.3% | 49.5% | 0.2498 | 0.2500 |
