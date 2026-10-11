# Backtest BNB 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 16050 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.7% | naive 48.0%, reverse 52.0%, always-up 50.4%, always-down 49.6% |
| Flat candles (close equal to the previous close) | 0.5% | |
| Coverage (share of non-neutral calls) | 13.1% | 100% |
| Brier score (lower is better) | 0.2498 | base rate 0.2501 |
| Log loss | 0.6928 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1170 / 54.2% / 7.8% | |
| Down calls: n / precision / recall | 931 / 50.8% / 5.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.54% (1.75% to 14.53%)
- Accuracy minus the best simple rule: 3.24% (-2.03% to 9.41%)
- Brier improvement over base rate: 0.00025 (-0.00049 to 0.00085)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -90.4% | -90.4% | -33.60 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -87.11 |
| Buy and hold | 30.6% | -27.1% | 1.65 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 101 | 0.385 | 0.436 |
| 0.4-0.5 | 7516 | 0.475 | 0.486 |
| 0.5-0.6 | 8411 | 0.526 | 0.520 |
| 0.6-0.7 | 22 | 0.611 | 0.773 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 33.3% | 52.6% | 47.5% | 0.2499 | 0.2503 |
| 52 | 2026-04-26 to 2026-05-10 |  | 4.4% | 55.9% | 49.3% | 0.2491 | 0.2504 |
| 53 | 2026-05-10 to 2026-05-24 |  | 31.0% | 51.8% | 49.3% | 0.2514 | 0.2502 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.5% | 38.2% | 48.1% | 0.2497 | 0.2499 |
| 55 | 2026-06-07 to 2026-06-21 |  | 0.5% | 85.7% | 45.8% | 0.2490 | 0.2501 |
| 56 | 2026-06-21 to 2026-07-05 |  | 18.1% | 53.5% | 47.7% | 0.2501 | 0.2500 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.1% | 50.0% | 44.7% | 0.2486 | 0.2500 |
| 58 | 2026-07-19 to 2026-08-02 |  | 14.4% | 53.4% | 48.8% | 0.2497 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 6.3% | 63.5% | 47.0% | 0.2486 | 0.2501 |
| 60 | 2026-08-16 to 2026-08-30 |  | 31.4% | 49.0% | 50.5% | 0.2528 | 0.2500 |
| 61 | 2026-08-30 to 2026-09-13 |  | 6.9% | 54.8% | 49.2% | 0.2496 | 0.2501 |
| 62 | 2026-09-13 to 2026-09-27 |  | 8.0% | 57.9% | 48.2% | 0.2493 | 0.2500 |
