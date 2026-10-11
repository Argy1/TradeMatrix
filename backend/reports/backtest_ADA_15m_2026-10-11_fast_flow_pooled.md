# Backtest ADA 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 14886 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.0% | naive 48.0%, always-up 49.5%, always-down 50.5% |
| Flat candles (close equal to the previous close) | 7.7% | |
| Coverage (share of non-neutral calls) | 17.2% | 100% |
| Brier score (lower is better) | 0.2490 | base rate 0.2500 |
| Log loss | 0.6911 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1218 / 54.8% / 9.1% | |
| Down calls: n / precision / recall | 1368 / 55.3% / 10.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 4.91% (-1.62% to 9.38%)
- Accuracy minus the best simple rule: 1.49% (-4.99% to 5.65%)
- Brier improvement over base rate: 0.00100 (0.00040 to 0.00157)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -91.8% | -91.8% | -22.25 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -51.50 |
| Buy and hold | 5.9% | -51.8% | 0.54 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.271 | 0.000 |
| 0.3-0.4 | 151 | 0.387 | 0.384 |
| 0.4-0.5 | 7621 | 0.471 | 0.471 |
| 0.5-0.6 | 7095 | 0.527 | 0.523 |
| 0.6-0.7 | 18 | 0.610 | 0.500 |

## Most useful features (average gain)

- dist_ema9: 148.33
- log_ret_1: 106.96
- ret_1: 105.80
- stoch_k: 71.16
- dist_ema21: 47.48
- btc_ret_1: 45.09
- ret_6: 40.41
- rsi14: 35.17

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51 | 2026-04-12 to 2026-04-26 |  | 38.0% | 57.4% | 46.7% | 0.2482 | 0.2501 |
| 52 | 2026-04-26 to 2026-05-10 |  | 8.0% | 61.2% | 45.6% | 0.2476 | 0.2504 |
| 53 | 2026-05-10 to 2026-05-24 |  | 31.1% | 53.4% | 48.6% | 0.2499 | 0.2497 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.4% | 51.6% | 50.6% | 0.2502 | 0.2498 |
| 55 | 2026-06-07 to 2026-06-21 |  | 0.9% | 55.6% | 47.2% | 0.2487 | 0.2499 |
| 56 | 2026-06-21 to 2026-07-05 |  | 31.5% | 53.2% | 48.9% | 0.2505 | 0.2500 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.7% | 22.2% | 47.8% | 0.2486 | 0.2499 |
| 58 | 2026-07-19 to 2026-08-02 |  | 26.5% | 54.6% | 47.8% | 0.2494 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 10.9% | 54.3% | 47.7% | 0.2475 | 0.2497 |
| 60 | 2026-08-16 to 2026-08-30 |  | 37.3% | 53.5% | 47.9% | 0.2499 | 0.2500 |
| 61 | 2026-08-30 to 2026-09-13 |  | 6.1% | 58.2% | 49.6% | 0.2487 | 0.2500 |
| 62 | 2026-09-13 to 2026-09-27 |  | 12.6% | 59.7% | 47.7% | 0.2485 | 0.2501 |
