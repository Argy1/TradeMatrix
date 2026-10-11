# Backtest XLM 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8162 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.1% | naive 48.9%, reverse 51.1%, always-up 48.3%, always-down 51.7% |
| Flat candles (close equal to the previous close) | 6.6% | |
| Coverage (share of non-neutral calls) | 5.2% | 100% |
| Brier score (lower is better) | 0.2494 | base rate 0.2499 |
| Log loss | 0.6920 | coin flip 0.6931 |
| Up calls: n / precision / recall | 168 / 54.8% / 2.3% | |
| Down calls: n / precision / recall | 255 / 55.3% / 3.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.48% (1.35% to 16.23%)
- Accuracy minus the best simple rule: 4.82% (-1.61% to 11.82%)
- Brier improvement over base rate: 0.00049 (-0.00020 to 0.00115)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -27.7% | -28.2% | -5.94 |
| Naive (hold after an up candle) | -99.9% | -99.9% | -19.89 |
| Buy and hold | 34.5% | -48.0% | 1.12 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 4 | 0.386 | 0.250 |
| 0.4-0.5 | 3844 | 0.480 | 0.462 |
| 0.5-0.6 | 4306 | 0.518 | 0.503 |
| 0.6-0.7 | 8 | 0.616 | 0.500 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 6.1% | 48.7% | 49.4% | 0.2497 | 0.2500 |
| 49 | 2026-04-17 to 2026-05-01 |  | 10.7% | 55.2% | 48.7% | 0.2515 | 0.2498 |
| 50 | 2026-05-01 to 2026-05-15 |  | 6.1% | 60.0% | 48.4% | 0.2485 | 0.2500 |
| 51 | 2026-05-15 to 2026-05-29 |  | 3.9% | 52.4% | 52.4% | 0.2509 | 0.2499 |
| 52 | 2026-05-29 to 2026-06-12 |  | 0.9% | 66.7% | 49.7% | 0.2500 | 0.2498 |
| 53 | 2026-06-12 to 2026-06-26 |  | 4.5% | 55.2% | 48.8% | 0.2484 | 0.2496 |
| 54 | 2026-06-26 to 2026-07-10 |  | 1.0% | 85.7% | 46.2% | 0.2482 | 0.2498 |
| 55 | 2026-07-10 to 2026-07-24 |  | 0.9% | 33.3% | 49.5% | 0.2498 | 0.2499 |
| 56 | 2026-07-24 to 2026-08-07 |  | 1.3% | 77.8% | 49.1% | 0.2473 | 0.2499 |
| 57 | 2026-08-07 to 2026-08-21 |  | 14.1% | 53.9% | 47.0% | 0.2500 | 0.2500 |
| 58 | 2026-08-21 to 2026-09-04 |  | 4.9% | 54.8% | 47.9% | 0.2481 | 0.2501 |
| 59 | 2026-09-04 to 2026-09-18 |  | 8.2% | 58.0% | 48.3% | 0.2491 | 0.2501 |
| 60 | 2026-09-18 to 2026-10-02 |  | 4.6% | 44.8% | 50.9% | 0.2509 | 0.2500 |
