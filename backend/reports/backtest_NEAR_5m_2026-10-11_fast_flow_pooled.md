# Backtest NEAR 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 46623 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.9% | naive 48.6%, reverse 51.4%, always-up 49.8%, always-down 50.2% |
| Flat candles (close equal to the previous close) | 11.1% | |
| Coverage (share of non-neutral calls) | 22.7% | 100% |
| Brier score (lower is better) | 0.2491 | base rate 0.2500 |
| Log loss | 0.6913 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4763 / 56.6% / 11.6% | |
| Down calls: n / precision / recall | 5414 / 55.3% / 12.8% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.13% (6.16% to 8.18%)
- Accuracy minus the best simple rule: 4.22% (3.47% to 4.90%)
- Brier improvement over base rate: 0.00098 (0.00050 to 0.00159)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -55.68 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -95.70 |
| Buy and hold | 289.9% | -49.7% | 2.94 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.291 | 1.000 |
| 0.3-0.4 | 663 | 0.381 | 0.407 |
| 0.4-0.5 | 24118 | 0.469 | 0.478 |
| 0.5-0.6 | 21148 | 0.530 | 0.520 |
| 0.6-0.7 | 691 | 0.620 | 0.596 |
| 0.7-0.8 | 2 | 0.702 | 0.500 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 37.1% | 56.7% | 47.9% | 0.2484 | 0.2501 |
| 30 | 2026-04-19 to 2026-05-03 |  | 34.7% | 58.9% | 47.4% | 0.2460 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 45.9% | 55.2% | 47.9% | 0.2496 | 0.2501 |
| 32 | 2026-05-17 to 2026-05-31 |  | 23.7% | 56.2% | 48.1% | 0.2489 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 10.4% | 55.7% | 48.7% | 0.2496 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 12.6% | 55.1% | 49.1% | 0.2488 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 16.7% | 52.9% | 47.8% | 0.2494 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 17.0% | 56.5% | 48.9% | 0.2487 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 32.0% | 56.4% | 50.0% | 0.2488 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 33.6% | 55.7% | 48.3% | 0.2492 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 19.0% | 53.2% | 49.9% | 0.2505 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 9.4% | 56.5% | 48.8% | 0.2494 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 2.7% | 55.7% | 49.1% | 0.2498 | 0.2500 |
