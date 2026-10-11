# Backtest DOGE 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 50149 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.9% | naive 48.9%, reverse 51.1%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 4.3% | |
| Coverage (share of non-neutral calls) | 15.0% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2500 |
| Log loss | 0.6927 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3500 / 54.1% / 7.6% | |
| Down calls: n / precision / recall | 4032 / 53.6% / 8.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 5.00% (3.43% to 6.54%)
- Accuracy minus the best simple rule: 2.79% (1.67% to 3.97%)
- Brier improvement over base rate: 0.00022 (-0.00004 to 0.00047)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -99.9% | -99.9% | -60.44 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -157.21 |
| Buy and hold | 4.2% | -42.5% | 0.45 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 227 | 0.385 | 0.432 |
| 0.4-0.5 | 26568 | 0.473 | 0.482 |
| 0.5-0.6 | 23147 | 0.527 | 0.517 |
| 0.6-0.7 | 207 | 0.620 | 0.599 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 24.7% | 52.5% | 50.2% | 0.2496 | 0.2500 |
| 30 | 2026-04-19 to 2026-05-03 |  | 18.2% | 57.4% | 49.7% | 0.2494 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 33.8% | 54.1% | 47.9% | 0.2498 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 20.1% | 50.6% | 50.2% | 0.2509 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 7.4% | 56.8% | 48.5% | 0.2492 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 7.6% | 57.3% | 48.3% | 0.2491 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 10.8% | 52.6% | 48.1% | 0.2500 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 10.1% | 49.9% | 49.4% | 0.2501 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 18.4% | 53.1% | 49.7% | 0.2503 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 21.6% | 55.7% | 48.0% | 0.2494 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 12.2% | 55.0% | 48.0% | 0.2498 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 6.4% | 52.7% | 50.0% | 0.2497 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 3.8% | 53.7% | 48.4% | 0.2497 | 0.2500 |
