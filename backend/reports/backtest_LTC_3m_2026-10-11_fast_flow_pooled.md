# Backtest LTC 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 54485 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.6% | naive 48.7%, reverse 51.3%, always-up 50.5%, always-down 49.5% |
| Flat candles (close equal to the previous close) | 9.9% | |
| Coverage (share of non-neutral calls) | 16.2% | 100% |
| Brier score (lower is better) | 0.2491 | base rate 0.2500 |
| Log loss | 0.6913 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3810 / 57.2% / 7.9% | |
| Down calls: n / precision / recall | 4747 / 56.0% / 9.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.76% (4.44% to 9.03%)
- Accuracy minus the best simple rule: 3.65% (2.06% to 5.09%)
- Brier improvement over base rate: 0.00100 (0.00027 to 0.00182)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -113.97 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -259.45 |
| Buy and hold | 38.7% | -16.0% | 1.88 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 3 | 0.278 | 0.333 |
| 0.3-0.4 | 771 | 0.379 | 0.370 |
| 0.4-0.5 | 28262 | 0.473 | 0.487 |
| 0.5-0.6 | 24826 | 0.525 | 0.526 |
| 0.6-0.7 | 612 | 0.622 | 0.623 |
| 0.7-0.8 | 11 | 0.726 | 0.273 |

## Most useful features (average gain)

- dist_ema9: 358.56
- dist_ema21: 191.48
- lower_wick_pct: 144.74
- log_ret_1: 123.25
- upper_wick_pct: 119.77
- stoch_k: 114.22
- ret_1: 107.74
- rsi14: 98.99

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 45 | 2026-06-04 to 2026-06-11 |  | 4.1% | 58.7% | 48.1% | 0.2486 | 0.2501 |
| 46 | 2026-06-11 to 2026-06-18 |  | 13.1% | 59.1% | 48.3% | 0.2488 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 19.4% | 55.1% | 48.1% | 0.2497 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 18.8% | 53.5% | 48.4% | 0.2500 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 18.0% | 54.9% | 48.6% | 0.2497 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 17.9% | 56.6% | 48.2% | 0.2491 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 13.3% | 54.0% | 47.6% | 0.2488 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 24.7% | 58.4% | 49.0% | 0.2484 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 30.1% | 60.0% | 46.0% | 0.2461 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 33.5% | 59.5% | 46.3% | 0.2455 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 36.9% | 60.8% | 46.7% | 0.2451 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 21.2% | 52.2% | 51.4% | 0.2507 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 8.0% | 58.2% | 48.3% | 0.2494 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 4.6% | 54.6% | 49.8% | 0.2500 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 13.5% | 50.6% | 49.3% | 0.2503 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 7.4% | 52.1% | 51.5% | 0.2510 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 3.4% | 53.6% | 49.6% | 0.2503 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 3.7% | 44.6% | 49.8% | 0.2504 | 0.2500 |
