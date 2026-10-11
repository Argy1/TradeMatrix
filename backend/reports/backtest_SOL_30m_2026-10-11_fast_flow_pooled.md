# Backtest SOL 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8592 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.4% | naive 48.6%, reverse 51.4%, always-up 50.3%, always-down 49.7% |
| Flat candles (close equal to the previous close) | 1.6% | |
| Coverage (share of non-neutral calls) | 4.8% | 100% |
| Brier score (lower is better) | 0.2496 | base rate 0.2500 |
| Log loss | 0.6924 | coin flip 0.6931 |
| Up calls: n / precision / recall | 156 / 56.4% / 2.0% | |
| Down calls: n / precision / recall | 261 / 53.3% / 3.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.83% (1.11% to 12.97%)
- Accuracy minus the best simple rule: 3.35% (-2.14% to 9.31%)
- Brier improvement over base rate: 0.00040 (-0.00011 to 0.00090)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -22.8% | -23.1% | -6.29 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -31.06 |
| Buy and hold | 48.8% | -38.0% | 1.68 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 1 | 0.382 | 1.000 |
| 0.4-0.5 | 4185 | 0.479 | 0.481 |
| 0.5-0.6 | 4403 | 0.518 | 0.524 |
| 0.6-0.7 | 3 | 0.608 | 1.000 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 5.1% | 51.5% | 46.7% | 0.2488 | 0.2501 |
| 49 | 2026-04-17 to 2026-05-01 |  | 8.0% | 69.8% | 49.8% | 0.2485 | 0.2500 |
| 50 | 2026-05-01 to 2026-05-15 |  | 6.4% | 48.8% | 52.3% | 0.2503 | 0.2501 |
| 51 | 2026-05-15 to 2026-05-29 |  | 4.0% | 38.5% | 48.9% | 0.2505 | 0.2499 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.3% | 50.0% | 49.9% | 0.2484 | 0.2500 |
| 53 | 2026-06-12 to 2026-06-26 |  | 5.5% | 48.6% | 50.5% | 0.2505 | 0.2501 |
| 54 | 2026-06-26 to 2026-07-10 |  | 2.5% | 47.1% | 50.7% | 0.2495 | 0.2499 |
| 55 | 2026-07-10 to 2026-07-24 |  | 1.0% | 71.4% | 47.2% | 0.2493 | 0.2500 |
| 56 | 2026-07-24 to 2026-08-07 |  | 1.3% | 75.0% | 49.3% | 0.2491 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 15.0% | 51.5% | 46.2% | 0.2509 | 0.2501 |
| 58 | 2026-08-21 to 2026-09-04 |  | 5.4% | 61.1% | 45.3% | 0.2484 | 0.2500 |
| 59 | 2026-09-04 to 2026-09-18 |  | 5.7% | 57.9% | 47.9% | 0.2497 | 0.2501 |
| 60 | 2026-09-18 to 2026-10-02 |  | 2.7% | 50.0% | 47.9% | 0.2513 | 0.2500 |
