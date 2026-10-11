# Backtest SOL 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 15718 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.7% | naive 48.7%, always-up 50.3%, always-down 49.7% |
| Flat candles (close equal to the previous close) | 2.5% | |
| Coverage (share of non-neutral calls) | 15.9% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2501 |
| Log loss | 0.6922 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1234 / 54.8% / 8.6% | |
| Down calls: n / precision / recall | 1270 / 52.7% / 8.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 4.04% (-2.43% to 8.46%)
- Accuracy minus the best simple rule: 1.38% (-5.24% to 5.95%)
- Brier improvement over base rate: 0.00052 (-0.00005 to 0.00102)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -91.1% | -91.1% | -26.43 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -61.16 |
| Buy and hold | 48.7% | -38.3% | 1.77 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.264 | 1.000 |
| 0.3-0.4 | 121 | 0.388 | 0.446 |
| 0.4-0.5 | 7883 | 0.472 | 0.485 |
| 0.5-0.6 | 7698 | 0.527 | 0.521 |
| 0.6-0.7 | 15 | 0.607 | 0.667 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 36.7% | 53.5% | 48.4% | 0.2492 | 0.2502 |
| 52 | 2026-04-26 to 2026-05-10 |  | 7.0% | 55.2% | 49.6% | 0.2486 | 0.2504 |
| 53 | 2026-05-10 to 2026-05-24 |  | 33.3% | 52.1% | 48.9% | 0.2503 | 0.2498 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.6% | 62.9% | 49.4% | 0.2495 | 0.2497 |
| 55 | 2026-06-07 to 2026-06-21 |  | 1.0% | 53.8% | 47.4% | 0.2497 | 0.2502 |
| 56 | 2026-06-21 to 2026-07-05 |  | 27.2% | 54.4% | 48.2% | 0.2496 | 0.2500 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.4% | 20.0% | 46.8% | 0.2485 | 0.2500 |
| 58 | 2026-07-19 to 2026-08-02 |  | 22.1% | 54.2% | 50.2% | 0.2498 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 9.6% | 59.2% | 47.1% | 0.2488 | 0.2499 |
| 60 | 2026-08-16 to 2026-08-30 |  | 34.0% | 50.4% | 48.6% | 0.2520 | 0.2502 |
| 61 | 2026-08-30 to 2026-09-13 |  | 6.4% | 60.7% | 49.4% | 0.2486 | 0.2500 |
| 62 | 2026-09-13 to 2026-09-27 |  | 10.3% | 56.2% | 50.1% | 0.2498 | 0.2501 |
