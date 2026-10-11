# Backtest XRP 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8618 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.7% | naive 49.4%, reverse 50.6%, always-up 49.5%, always-down 50.5% |
| Flat candles (close equal to the previous close) | 1.4% | |
| Coverage (share of non-neutral calls) | 4.9% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2500 |
| Log loss | 0.6927 | coin flip 0.6931 |
| Up calls: n / precision / recall | 194 / 57.7% / 2.6% | |
| Down calls: n / precision / recall | 230 / 53.9% / 2.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 5.54% (-1.70% to 12.10%)
- Accuracy minus the best simple rule: 2.86% (-4.18% to 9.49%)
- Brier improvement over base rate: 0.00019 (-0.00030 to 0.00066)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -26.1% | -26.7% | -4.70 |
| Naive (hold after an up candle) | -99.8% | -99.8% | -28.32 |
| Buy and hold | 13.5% | -35.6% | 0.72 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 3982 | 0.480 | 0.480 |
| 0.5-0.6 | 4630 | 0.518 | 0.508 |
| 0.6-0.7 | 6 | 0.625 | 0.333 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 4.2% | 51.9% | 49.6% | 0.2500 | 0.2501 |
| 49 | 2026-04-17 to 2026-05-01 |  | 6.8% | 67.4% | 49.5% | 0.2495 | 0.2499 |
| 50 | 2026-05-01 to 2026-05-15 |  | 5.8% | 63.2% | 50.8% | 0.2495 | 0.2500 |
| 51 | 2026-05-15 to 2026-05-29 |  | 3.0% | 30.0% | 53.0% | 0.2512 | 0.2498 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.0% | n/a | 49.7% | 0.2490 | 0.2499 |
| 53 | 2026-06-12 to 2026-06-26 |  | 4.6% | 54.8% | 48.7% | 0.2489 | 0.2499 |
| 54 | 2026-06-26 to 2026-07-10 |  | 3.3% | 50.0% | 51.1% | 0.2501 | 0.2500 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.7% | 40.0% | 46.9% | 0.2494 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 1.0% | 71.4% | 48.6% | 0.2488 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 17.0% | 52.7% | 48.6% | 0.2510 | 0.2500 |
| 58 | 2026-08-21 to 2026-09-04 |  | 5.5% | 48.6% | 47.8% | 0.2487 | 0.2501 |
| 59 | 2026-09-04 to 2026-09-18 |  | 8.3% | 58.9% | 47.4% | 0.2512 | 0.2499 |
| 60 | 2026-09-18 to 2026-10-02 |  | 3.7% | 69.6% | 50.2% | 0.2498 | 0.2501 |
