# Backtest LINK 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 57830 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.0% | naive 49.9%, always-up 50.0%, always-down 50.0% |
| Flat candles (close equal to the previous close) | 4.4% | |
| Coverage (share of non-neutral calls) | 14.2% | 100% |
| Brier score (lower is better) | 0.2506 | base rate 0.2500 |
| Log loss | 0.6943 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3940 / 53.2% / 7.2% | |
| Down calls: n / precision / recall | 4171 / 50.9% / 7.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 1.69% (-0.24% to 3.67%)
- Accuracy minus the best simple rule: 0.82% (-1.06% to 2.78%)
- Brier improvement over base rate: -0.00057 (-0.00082 to -0.00031)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -100.29 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -228.33 |
| Buy and hold | 60.9% | -22.1% | 2.36 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 398 | 0.381 | 0.497 |
| 0.4-0.5 | 30621 | 0.474 | 0.492 |
| 0.5-0.6 | 26266 | 0.525 | 0.509 |
| 0.6-0.7 | 544 | 0.618 | 0.535 |
| 0.7-0.8 | 1 | 0.724 | 0.000 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 3.9% | 50.8% | 50.0% | 0.2497 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 12.5% | 54.2% | 50.6% | 0.2501 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 19.6% | 52.3% | 48.8% | 0.2505 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 19.4% | 51.9% | 49.7% | 0.2506 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 15.7% | 52.3% | 50.3% | 0.2510 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 15.7% | 49.9% | 50.5% | 0.2513 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 12.6% | 48.1% | 49.1% | 0.2508 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 23.1% | 54.4% | 49.6% | 0.2503 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 29.8% | 51.8% | 49.8% | 0.2513 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 27.9% | 51.6% | 50.3% | 0.2514 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 26.9% | 52.1% | 48.3% | 0.2513 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 18.4% | 54.5% | 51.0% | 0.2505 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 5.1% | 50.0% | 50.8% | 0.2506 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 3.8% | 46.3% | 49.3% | 0.2501 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 10.4% | 53.7% | 47.6% | 0.2499 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 5.7% | 47.4% | 50.8% | 0.2509 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 1.7% | 63.2% | 49.9% | 0.2497 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 2.8% | 43.8% | 51.4% | 0.2503 | 0.2500 |
