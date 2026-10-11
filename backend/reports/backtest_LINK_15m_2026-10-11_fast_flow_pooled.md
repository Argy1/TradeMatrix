# Backtest LINK 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 15162 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.8% | naive 48.2%, always-up 50.3%, always-down 49.7% |
| Flat candles (close equal to the previous close) | 6.0% | |
| Coverage (share of non-neutral calls) | 16.8% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2501 |
| Log loss | 0.6921 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1167 / 56.3% / 8.6% | |
| Down calls: n / precision / recall | 1337 / 51.6% / 9.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.60% (3.97% to 9.42%)
- Accuracy minus the best simple rule: 3.64% (1.60% to 5.91%)
- Brier improvement over base rate: 0.00065 (-0.00002 to 0.00129)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -90.4% | -90.4% | -23.13 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -59.24 |
| Buy and hold | 61.3% | -35.2% | 1.96 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.258 | 1.000 |
| 0.3-0.4 | 147 | 0.388 | 0.415 |
| 0.4-0.5 | 7899 | 0.472 | 0.480 |
| 0.5-0.6 | 7096 | 0.527 | 0.530 |
| 0.6-0.7 | 19 | 0.607 | 0.579 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 38.5% | 55.8% | 44.7% | 0.2477 | 0.2503 |
| 52 | 2026-04-26 to 2026-05-10 |  | 8.9% | 55.9% | 45.1% | 0.2484 | 0.2503 |
| 53 | 2026-05-10 to 2026-05-24 |  | 35.6% | 53.7% | 47.7% | 0.2501 | 0.2500 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.7% | 52.9% | 49.7% | 0.2499 | 0.2499 |
| 55 | 2026-06-07 to 2026-06-21 |  | 1.3% | 64.7% | 47.7% | 0.2485 | 0.2499 |
| 56 | 2026-06-21 to 2026-07-05 |  | 24.7% | 54.3% | 46.3% | 0.2490 | 0.2501 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.3% | 50.0% | 48.0% | 0.2492 | 0.2501 |
| 58 | 2026-07-19 to 2026-08-02 |  | 26.0% | 47.8% | 49.4% | 0.2518 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 11.2% | 58.8% | 50.1% | 0.2487 | 0.2501 |
| 60 | 2026-08-16 to 2026-08-30 |  | 35.1% | 53.2% | 49.0% | 0.2507 | 0.2501 |
| 61 | 2026-08-30 to 2026-09-13 |  | 6.0% | 53.1% | 49.1% | 0.2491 | 0.2499 |
| 62 | 2026-09-13 to 2026-09-27 |  | 11.0% | 55.8% | 49.9% | 0.2500 | 0.2501 |
