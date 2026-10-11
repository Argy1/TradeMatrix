# Backtest DOT 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 13689 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.9% | naive 48.0%, reverse 52.0%, always-up 49.7%, always-down 50.3% |
| Flat candles (close equal to the previous close) | 15.1% | |
| Coverage (share of non-neutral calls) | 16.8% | 100% |
| Brier score (lower is better) | 0.2493 | base rate 0.2500 |
| Log loss | 0.6918 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1116 / 53.8% / 8.8% | |
| Down calls: n / precision / recall | 1212 / 54.0% / 9.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.74% (4.50% to 15.64%)
- Accuracy minus the best simple rule: 5.27% (0.39% to 10.78%)
- Brier improvement over base rate: 0.00072 (-0.00002 to 0.00134)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -92.1% | -92.1% | -22.20 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -53.63 |
| Buy and hold | -0.4% | -49.1% | 0.36 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.284 | 0.000 |
| 0.3-0.4 | 121 | 0.385 | 0.405 |
| 0.4-0.5 | 7061 | 0.472 | 0.475 |
| 0.5-0.6 | 6487 | 0.527 | 0.522 |
| 0.6-0.7 | 19 | 0.608 | 0.526 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 36.8% | 55.0% | 49.7% | 0.2499 | 0.2500 |
| 52 | 2026-04-26 to 2026-05-10 |  | 8.9% | 50.0% | 46.9% | 0.2490 | 0.2504 |
| 53 | 2026-05-10 to 2026-05-24 |  | 32.7% | 50.4% | 47.1% | 0.2520 | 0.2500 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.8% | 48.6% | 49.9% | 0.2496 | 0.2499 |
| 55 | 2026-06-07 to 2026-06-21 |  | 1.0% | 72.7% | 45.0% | 0.2485 | 0.2500 |
| 56 | 2026-06-21 to 2026-07-05 |  | 29.9% | 57.6% | 47.5% | 0.2491 | 0.2499 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.4% | 75.0% | 48.6% | 0.2487 | 0.2499 |
| 58 | 2026-07-19 to 2026-08-02 |  | 24.3% | 57.3% | 46.4% | 0.2483 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 10.0% | 51.0% | 46.2% | 0.2480 | 0.2499 |
| 60 | 2026-08-16 to 2026-08-30 |  | 37.9% | 50.1% | 50.7% | 0.2516 | 0.2502 |
| 61 | 2026-08-30 to 2026-09-13 |  | 4.7% | 71.7% | 48.4% | 0.2482 | 0.2501 |
| 62 | 2026-09-13 to 2026-09-27 |  | 12.6% | 52.9% | 49.0% | 0.2484 | 0.2500 |
