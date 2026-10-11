# Backtest ETH 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 137291 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.0% | naive 50.0%, reverse 50.0%, always-up 50.4%, always-down 49.6% |
| Flat candles (close equal to the previous close) | 2.7% | |
| Coverage (share of non-neutral calls) | 2.8% | 100% |
| Brier score (lower is better) | 0.2496 | base rate 0.2500 |
| Log loss | 0.6924 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1394 / 55.1% / 1.1% | |
| Down calls: n / precision / recall | 2477 / 56.5% / 2.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 10.74% (3.99% to 18.68%)
- Accuracy minus the best simple rule: 9.91% (3.18% to 17.89%)
- Brier improvement over base rate: 0.00036 (0.00019 to 0.00057)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -92.1% | -92.1% | -71.75 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -609.76 |
| Buy and hold | 58.6% | -11.1% | 3.86 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 201 | 0.386 | 0.343 |
| 0.4-0.5 | 49079 | 0.483 | 0.485 |
| 0.5-0.6 | 88009 | 0.516 | 0.516 |
| 0.6-0.7 | 2 | 0.604 | 0.500 |

## Most useful features (average gain)

- dist_ema21: 33.64
- dist_ema50: 21.15
- dist_ema9: 20.41
- rsi14: 19.13
- bb_percent_b: 13.54
- ret_6: 12.40
- macd_pct: 12.01
- btc_rsi14: 11.47

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 566 | 7.3% | 60.7% | 47.9% | 0.2486 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 147 | 16.3% | 53.7% | 50.3% | 0.2495 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 221 | 4.5% | 56.4% | 49.9% | 0.2494 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 277 | 2.7% | 54.9% | 50.0% | 0.2495 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 47 | 0.6% | 67.2% | 50.3% | 0.2497 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 127 | 0.1% | 63.6% | 51.6% | 0.2495 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 30 | 0.0% | 100.0% | 49.7% | 0.2499 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 177 | 1.7% | 59.8% | 49.3% | 0.2496 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 765 | 0.6% | 51.6% | 50.6% | 0.2500 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 67 | 0.0% | n/a | 49.7% | 0.2500 | 0.2499 |
| 38 | 2026-09-09 to 2026-09-16 | 243 | 0.1% | 37.5% | 49.3% | 0.2500 | 0.2501 |
| 39 | 2026-09-16 to 2026-09-23 | 71 | 0.3% | 59.3% | 49.8% | 0.2497 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 370 | 4.4% | 53.1% | 51.2% | 0.2500 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 391 | 0.4% | 72.7% | 51.1% | 0.2495 | 0.2500 |
