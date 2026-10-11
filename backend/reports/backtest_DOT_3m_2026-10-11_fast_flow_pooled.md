# Backtest DOT 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 41814 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 65.0% | naive 45.9%, reverse 54.1%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 30.9% | |
| Coverage (share of non-neutral calls) | 39.9% | 100% |
| Brier score (lower is better) | 0.2413 | base rate 0.2500 |
| Log loss | 0.6754 | coin flip 0.6931 |
| Up calls: n / precision / recall | 7328 / 65.9% / 23.2% | |
| Down calls: n / precision / recall | 8448 / 64.3% / 25.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 17.88% (13.30% to 22.49%)
- Accuracy minus the best simple rule: 8.68% (6.74% to 10.58%)
- Brier improvement over base rate: 0.00990 (0.00573 to 0.01451)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -145.59 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -219.34 |
| Buy and hold | 3.6% | -32.1% | 0.53 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 79 | 0.278 | 0.165 |
| 0.3-0.4 | 2324 | 0.370 | 0.300 |
| 0.4-0.5 | 19315 | 0.462 | 0.440 |
| 0.5-0.6 | 18089 | 0.537 | 0.564 |
| 0.6-0.7 | 1976 | 0.625 | 0.725 |
| 0.7-0.8 | 31 | 0.716 | 0.903 |

## Most useful features (average gain)

- dist_ema9: 358.56
- dist_ema21: 191.48
- lower_wick_pct: 144.74
- log_ret_1: 123.25
- upper_wick_pct: 119.77
- stoch_k: 114.22
- ret_1: 107.74
- rsi14: 98.99

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 45 | 2026-06-04 to 2026-06-11 |  | 16.9% | 57.0% | 46.9% | 0.2478 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 30.7% | 61.5% | 47.3% | 0.2458 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 45.5% | 65.3% | 43.8% | 0.2407 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 46.7% | 63.7% | 44.7% | 0.2418 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 45.1% | 66.9% | 44.1% | 0.2383 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 47.9% | 68.1% | 43.0% | 0.2366 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 45.1% | 68.8% | 43.3% | 0.2374 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 59.6% | 71.4% | 42.1% | 0.2279 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 61.8% | 70.1% | 43.0% | 0.2273 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 64.0% | 75.6% | 40.4% | 0.2201 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 65.6% | 74.1% | 39.1% | 0.2204 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 46.8% | 54.6% | 50.5% | 0.2498 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 27.9% | 61.9% | 47.5% | 0.2458 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 18.7% | 61.4% | 47.6% | 0.2466 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 40.7% | 58.9% | 46.2% | 0.2451 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 24.9% | 53.1% | 50.6% | 0.2513 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 12.7% | 50.7% | 50.1% | 0.2511 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 17.9% | 58.4% | 49.2% | 0.2479 | 0.2500 |
