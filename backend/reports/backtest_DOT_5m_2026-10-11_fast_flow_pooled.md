# Backtest DOT 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 40003 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 60.3% | naive 46.3%, always-up 49.7%, always-down 50.3% |
| Flat candles (close equal to the previous close) | 23.7% | |
| Coverage (share of non-neutral calls) | 32.2% | 100% |
| Brier score (lower is better) | 0.2459 | base rate 0.2500 |
| Log loss | 0.6848 | coin flip 0.6931 |
| Up calls: n / precision / recall | 5595 / 60.6% / 17.0% | |
| Down calls: n / precision / recall | 6981 / 60.2% / 20.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 13.92% (10.33% to 17.61%)
- Accuracy minus the best simple rule: 9.42% (7.02% to 11.79%)
- Brier improvement over base rate: 0.00444 (0.00233 to 0.00670)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -87.66 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -148.80 |
| Buy and hold | -2.6% | -49.1% | 0.32 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 2 | 0.294 | 0.500 |
| 0.3-0.4 | 1208 | 0.380 | 0.374 |
| 0.4-0.5 | 20145 | 0.464 | 0.452 |
| 0.5-0.6 | 17675 | 0.535 | 0.550 |
| 0.6-0.7 | 972 | 0.621 | 0.632 |
| 0.7-0.8 | 1 | 0.715 | 0.000 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 37.1% | 54.2% | 48.1% | 0.2494 | 0.2500 |
| 30 | 2026-04-19 to 2026-05-03 |  | 35.4% | 62.0% | 44.2% | 0.2436 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 46.1% | 55.2% | 48.1% | 0.2495 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 34.8% | 57.4% | 47.0% | 0.2480 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 15.4% | 55.4% | 47.9% | 0.2490 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 25.1% | 63.6% | 46.0% | 0.2453 | 0.2499 |
| 35 | 2026-06-28 to 2026-07-12 |  | 33.6% | 61.7% | 44.2% | 0.2436 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 30.7% | 65.1% | 44.6% | 0.2433 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 48.8% | 68.5% | 42.0% | 0.2362 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 47.7% | 65.7% | 42.2% | 0.2394 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 31.7% | 58.0% | 47.9% | 0.2475 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 18.8% | 58.5% | 48.2% | 0.2479 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 12.9% | 55.7% | 49.5% | 0.2494 | 0.2500 |
