# Backtest BCH 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 46022 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.8% | naive 48.3%, reverse 51.7%, always-up 50.0%, always-down 50.0% |
| Flat candles (close equal to the previous close) | 12.2% | |
| Coverage (share of non-neutral calls) | 23.8% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2500 |
| Log loss | 0.6922 | coin flip 0.6931 |
| Up calls: n / precision / recall | 5199 / 55.0% / 12.4% | |
| Down calls: n / precision / recall | 5586 / 54.5% / 13.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.16% (5.56% to 8.95%)
- Accuracy minus the best simple rule: 3.65% (2.52% to 5.00%)
- Brier improvement over base rate: 0.00051 (0.00005 to 0.00095)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -84.12 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -146.41 |
| Buy and hold | -24.7% | -62.7% | -0.41 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 658 | 0.383 | 0.438 |
| 0.4-0.5 | 23403 | 0.468 | 0.481 |
| 0.5-0.6 | 21131 | 0.532 | 0.520 |
| 0.6-0.7 | 814 | 0.624 | 0.575 |
| 0.7-0.8 | 16 | 0.729 | 0.688 |

## Most useful features (average gain)

- dist_ema9: 222.13
- bb_percent_b: 165.37
- dist_ema21: 133.72
- rsi14: 99.11
- lower_wick_pct: 92.35
- upper_wick_pct: 81.22
- stoch_k: 71.15
- log_ret_1: 59.11

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 29 | 2026-04-05 to 2026-04-19 |  | 35.1% | 52.2% | 49.2% | 0.2513 | 0.2500 |
| 30 | 2026-04-19 to 2026-05-03 |  | 30.6% | 53.0% | 49.3% | 0.2498 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 38.7% | 57.6% | 46.8% | 0.2479 | 0.2499 |
| 32 | 2026-05-17 to 2026-05-31 |  | 28.3% | 53.1% | 48.4% | 0.2505 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 10.5% | 56.1% | 48.4% | 0.2495 | 0.2499 |
| 34 | 2026-06-14 to 2026-06-28 |  | 15.4% | 54.6% | 48.9% | 0.2491 | 0.2501 |
| 35 | 2026-06-28 to 2026-07-12 |  | 17.0% | 56.4% | 47.6% | 0.2494 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 19.0% | 56.7% | 47.9% | 0.2484 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 32.1% | 53.5% | 47.7% | 0.2494 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 36.9% | 54.5% | 48.2% | 0.2494 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 22.1% | 52.8% | 48.9% | 0.2504 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 16.4% | 57.6% | 48.6% | 0.2494 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 7.6% | 62.4% | 47.5% | 0.2488 | 0.2500 |
