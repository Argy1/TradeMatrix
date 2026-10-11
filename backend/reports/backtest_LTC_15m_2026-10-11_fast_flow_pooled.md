# Backtest LTC 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 15414 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.3% | naive 48.0%, always-up 51.1%, always-down 48.9% |
| Flat candles (close equal to the previous close) | 4.4% | |
| Coverage (share of non-neutral calls) | 14.5% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2501 |
| Log loss | 0.6921 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1157 / 54.7% / 8.0% | |
| Down calls: n / precision / recall | 1105 / 51.9% / 7.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.88% (4.76% to 13.05%)
- Accuracy minus the best simple rule: 5.46% (1.92% to 9.12%)
- Brier improvement over base rate: 0.00064 (0.00009 to 0.00117)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -90.4% | -90.4% | -27.22 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -68.94 |
| Buy and hold | 32.4% | -34.9% | 1.40 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.278 | 1.000 |
| 0.3-0.4 | 96 | 0.388 | 0.469 |
| 0.4-0.5 | 7786 | 0.474 | 0.491 |
| 0.5-0.6 | 7518 | 0.526 | 0.533 |
| 0.6-0.7 | 13 | 0.610 | 0.615 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 34.8% | 52.6% | 48.4% | 0.2503 | 0.2502 |
| 52 | 2026-04-26 to 2026-05-10 |  | 5.3% | 63.2% | 47.5% | 0.2485 | 0.2503 |
| 53 | 2026-05-10 to 2026-05-24 |  | 29.4% | 52.2% | 46.6% | 0.2502 | 0.2499 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.8% | 56.8% | 48.8% | 0.2490 | 0.2500 |
| 55 | 2026-06-07 to 2026-06-21 |  | 0.9% | 66.7% | 46.2% | 0.2502 | 0.2502 |
| 56 | 2026-06-21 to 2026-07-05 |  | 24.6% | 48.3% | 49.4% | 0.2512 | 0.2501 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.3% | 50.0% | 48.8% | 0.2493 | 0.2501 |
| 58 | 2026-07-19 to 2026-08-02 |  | 21.6% | 50.5% | 48.7% | 0.2496 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 6.8% | 65.9% | 48.1% | 0.2484 | 0.2502 |
| 60 | 2026-08-16 to 2026-08-30 |  | 30.4% | 52.3% | 49.0% | 0.2503 | 0.2502 |
| 61 | 2026-08-30 to 2026-09-13 |  | 4.9% | 67.2% | 47.5% | 0.2481 | 0.2501 |
| 62 | 2026-09-13 to 2026-09-27 |  | 12.5% | 57.1% | 47.2% | 0.2488 | 0.2501 |
