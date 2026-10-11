# Backtest XLM 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 44508 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 57.4% | naive 47.7%, always-up 49.1%, always-down 50.9% |
| Flat candles (close equal to the previous close) | 15.1% | |
| Coverage (share of non-neutral calls) | 25.4% | 100% |
| Brier score (lower is better) | 0.2482 | base rate 0.2500 |
| Log loss | 0.6896 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4914 / 57.3% / 12.9% | |
| Down calls: n / precision / recall | 6089 / 57.4% / 15.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.72% (7.81% to 11.76%)
- Accuracy minus the best simple rule: 6.36% (4.98% to 7.74%)
- Brier improvement over base rate: 0.00182 (0.00105 to 0.00265)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -78.20 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -119.63 |
| Buy and hold | 38.4% | -48.6% | 1.18 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 4 | 0.285 | 0.500 |
| 0.3-0.4 | 906 | 0.380 | 0.376 |
| 0.4-0.5 | 23121 | 0.467 | 0.466 |
| 0.5-0.6 | 19681 | 0.532 | 0.522 |
| 0.6-0.7 | 795 | 0.621 | 0.592 |
| 0.7-0.8 | 1 | 0.703 | 1.000 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 39.2% | 54.2% | 48.0% | 0.2501 | 0.2500 |
| 30 | 2026-04-19 to 2026-05-03 |  | 34.1% | 58.7% | 44.4% | 0.2462 | 0.2499 |
| 31 | 2026-05-03 to 2026-05-17 |  | 46.0% | 59.0% | 47.1% | 0.2456 | 0.2499 |
| 32 | 2026-05-17 to 2026-05-31 |  | 30.8% | 55.7% | 48.2% | 0.2485 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 10.6% | 55.9% | 48.5% | 0.2492 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 14.5% | 53.8% | 47.9% | 0.2492 | 0.2499 |
| 35 | 2026-06-28 to 2026-07-12 |  | 16.6% | 57.5% | 48.9% | 0.2488 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 19.0% | 63.2% | 46.2% | 0.2470 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 35.9% | 59.5% | 47.6% | 0.2461 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 34.8% | 58.4% | 46.1% | 0.2472 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 23.3% | 54.6% | 48.3% | 0.2497 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 16.5% | 54.5% | 49.5% | 0.2492 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 9.3% | 60.4% | 48.4% | 0.2492 | 0.2500 |
