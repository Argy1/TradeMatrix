# Backtest BTC 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 133713 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.8% | naive 51.3%, reverse 48.7%, always-up 50.2%, always-down 49.8% |
| Flat candles (close equal to the previous close) | 5.2% | |
| Coverage (share of non-neutral calls) | 17.1% | 100% |
| Brier score (lower is better) | 0.2485 | base rate 0.2500 |
| Log loss | 0.6902 | coin flip 0.6931 |
| Up calls: n / precision / recall | 11049 / 57.8% / 9.5% | |
| Down calls: n / precision / recall | 11003 / 55.7% / 9.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.49% (4.70% to 8.53%)
- Accuracy minus the best simple rule: 6.36% (4.56% to 8.43%)
- Brier improvement over base rate: 0.00151 (0.00057 to 0.00246)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -248.37 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -630.91 |
| Buy and hold | 38.7% | -8.6% | 3.66 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.1-0.2 | 11 | 0.193 | 0.091 |
| 0.2-0.3 | 187 | 0.266 | 0.412 |
| 0.3-0.4 | 1874 | 0.370 | 0.422 |
| 0.4-0.5 | 59344 | 0.473 | 0.472 |
| 0.5-0.6 | 70342 | 0.526 | 0.526 |
| 0.6-0.7 | 1794 | 0.633 | 0.633 |
| 0.7-0.8 | 159 | 0.724 | 0.818 |
| 0.8-0.9 | 2 | 0.809 | 1.000 |

## Most useful features (average gain)

- log_ret_1: 17.03
- dist_ema9: 16.14
- upper_wick_pct: 15.51
- ret_1: 14.90
- body_pct: 13.97
- lower_wick_pct: 13.66
- dist_ema21: 12.91
- atr_pct: 12.40

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 124 | 1.8% | 61.7% | 49.7% | 0.2489 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 105 | 15.0% | 55.0% | 50.3% | 0.2489 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 181 | 8.4% | 54.2% | 51.0% | 0.2495 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 447 | 6.2% | 56.8% | 51.7% | 0.2490 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 792 | 13.2% | 54.2% | 51.1% | 0.2493 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 509 | 19.0% | 57.9% | 52.5% | 0.2472 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 727 | 52.0% | 58.9% | 51.6% | 0.2448 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 720 | 38.9% | 51.5% | 50.0% | 0.2523 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 800 | 1.5% | 67.8% | 52.0% | 0.2495 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 111 | 7.6% | 54.8% | 50.7% | 0.2493 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 307 | 7.7% | 61.1% | 50.9% | 0.2482 | 0.2500 |
| 39 | 2026-09-16 to 2026-09-23 | 263 | 15.3% | 56.7% | 51.2% | 0.2490 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 686 | 20.0% | 59.0% | 53.4% | 0.2476 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 708 | 33.3% | 60.0% | 52.5% | 0.2452 | 0.2500 |
