# Backtest ETH 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 16101 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.6% | naive 47.8%, reverse 52.2%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 0.2% | |
| Coverage (share of non-neutral calls) | 14.4% | 100% |
| Brier score (lower is better) | 0.2485 | base rate 0.2500 |
| Log loss | 0.6902 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1181 / 58.3% / 8.6% | |
| Down calls: n / precision / recall | 1126 / 54.8% / 7.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.17% (2.37% to 13.96%)
- Accuracy minus the best simple rule: 3.65% (-1.90% to 8.84%)
- Brier improvement over base rate: 0.00147 (0.00090 to 0.00205)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -90.7% | -90.7% | -28.32 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -70.69 |
| Buy and hold | 22.9% | -38.2% | 1.14 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.265 | 0.000 |
| 0.3-0.4 | 124 | 0.389 | 0.403 |
| 0.4-0.5 | 7735 | 0.474 | 0.464 |
| 0.5-0.6 | 8217 | 0.526 | 0.532 |
| 0.6-0.7 | 24 | 0.610 | 0.542 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 35.2% | 56.1% | 48.6% | 0.2483 | 0.2501 |
| 52 | 2026-04-26 to 2026-05-10 |  | 7.2% | 60.8% | 45.4% | 0.2480 | 0.2499 |
| 53 | 2026-05-10 to 2026-05-24 |  | 31.9% | 52.2% | 49.4% | 0.2500 | 0.2499 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.7% | 55.6% | 47.9% | 0.2492 | 0.2497 |
| 55 | 2026-06-07 to 2026-06-21 |  | 0.7% | 33.3% | 46.9% | 0.2487 | 0.2499 |
| 56 | 2026-06-21 to 2026-07-05 |  | 21.0% | 55.3% | 45.7% | 0.2480 | 0.2500 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.1% | 50.0% | 46.8% | 0.2480 | 0.2500 |
| 58 | 2026-07-19 to 2026-08-02 |  | 21.4% | 52.5% | 50.8% | 0.2502 | 0.2501 |
| 59 | 2026-08-02 to 2026-08-16 |  | 8.7% | 77.8% | 45.3% | 0.2464 | 0.2501 |
| 60 | 2026-08-16 to 2026-08-30 |  | 28.6% | 56.8% | 49.2% | 0.2486 | 0.2501 |
| 61 | 2026-08-30 to 2026-09-13 |  | 6.0% | 61.3% | 49.1% | 0.2490 | 0.2501 |
| 62 | 2026-09-13 to 2026-09-27 |  | 8.9% | 60.5% | 49.0% | 0.2479 | 0.2500 |
