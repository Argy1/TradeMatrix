# Backtest UNI 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 125540 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.0% | naive 49.7%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 11.0% | |
| Coverage (share of non-neutral calls) | 1.5% | 100% |
| Brier score (lower is better) | 0.2499 | base rate 0.2500 |
| Log loss | 0.6929 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1392 / 57.2% / 1.3% | |
| Down calls: n / precision / recall | 456 / 52.4% / 0.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.21% (3.32% to 9.67%)
- Accuracy minus the best simple rule: 5.16% (2.27% to 8.81%)
- Brier improvement over base rate: 0.00013 (0.00004 to 0.00023)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -98.0% | -98.0% | -53.58 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -426.87 |
| Buy and hold | 181.1% | -30.6% | 4.20 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 11 | 0.387 | 0.818 |
| 0.4-0.5 | 70802 | 0.491 | 0.493 |
| 0.5-0.6 | 54716 | 0.513 | 0.508 |
| 0.6-0.7 | 11 | 0.606 | 0.727 |

## Most useful features (average gain)

- stoch_k: 16.70
- dist_ema21: 16.50
- rsi14: 14.36
- log_ret_1: 13.34
- dist_ema9: 13.14
- ret_1: 12.44
- ret_3: 12.01
- bb_percent_b: 11.79

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 289 | 7.2% | 55.1% | 48.5% | 0.2495 | 0.2499 |
| 29 | 2026-07-08 to 2026-07-15 | 142 | 5.7% | 56.8% | 49.8% | 0.2501 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 194 | 0.0% | 50.0% | 49.5% | 0.2497 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 7 | 0.0% | n/a | 49.2% | 0.2500 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 488 | 0.6% | 66.0% | 49.8% | 0.2498 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 220 | 0.5% | 56.8% | 48.9% | 0.2495 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 66 | 2.4% | 52.5% | 48.8% | 0.2497 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 376 | 4.4% | 57.1% | 50.3% | 0.2501 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 298 | 0.4% | 51.4% | 50.4% | 0.2500 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 7 | 0.0% | n/a | 49.4% | 0.2500 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 59 | 0.0% | n/a | 49.6% | 0.2500 | 0.2501 |
| 39 | 2026-09-16 to 2026-09-23 | 50 | 0.0% | n/a | 50.8% | 0.2501 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 271 | 0.0% | n/a | 51.2% | 0.2499 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 1 | 0.0% | n/a | 49.5% | 0.2499 | 0.2500 |
