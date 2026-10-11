# Backtest TRX 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 35924 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 65.9% | naive 43.7%, always-up 51.5%, always-down 48.5% |
| Flat candles (close equal to the previous close) | 31.5% | |
| Coverage (share of non-neutral calls) | 41.8% | 100% |
| Brier score (lower is better) | 0.2398 | base rate 0.2501 |
| Log loss | 0.6725 | coin flip 0.6931 |
| Up calls: n / precision / recall | 7893 / 68.6% / 29.3% | |
| Down calls: n / precision / recall | 6658 / 62.8% / 24.0% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 22.41% (19.99% to 24.87%)
- Accuracy minus the best simple rule: 14.42% (12.09% to 16.57%)
- Brier improvement over base rate: 0.01053 (0.00806 to 0.01304)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -187.28 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -295.92 |
| Buy and hold | 5.1% | -17.2% | 0.64 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 12 | 0.278 | 0.333 |
| 0.3-0.4 | 1344 | 0.377 | 0.361 |
| 0.4-0.5 | 14754 | 0.460 | 0.424 |
| 0.5-0.6 | 16813 | 0.537 | 0.566 |
| 0.6-0.7 | 2795 | 0.635 | 0.742 |
| 0.7-0.8 | 206 | 0.721 | 0.801 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 52.2% | 66.5% | 42.1% | 0.2371 | 0.2502 |
| 30 | 2026-04-19 to 2026-05-03 |  | 42.2% | 65.5% | 45.0% | 0.2389 | 0.2502 |
| 31 | 2026-05-03 to 2026-05-17 |  | 48.6% | 60.6% | 44.3% | 0.2443 | 0.2502 |
| 32 | 2026-05-17 to 2026-05-31 |  | 39.0% | 60.0% | 45.3% | 0.2449 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 17.4% | 65.8% | 46.9% | 0.2468 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 38.5% | 62.8% | 42.9% | 0.2449 | 0.2502 |
| 35 | 2026-06-28 to 2026-07-12 |  | 40.2% | 64.7% | 45.3% | 0.2412 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 37.6% | 69.3% | 41.4% | 0.2377 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 57.0% | 70.3% | 40.6% | 0.2296 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 51.9% | 68.8% | 42.2% | 0.2340 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 42.4% | 65.1% | 44.4% | 0.2393 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 38.7% | 68.1% | 42.5% | 0.2383 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 37.3% | 70.5% | 43.8% | 0.2371 | 0.2500 |
