# Backtest DOT 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 7720 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 51.5% | naive 48.4%, reverse 51.6%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 11.6% | |
| Coverage (share of non-neutral calls) | 5.6% | 100% |
| Brier score (lower is better) | 0.2494 | base rate 0.2500 |
| Log loss | 0.6920 | coin flip 0.6931 |
| Up calls: n / precision / recall | 172 / 47.7% / 2.1% | |
| Down calls: n / precision / recall | 269 / 53.9% / 3.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.30% (-0.79% to 18.52%)
- Accuracy minus the best simple rule: 4.57% (-4.83% to 15.33%)
- Brier improvement over base rate: 0.00060 (0.00005 to 0.00116)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -26.9% | -28.9% | -5.31 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -27.29 |
| Buy and hold | -2.8% | -49.1% | 0.29 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 2 | 0.386 | 0.500 |
| 0.4-0.5 | 3797 | 0.479 | 0.475 |
| 0.5-0.6 | 3915 | 0.518 | 0.522 |
| 0.6-0.7 | 6 | 0.627 | 0.833 |

## Most useful features (average gain)

- dist_ema9: 44.72
- ret_3: 41.67
- log_ret_1: 35.31
- ret_1: 33.70
- ret_6: 32.26
- hour_cos: 30.26
- hour_sin: 29.33
- btc_ret_1: 28.99

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 48 | 2026-04-03 to 2026-04-17 |  | 5.5% | 43.2% | 50.3% | 0.2501 | 0.2500 |
| 49 | 2026-04-17 to 2026-05-01 |  | 8.6% | 60.8% | 47.2% | 0.2494 | 0.2499 |
| 50 | 2026-05-01 to 2026-05-15 |  | 8.3% | 49.0% | 48.8% | 0.2499 | 0.2501 |
| 51 | 2026-05-15 to 2026-05-29 |  | 4.0% | 25.9% | 48.1% | 0.2510 | 0.2499 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.3% | 100.0% | 50.8% | 0.2485 | 0.2501 |
| 53 | 2026-06-12 to 2026-06-26 |  | 6.0% | 58.3% | 47.0% | 0.2490 | 0.2500 |
| 54 | 2026-06-26 to 2026-07-10 |  | 2.4% | 68.8% | 50.3% | 0.2499 | 0.2500 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.9% | 40.0% | 46.3% | 0.2483 | 0.2499 |
| 56 | 2026-07-24 to 2026-08-07 |  | 0.7% | 80.0% | 47.2% | 0.2477 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 16.1% | 48.3% | 48.5% | 0.2509 | 0.2501 |
| 58 | 2026-08-21 to 2026-09-04 |  | 5.4% | 63.6% | 48.3% | 0.2479 | 0.2500 |
| 59 | 2026-09-04 to 2026-09-18 |  | 9.2% | 49.1% | 50.6% | 0.2501 | 0.2500 |
| 60 | 2026-09-18 to 2026-10-02 |  | 5.8% | 50.0% | 45.6% | 0.2497 | 0.2500 |
