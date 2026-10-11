# Backtest BTC 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 16113 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.6% | naive 48.2%, reverse 51.8%, always-up 49.5%, always-down 50.5% |
| Flat candles (close equal to the previous close) | 0.1% | |
| Coverage (share of non-neutral calls) | 9.8% | 100% |
| Brier score (lower is better) | 0.2493 | base rate 0.2500 |
| Log loss | 0.6918 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1021 / 55.8% / 7.1% | |
| Down calls: n / precision / recall | 560 / 52.5% / 3.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 2.26% (-9.92% to 10.16%)
- Accuracy minus the best simple rule: -1.37% (-14.09% to 6.75%)
- Brier improvement over base rate: 0.00066 (0.00038 to 0.00096)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -84.5% | -84.5% | -29.76 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -90.55 |
| Buy and hold | 19.0% | -29.6% | 1.18 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 14 | 0.385 | 0.571 |
| 0.4-0.5 | 7283 | 0.479 | 0.469 |
| 0.5-0.6 | 8813 | 0.524 | 0.516 |
| 0.6-0.7 | 3 | 0.610 | 0.333 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 21.4% | 57.6% | 47.1% | 0.2485 | 0.2502 |
| 52 | 2026-04-26 to 2026-05-10 |  | 0.2% | 66.7% | 47.7% | 0.2489 | 0.2500 |
| 53 | 2026-05-10 to 2026-05-24 |  | 23.7% | 54.2% | 48.1% | 0.2499 | 0.2500 |
| 54 | 2026-05-24 to 2026-06-07 |  | 0.1% | 0.0% | 47.5% | 0.2494 | 0.2496 |
| 55 | 2026-06-07 to 2026-06-21 |  | 0.0% | n/a | 47.3% | 0.2492 | 0.2500 |
| 56 | 2026-06-21 to 2026-07-05 |  | 17.9% | 53.8% | 48.3% | 0.2495 | 0.2499 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.0% | n/a | 47.8% | 0.2490 | 0.2500 |
| 58 | 2026-07-19 to 2026-08-02 |  | 13.2% | 51.4% | 48.4% | 0.2495 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 6.4% | 54.7% | 47.8% | 0.2492 | 0.2500 |
| 60 | 2026-08-16 to 2026-08-30 |  | 22.6% | 53.6% | 50.0% | 0.2503 | 0.2501 |
| 61 | 2026-08-30 to 2026-09-13 |  | 5.7% | 51.3% | 48.1% | 0.2494 | 0.2499 |
| 62 | 2026-09-13 to 2026-09-27 |  | 6.5% | 62.1% | 49.8% | 0.2491 | 0.2500 |
