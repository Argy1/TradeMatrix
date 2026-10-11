# Backtest AVAX 30m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-03 to 2026-10-02, 13 walk-forward folds, 8315 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.2% | naive 48.3%, always-up 49.8%, always-down 50.2% |
| Flat candles (close equal to the previous close) | 4.8% | |
| Coverage (share of non-neutral calls) | 5.3% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2500 |
| Log loss | 0.6922 | coin flip 0.6931 |
| Up calls: n / precision / recall | 151 / 53.6% / 2.0% | |
| Down calls: n / precision / recall | 281 / 57.7% / 3.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.33% (1.81% to 14.74%)
- Accuracy minus the best simple rule: 4.94% (-1.12% to 10.65%)
- Brier improvement over base rate: 0.00046 (-0.00011 to 0.00104)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -24.0% | -25.7% | -4.33 |
| Naive (hold after an up candle) | -99.8% | -99.9% | -25.45 |
| Buy and hold | 22.4% | -45.1% | 0.93 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 5 | 0.395 | 0.400 |
| 0.4-0.5 | 4187 | 0.479 | 0.479 |
| 0.5-0.6 | 4118 | 0.518 | 0.518 |
| 0.6-0.7 | 5 | 0.610 | 0.600 |

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
| 48 | 2026-04-03 to 2026-04-17 |  | 4.8% | 63.0% | 54.3% | 0.2505 | 0.2499 |
| 49 | 2026-04-17 to 2026-05-01 |  | 8.6% | 60.0% | 44.5% | 0.2491 | 0.2500 |
| 50 | 2026-05-01 to 2026-05-15 |  | 8.6% | 59.3% | 48.9% | 0.2483 | 0.2502 |
| 51 | 2026-05-15 to 2026-05-29 |  | 3.3% | 38.9% | 47.2% | 0.2506 | 0.2498 |
| 52 | 2026-05-29 to 2026-06-12 |  | 1.3% | 44.4% | 49.5% | 0.2490 | 0.2500 |
| 53 | 2026-06-12 to 2026-06-26 |  | 5.1% | 36.4% | 49.5% | 0.2505 | 0.2501 |
| 54 | 2026-06-26 to 2026-07-10 |  | 2.8% | 61.1% | 50.1% | 0.2492 | 0.2500 |
| 55 | 2026-07-10 to 2026-07-24 |  | 1.3% | 55.6% | 43.7% | 0.2490 | 0.2499 |
| 56 | 2026-07-24 to 2026-08-07 |  | 1.3% | 77.8% | 46.1% | 0.2482 | 0.2500 |
| 57 | 2026-08-07 to 2026-08-21 |  | 14.0% | 52.2% | 49.0% | 0.2507 | 0.2500 |
| 58 | 2026-08-21 to 2026-09-04 |  | 5.2% | 67.6% | 44.6% | 0.2483 | 0.2501 |
| 59 | 2026-09-04 to 2026-09-18 |  | 5.7% | 64.9% | 48.0% | 0.2494 | 0.2500 |
| 60 | 2026-09-18 to 2026-10-02 |  | 6.4% | 54.8% | 52.0% | 0.2512 | 0.2500 |
