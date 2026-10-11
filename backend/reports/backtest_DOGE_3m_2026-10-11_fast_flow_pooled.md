# Backtest DOGE 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 56830 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.2% | naive 49.6%, always-up 50.0%, always-down 50.0% |
| Flat candles (close equal to the previous close) | 6.0% | |
| Coverage (share of non-neutral calls) | 12.1% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2500 |
| Log loss | 0.6928 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3377 / 53.8% / 6.4% | |
| Down calls: n / precision / recall | 3387 / 52.7% / 6.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.12% (0.91% to 5.03%)
- Accuracy minus the best simple rule: 1.93% (-0.47% to 3.85%)
- Brier improvement over base rate: 0.00017 (-0.00007 to 0.00042)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -98.02 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -242.31 |
| Buy and hold | -3.2% | -25.8% | 0.18 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 2 | 0.282 | 0.500 |
| 0.3-0.4 | 314 | 0.383 | 0.404 |
| 0.4-0.5 | 30215 | 0.476 | 0.486 |
| 0.5-0.6 | 25830 | 0.524 | 0.517 |
| 0.6-0.7 | 452 | 0.623 | 0.602 |
| 0.7-0.8 | 17 | 0.727 | 0.471 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 2.3% | 38.4% | 48.0% | 0.2498 | 0.2501 |
| 46 | 2026-06-11 to 2026-06-18 |  | 7.9% | 50.6% | 49.8% | 0.2495 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 14.6% | 52.5% | 49.8% | 0.2494 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 14.3% | 52.0% | 49.4% | 0.2503 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 12.0% | 50.3% | 50.3% | 0.2500 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 11.5% | 53.4% | 50.7% | 0.2507 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 10.8% | 52.8% | 49.5% | 0.2494 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 18.6% | 54.7% | 48.6% | 0.2491 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 25.1% | 54.3% | 50.1% | 0.2501 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 26.7% | 53.5% | 49.9% | 0.2501 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 30.7% | 55.6% | 48.9% | 0.2491 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 16.7% | 51.9% | 50.7% | 0.2505 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 4.9% | 51.2% | 49.1% | 0.2502 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 3.1% | 60.4% | 50.2% | 0.2492 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 9.3% | 55.6% | 48.5% | 0.2497 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 4.8% | 47.8% | 51.0% | 0.2507 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 1.8% | 57.6% | 49.8% | 0.2498 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 2.9% | 56.8% | 48.9% | 0.2494 | 0.2500 |
