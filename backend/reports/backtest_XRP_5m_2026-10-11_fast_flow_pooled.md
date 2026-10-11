# Backtest XRP 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 50666 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.7% | naive 48.9%, reverse 51.1%, always-up 49.5%, always-down 50.5% |
| Flat candles (close equal to the previous close) | 3.3% | |
| Coverage (share of non-neutral calls) | 15.2% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2500 |
| Log loss | 0.6928 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3958 / 54.4% / 8.6% | |
| Down calls: n / precision / recall | 3774 / 52.9% / 7.8% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 5.64% (3.71% to 7.73%)
- Accuracy minus the best simple rule: 3.07% (1.77% to 4.57%)
- Brier improvement over base rate: 0.00015 (-0.00022 to 0.00052)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -69.14 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -162.18 |
| Buy and hold | 16.8% | -36.0% | 0.82 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 208 | 0.387 | 0.471 |
| 0.4-0.5 | 25931 | 0.473 | 0.479 |
| 0.5-0.6 | 24217 | 0.527 | 0.512 |
| 0.6-0.7 | 309 | 0.620 | 0.553 |
| 0.7-0.8 | 1 | 0.701 | 1.000 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 26.1% | 52.6% | 50.5% | 0.2502 | 0.2500 |
| 30 | 2026-04-19 to 2026-05-03 |  | 21.2% | 56.8% | 48.7% | 0.2487 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 33.1% | 52.1% | 50.0% | 0.2509 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 19.5% | 50.2% | 49.1% | 0.2509 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 7.8% | 53.2% | 49.7% | 0.2496 | 0.2499 |
| 34 | 2026-06-14 to 2026-06-28 |  | 9.3% | 54.3% | 48.1% | 0.2496 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 11.1% | 55.8% | 47.4% | 0.2494 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 10.9% | 53.5% | 48.9% | 0.2498 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 19.1% | 51.4% | 49.8% | 0.2504 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 19.1% | 55.0% | 49.5% | 0.2506 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 10.8% | 56.9% | 47.3% | 0.2488 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 6.7% | 54.7% | 49.1% | 0.2498 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 3.2% | 62.2% | 47.5% | 0.2493 | 0.2500 |
