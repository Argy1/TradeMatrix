# Backtest AVAX 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 47150 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 57.8% | naive 47.9%, reverse 52.1%, always-up 49.5%, always-down 50.5% |
| Flat candles (close equal to the previous close) | 10.0% | |
| Coverage (share of non-neutral calls) | 21.6% | 100% |
| Brier score (lower is better) | 0.2481 | base rate 0.2500 |
| Log loss | 0.6894 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4394 / 58.3% / 11.0% | |
| Down calls: n / precision / recall | 5032 / 57.4% / 12.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.79% (5.45% to 12.75%)
- Accuracy minus the best simple rule: 3.94% (2.21% to 5.82%)
- Brier improvement over base rate: 0.00232 (0.00033 to 0.00481)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -75.35 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -147.64 |
| Buy and hold | 25.1% | -45.7% | 0.99 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 17 | 0.290 | 0.294 |
| 0.3-0.4 | 836 | 0.375 | 0.347 |
| 0.4-0.5 | 24470 | 0.471 | 0.471 |
| 0.5-0.6 | 21104 | 0.529 | 0.523 |
| 0.6-0.7 | 716 | 0.623 | 0.649 |
| 0.7-0.8 | 7 | 0.720 | 0.571 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 41.3% | 59.7% | 46.4% | 0.2447 | 0.2500 |
| 30 | 2026-04-19 to 2026-05-03 |  | 41.9% | 68.7% | 43.1% | 0.2373 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 50.0% | 63.9% | 44.0% | 0.2401 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 26.8% | 54.4% | 49.0% | 0.2492 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 10.1% | 52.8% | 49.4% | 0.2501 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 10.3% | 58.1% | 47.7% | 0.2490 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 14.1% | 53.5% | 46.4% | 0.2490 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 12.3% | 51.3% | 50.0% | 0.2507 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 22.3% | 52.7% | 47.3% | 0.2492 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 24.9% | 52.7% | 49.4% | 0.2513 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 14.4% | 53.3% | 48.6% | 0.2496 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 8.5% | 55.5% | 49.7% | 0.2499 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 3.5% | 57.1% | 48.4% | 0.2495 | 0.2500 |
