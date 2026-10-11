# Backtest XRP 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 15825 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.4% | naive 49.2%, reverse 50.8%, always-up 49.4%, always-down 50.6% |
| Flat candles (close equal to the previous close) | 1.9% | |
| Coverage (share of non-neutral calls) | 15.3% | 100% |
| Brier score (lower is better) | 0.2497 | base rate 0.2500 |
| Log loss | 0.6926 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1285 / 54.4% / 8.9% | |
| Down calls: n / precision / recall | 1137 / 54.4% / 7.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 4.95% (-1.26% to 9.61%)
- Accuracy minus the best simple rule: 2.62% (-3.56% to 6.97%)
- Brier improvement over base rate: 0.00025 (-0.00017 to 0.00068)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -92.3% | -92.3% | -27.21 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -57.73 |
| Buy and hold | 14.1% | -35.8% | 0.78 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.287 | 0.000 |
| 0.3-0.4 | 126 | 0.385 | 0.484 |
| 0.4-0.5 | 7606 | 0.473 | 0.474 |
| 0.5-0.6 | 8080 | 0.527 | 0.513 |
| 0.6-0.7 | 12 | 0.608 | 0.500 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 34.6% | 54.5% | 48.3% | 0.2496 | 0.2501 |
| 52 | 2026-04-26 to 2026-05-10 |  | 6.3% | 61.4% | 47.3% | 0.2491 | 0.2501 |
| 53 | 2026-05-10 to 2026-05-24 |  | 30.9% | 55.1% | 48.8% | 0.2504 | 0.2501 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.5% | 57.6% | 50.3% | 0.2495 | 0.2497 |
| 55 | 2026-06-07 to 2026-06-21 |  | 0.9% | 66.7% | 49.7% | 0.2492 | 0.2499 |
| 56 | 2026-06-21 to 2026-07-05 |  | 24.2% | 51.1% | 50.8% | 0.2509 | 0.2499 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.3% | 25.0% | 48.4% | 0.2491 | 0.2499 |
| 58 | 2026-07-19 to 2026-08-02 |  | 21.7% | 53.0% | 49.3% | 0.2502 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 10.2% | 59.1% | 47.6% | 0.2490 | 0.2498 |
| 60 | 2026-08-16 to 2026-08-30 |  | 32.2% | 52.5% | 50.6% | 0.2506 | 0.2501 |
| 61 | 2026-08-30 to 2026-09-13 |  | 7.1% | 57.9% | 48.5% | 0.2484 | 0.2500 |
| 62 | 2026-09-13 to 2026-09-27 |  | 12.3% | 56.4% | 51.3% | 0.2505 | 0.2500 |
