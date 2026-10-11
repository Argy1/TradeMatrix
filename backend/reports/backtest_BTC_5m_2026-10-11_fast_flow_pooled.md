# Backtest BTC 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 52218 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.9% | naive 48.7%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 0.4% | |
| Coverage (share of non-neutral calls) | 15.1% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2500 |
| Log loss | 0.6928 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4646 / 53.9% / 9.6% | |
| Down calls: n / precision / recall | 3231 / 53.9% / 6.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 5.13% (4.00% to 6.37%)
- Accuracy minus the best simple rule: 3.28% (2.25% to 4.32%)
- Brier improvement over base rate: 0.00020 (-0.00014 to 0.00053)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -97.48 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -221.01 |
| Buy and hold | 27.2% | -29.7% | 1.45 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 89 | 0.391 | 0.494 |
| 0.4-0.5 | 25701 | 0.474 | 0.481 |
| 0.5-0.6 | 26070 | 0.528 | 0.517 |
| 0.6-0.7 | 358 | 0.621 | 0.556 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 22.6% | 55.8% | 48.6% | 0.2490 | 0.2501 |
| 30 | 2026-04-19 to 2026-05-03 |  | 17.8% | 55.4% | 49.0% | 0.2498 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 30.8% | 53.2% | 48.2% | 0.2503 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 18.7% | 52.9% | 50.2% | 0.2502 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 6.0% | 53.8% | 48.6% | 0.2492 | 0.2499 |
| 34 | 2026-06-14 to 2026-06-28 |  | 8.5% | 52.6% | 48.7% | 0.2498 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 10.5% | 50.6% | 47.3% | 0.2495 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 10.3% | 53.8% | 47.9% | 0.2498 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 20.4% | 52.5% | 50.6% | 0.2511 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 21.3% | 52.7% | 48.6% | 0.2506 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 15.0% | 57.6% | 47.4% | 0.2490 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 8.6% | 53.0% | 49.4% | 0.2497 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 5.7% | 56.3% | 49.0% | 0.2495 | 0.2500 |
