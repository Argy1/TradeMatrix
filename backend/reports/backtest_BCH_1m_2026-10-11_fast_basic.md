# Backtest BCH 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 96995 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 58.1% | naive 48.5%, reverse 51.5%, always-up 50.2%, always-down 49.8% |
| Flat candles (close equal to the previous close) | 31.3% | |
| Coverage (share of non-neutral calls) | 34.6% | 100% |
| Brier score (lower is better) | 0.2472 | base rate 0.2500 |
| Log loss | 0.6875 | coin flip 0.6931 |
| Up calls: n / precision / recall | 16804 / 58.6% / 20.2% | |
| Down calls: n / precision / recall | 14547 / 57.5% / 17.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.07% (4.48% to 13.10%)
- Accuracy minus the best simple rule: 5.11% (1.60% to 7.90%)
- Brier improvement over base rate: 0.00374 (0.00085 to 0.00685)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -308.06 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -478.44 |
| Buy and hold | 40.3% | -30.2% | 2.03 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.1-0.2 | 8 | 0.182 | 0.125 |
| 0.2-0.3 | 440 | 0.272 | 0.352 |
| 0.3-0.4 | 4342 | 0.367 | 0.407 |
| 0.4-0.5 | 41145 | 0.467 | 0.461 |
| 0.5-0.6 | 45055 | 0.533 | 0.536 |
| 0.6-0.7 | 5147 | 0.635 | 0.605 |
| 0.7-0.8 | 812 | 0.735 | 0.660 |
| 0.8-0.9 | 46 | 0.825 | 0.804 |

## Most useful features (average gain)

- dist_ema9: 47.62
- dist_ema21: 29.34
- btc_ret_1: 28.68
- log_ret_1: 28.54
- ret_1: 26.64
- body_pct: 21.80
- bb_percent_b: 19.71
- stoch_k: 18.67

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 651 | 24.8% | 54.7% | 48.6% | 0.2491 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 102 | 9.9% | 62.0% | 46.8% | 0.2471 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 49 | 43.1% | 58.9% | 46.5% | 0.2453 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 788 | 55.3% | 60.2% | 48.6% | 0.2431 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 794 | 56.7% | 61.3% | 47.9% | 0.2415 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 714 | 58.0% | 65.5% | 46.3% | 0.2341 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 619 | 74.8% | 62.5% | 44.1% | 0.2363 | 0.2499 |
| 35 | 2026-08-19 to 2026-08-26 | 796 | 67.5% | 52.8% | 48.6% | 0.2563 | 0.2499 |
| 36 | 2026-08-26 to 2026-09-02 | 736 | 7.7% | 61.8% | 51.2% | 0.2477 | 0.2501 |
| 37 | 2026-09-02 to 2026-09-09 | 26 | 22.7% | 53.8% | 50.0% | 0.2496 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 487 | 20.4% | 59.1% | 48.0% | 0.2473 | 0.2501 |
| 39 | 2026-09-16 to 2026-09-23 | 316 | 43.4% | 52.9% | 50.0% | 0.2512 | 0.2499 |
| 40 | 2026-09-23 to 2026-09-30 | 422 | 0.5% | 39.5% | 50.7% | 0.2498 | 0.2501 |
| 41 | 2026-09-30 to 2026-10-07 | 19 | 0.0% | n/a | 48.2% | 0.2490 | 0.2500 |
