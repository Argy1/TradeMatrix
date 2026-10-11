# Backtest NEAR 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 15097 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.9% | naive 48.7%, reverse 51.3%, always-up 50.3%, always-down 49.7% |
| Flat candles (close equal to the previous close) | 6.4% | |
| Coverage (share of non-neutral calls) | 17.3% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2501 |
| Log loss | 0.6927 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1167 / 55.0% / 8.5% | |
| Down calls: n / precision / recall | 1433 / 53.0% / 10.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.74% (4.25% to 18.67%)
- Accuracy minus the best simple rule: 6.53% (1.14% to 14.94%)
- Brier improvement over base rate: 0.00029 (-0.00031 to 0.00082)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -87.8% | -88.1% | -14.66 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -32.08 |
| Buy and hold | 288.3% | -49.5% | 3.15 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.270 | 0.000 |
| 0.3-0.4 | 139 | 0.387 | 0.532 |
| 0.4-0.5 | 8393 | 0.471 | 0.489 |
| 0.5-0.6 | 6542 | 0.528 | 0.519 |
| 0.6-0.7 | 22 | 0.608 | 0.591 |

## Most useful features (average gain)

- dist_ema9: 148.33
- log_ret_1: 106.96
- ret_1: 105.80
- stoch_k: 71.16
- dist_ema21: 47.48
- btc_ret_1: 45.09
- ret_6: 40.41
- rsi14: 35.17

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51 | 2026-04-12 to 2026-04-26 |  | 39.6% | 52.5% | 48.7% | 0.2505 | 0.2500 |
| 52 | 2026-04-26 to 2026-05-10 |  | 7.5% | 56.4% | 47.6% | 0.2487 | 0.2503 |
| 53 | 2026-05-10 to 2026-05-24 |  | 26.3% | 49.7% | 50.3% | 0.2523 | 0.2504 |
| 54 | 2026-05-24 to 2026-06-07 |  | 1.6% | 60.0% | 49.9% | 0.2501 | 0.2500 |
| 55 | 2026-06-07 to 2026-06-21 |  | 1.3% | 50.0% | 45.9% | 0.2498 | 0.2500 |
| 56 | 2026-06-21 to 2026-07-05 |  | 34.4% | 54.0% | 48.0% | 0.2499 | 0.2499 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.1% | 100.0% | 46.8% | 0.2487 | 0.2500 |
| 58 | 2026-07-19 to 2026-08-02 |  | 27.6% | 57.5% | 47.8% | 0.2491 | 0.2499 |
| 59 | 2026-08-02 to 2026-08-16 |  | 12.9% | 58.3% | 51.0% | 0.2488 | 0.2500 |
| 60 | 2026-08-16 to 2026-08-30 |  | 37.4% | 52.1% | 50.1% | 0.2507 | 0.2501 |
| 61 | 2026-08-30 to 2026-09-13 |  | 4.8% | 51.7% | 49.1% | 0.2501 | 0.2500 |
| 62 | 2026-09-13 to 2026-09-27 |  | 14.0% | 58.5% | 48.6% | 0.2487 | 0.2501 |
