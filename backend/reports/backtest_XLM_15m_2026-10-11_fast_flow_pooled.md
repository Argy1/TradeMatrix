# Backtest XLM 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 14706 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.1% | naive 49.0%, always-up 48.7%, always-down 51.3% |
| Flat candles (close equal to the previous close) | 8.8% | |
| Coverage (share of non-neutral calls) | 17.1% | 100% |
| Brier score (lower is better) | 0.2501 | base rate 0.2499 |
| Log loss | 0.6933 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1165 / 52.7% / 8.6% | |
| Down calls: n / precision / recall | 1318 / 53.5% / 9.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 2.77% (-7.68% to 9.84%)
- Accuracy minus the best simple rule: -0.29% (-11.11% to 7.09%)
- Brier improvement over base rate: -0.00020 (-0.00122 to 0.00071)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -92.9% | -92.9% | -21.88 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -39.50 |
| Buy and hold | 41.9% | -48.0% | 1.30 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.271 | 0.000 |
| 0.3-0.4 | 161 | 0.385 | 0.478 |
| 0.4-0.5 | 7726 | 0.472 | 0.470 |
| 0.5-0.6 | 6799 | 0.528 | 0.507 |
| 0.6-0.7 | 19 | 0.608 | 0.421 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 36.9% | 51.9% | 48.8% | 0.2516 | 0.2499 |
| 52 | 2026-04-26 to 2026-05-10 |  | 7.2% | 51.8% | 47.9% | 0.2489 | 0.2498 |
| 53 | 2026-05-10 to 2026-05-24 |  | 33.5% | 52.8% | 50.3% | 0.2520 | 0.2495 |
| 54 | 2026-05-24 to 2026-06-07 |  | 1.6% | 63.6% | 50.2% | 0.2500 | 0.2499 |
| 55 | 2026-06-07 to 2026-06-21 |  | 1.0% | 57.1% | 48.4% | 0.2485 | 0.2497 |
| 56 | 2026-06-21 to 2026-07-05 |  | 33.0% | 51.7% | 50.1% | 0.2510 | 0.2498 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.1% | 0.0% | 46.4% | 0.2485 | 0.2499 |
| 58 | 2026-07-19 to 2026-08-02 |  | 25.4% | 55.7% | 48.1% | 0.2492 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 10.0% | 62.7% | 49.5% | 0.2485 | 0.2497 |
| 60 | 2026-08-16 to 2026-08-30 |  | 38.8% | 48.8% | 50.0% | 0.2540 | 0.2501 |
| 61 | 2026-08-30 to 2026-09-13 |  | 3.9% | 68.8% | 48.6% | 0.2483 | 0.2501 |
| 62 | 2026-09-13 to 2026-09-27 |  | 13.5% | 56.5% | 49.8% | 0.2506 | 0.2502 |
