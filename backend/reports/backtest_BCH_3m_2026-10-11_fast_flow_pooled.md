# Backtest BCH 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 50393 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.6% | naive 48.1%, always-up 50.2%, always-down 49.8% |
| Flat candles (close equal to the previous close) | 16.7% | |
| Coverage (share of non-neutral calls) | 27.7% | 100% |
| Brier score (lower is better) | 0.2493 | base rate 0.2500 |
| Log loss | 0.6917 | coin flip 0.6931 |
| Up calls: n / precision / recall | 6194 / 56.1% / 13.7% | |
| Down calls: n / precision / recall | 7249 / 55.2% / 15.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.16% (4.91% to 9.22%)
- Accuracy minus the best simple rule: 4.66% (2.83% to 6.20%)
- Brier improvement over base rate: 0.00085 (0.00008 to 0.00168)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -126.49 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -213.39 |
| Buy and hold | 21.2% | -29.8% | 1.10 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 17 | 0.283 | 0.353 |
| 0.3-0.4 | 1415 | 0.375 | 0.418 |
| 0.4-0.5 | 25196 | 0.467 | 0.482 |
| 0.5-0.6 | 22539 | 0.532 | 0.527 |
| 0.6-0.7 | 1212 | 0.621 | 0.551 |
| 0.7-0.8 | 14 | 0.715 | 0.643 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 7.7% | 51.7% | 48.2% | 0.2500 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 20.0% | 56.9% | 48.1% | 0.2489 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 33.2% | 58.9% | 46.2% | 0.2480 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 31.3% | 54.1% | 47.5% | 0.2502 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 25.2% | 55.3% | 50.1% | 0.2495 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 25.6% | 56.4% | 48.3% | 0.2494 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 27.8% | 57.9% | 48.1% | 0.2481 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 42.2% | 54.8% | 47.6% | 0.2488 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 45.5% | 56.7% | 46.0% | 0.2479 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 48.6% | 59.0% | 45.4% | 0.2465 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 53.8% | 59.2% | 44.3% | 0.2446 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 29.9% | 49.5% | 50.3% | 0.2522 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 19.0% | 51.7% | 50.4% | 0.2509 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 13.8% | 56.4% | 48.6% | 0.2490 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 34.2% | 55.1% | 48.5% | 0.2503 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 18.7% | 45.6% | 49.7% | 0.2518 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 8.7% | 57.1% | 48.8% | 0.2495 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 13.0% | 57.5% | 48.7% | 0.2490 | 0.2500 |
