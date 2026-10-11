# Backtest DOGE 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 15733 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.2% | naive 47.7%, reverse 52.3%, always-up 50.4%, always-down 49.6% |
| Flat candles (close equal to the previous close) | 2.4% | |
| Coverage (share of non-neutral calls) | 15.4% | 100% |
| Brier score (lower is better) | 0.2493 | base rate 0.2501 |
| Log loss | 0.6917 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1166 / 56.3% / 8.3% | |
| Down calls: n / precision / recall | 1273 / 54.2% / 8.8% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.90% (4.37% to 11.16%)
- Accuracy minus the best simple rule: 3.28% (-0.83% to 6.55%)
- Brier improvement over base rate: 0.00080 (0.00026 to 0.00136)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -90.4% | -90.5% | -24.18 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -59.70 |
| Buy and hold | 6.5% | -42.2% | 0.53 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.273 | 1.000 |
| 0.3-0.4 | 133 | 0.387 | 0.474 |
| 0.4-0.5 | 7980 | 0.473 | 0.480 |
| 0.5-0.6 | 7603 | 0.526 | 0.528 |
| 0.6-0.7 | 16 | 0.613 | 0.562 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 36.4% | 56.3% | 49.0% | 0.2493 | 0.2501 |
| 52 | 2026-04-26 to 2026-05-10 |  | 8.6% | 57.4% | 44.9% | 0.2477 | 0.2502 |
| 53 | 2026-05-10 to 2026-05-24 |  | 30.1% | 51.5% | 49.2% | 0.2509 | 0.2500 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.5% | 58.8% | 47.7% | 0.2495 | 0.2499 |
| 55 | 2026-06-07 to 2026-06-21 |  | 1.2% | 56.2% | 46.1% | 0.2493 | 0.2501 |
| 56 | 2026-06-21 to 2026-07-05 |  | 24.5% | 53.2% | 48.3% | 0.2500 | 0.2500 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.4% | 40.0% | 45.0% | 0.2482 | 0.2500 |
| 58 | 2026-07-19 to 2026-08-02 |  | 22.3% | 55.8% | 48.9% | 0.2496 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 8.0% | 60.4% | 47.5% | 0.2483 | 0.2501 |
| 60 | 2026-08-16 to 2026-08-30 |  | 32.1% | 53.3% | 50.3% | 0.2506 | 0.2501 |
| 61 | 2026-08-30 to 2026-09-13 |  | 6.4% | 66.7% | 47.4% | 0.2481 | 0.2501 |
| 62 | 2026-09-13 to 2026-09-27 |  | 11.7% | 58.1% | 48.7% | 0.2495 | 0.2501 |
