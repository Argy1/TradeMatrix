# Backtest UNI 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 56571 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.3% | naive 49.6%, reverse 50.4%, always-up 49.6%, always-down 50.4% |
| Flat candles (close equal to the previous close) | 6.5% | |
| Coverage (share of non-neutral calls) | 17.2% | 100% |
| Brier score (lower is better) | 0.2506 | base rate 0.2500 |
| Log loss | 0.6944 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4315 / 52.1% / 8.0% | |
| Down calls: n / precision / recall | 5176 / 52.5% / 9.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.59% (1.85% to 5.64%)
- Accuracy minus the best simple rule: 2.11% (0.34% to 4.03%)
- Brier improvement over base rate: -0.00061 (-0.00097 to -0.00027)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -87.02 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -165.55 |
| Buy and hold | 183.1% | -30.4% | 3.37 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 559 | 0.378 | 0.428 |
| 0.4-0.5 | 29140 | 0.472 | 0.490 |
| 0.5-0.6 | 26323 | 0.526 | 0.504 |
| 0.6-0.7 | 549 | 0.617 | 0.526 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 8.8% | 50.9% | 47.7% | 0.2496 | 0.2501 |
| 46 | 2026-06-11 to 2026-06-18 |  | 17.4% | 54.5% | 49.5% | 0.2504 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 21.4% | 52.1% | 49.0% | 0.2501 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 25.0% | 54.6% | 49.6% | 0.2496 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 21.9% | 51.7% | 50.3% | 0.2511 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 17.7% | 50.1% | 50.6% | 0.2516 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 17.5% | 52.0% | 48.7% | 0.2507 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 29.6% | 50.5% | 49.4% | 0.2514 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 33.3% | 52.2% | 50.2% | 0.2521 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 34.1% | 52.7% | 49.5% | 0.2510 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 37.1% | 52.1% | 49.3% | 0.2520 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 20.4% | 51.9% | 50.2% | 0.2503 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 4.9% | 56.9% | 49.6% | 0.2502 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 2.6% | 64.4% | 48.6% | 0.2498 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 9.0% | 50.3% | 50.4% | 0.2507 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 4.7% | 54.8% | 51.6% | 0.2507 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 1.6% | 59.6% | 49.1% | 0.2501 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 1.8% | 46.4% | 49.6% | 0.2497 | 0.2500 |
