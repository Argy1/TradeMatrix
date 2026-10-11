# Backtest BTC 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 59791 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 51.0% | naive 49.4%, always-up 49.8%, always-down 50.2% |
| Flat candles (close equal to the previous close) | 1.1% | |
| Coverage (share of non-neutral calls) | 10.5% | 100% |
| Brier score (lower is better) | 0.2503 | base rate 0.2500 |
| Log loss | 0.6937 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3019 / 50.5% / 5.1% | |
| Down calls: n / precision / recall | 3160 / 51.4% / 5.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 1.36% (-0.57% to 3.20%)
- Accuracy minus the best simple rule: 0.18% (-1.56% to 1.77%)
- Brier improvement over base rate: -0.00027 (-0.00068 to 0.00012)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -99.9% | -99.9% | -111.13 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -317.00 |
| Buy and hold | 29.0% | -13.6% | 2.09 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 7 | 0.286 | 0.571 |
| 0.3-0.4 | 257 | 0.381 | 0.514 |
| 0.4-0.5 | 32362 | 0.476 | 0.487 |
| 0.5-0.6 | 26806 | 0.523 | 0.510 |
| 0.6-0.7 | 345 | 0.627 | 0.542 |
| 0.7-0.8 | 14 | 0.721 | 0.857 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 1.7% | 49.1% | 48.7% | 0.2488 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 4.0% | 55.6% | 47.0% | 0.2492 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 9.8% | 50.8% | 50.2% | 0.2508 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 9.3% | 55.4% | 47.9% | 0.2491 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 9.7% | 52.8% | 48.1% | 0.2499 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 8.1% | 50.6% | 48.9% | 0.2498 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 6.0% | 51.7% | 50.1% | 0.2498 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 17.7% | 49.5% | 50.5% | 0.2508 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 21.5% | 53.1% | 48.3% | 0.2498 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 21.5% | 49.7% | 49.8% | 0.2515 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 27.8% | 50.9% | 49.9% | 0.2518 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 18.2% | 50.5% | 50.2% | 0.2514 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 5.2% | 55.0% | 50.3% | 0.2504 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 3.0% | 44.9% | 49.3% | 0.2500 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 10.8% | 48.0% | 49.5% | 0.2514 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 6.2% | 51.0% | 50.5% | 0.2505 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 4.2% | 42.0% | 51.1% | 0.2506 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 4.7% | 53.1% | 48.9% | 0.2493 | 0.2500 |
