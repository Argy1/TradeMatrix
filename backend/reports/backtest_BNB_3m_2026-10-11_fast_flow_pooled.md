# Backtest BNB 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 59682 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 51.0% | naive 49.8%, reverse 50.2%, always-up 50.0%, always-down 50.0% |
| Flat candles (close equal to the previous close) | 1.3% | |
| Coverage (share of non-neutral calls) | 10.0% | 100% |
| Brier score (lower is better) | 0.2504 | base rate 0.2500 |
| Log loss | 0.6939 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3241 / 51.7% / 5.6% | |
| Down calls: n / precision / recall | 2703 / 50.2% / 4.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 1.51% (-0.15% to 3.12%)
- Accuracy minus the best simple rule: 0.25% (-1.05% to 1.49%)
- Brier improvement over base rate: -0.00038 (-0.00074 to -0.00003)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -99.9% | -99.9% | -107.86 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -314.58 |
| Buy and hold | 27.0% | -14.7% | 1.96 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 201 | 0.385 | 0.488 |
| 0.4-0.5 | 31113 | 0.477 | 0.491 |
| 0.5-0.6 | 28029 | 0.523 | 0.509 |
| 0.6-0.7 | 330 | 0.620 | 0.579 |
| 0.7-0.8 | 9 | 0.735 | 0.444 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 1.5% | 57.1% | 48.1% | 0.2487 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 6.5% | 50.0% | 49.8% | 0.2505 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 9.9% | 52.0% | 48.9% | 0.2500 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 10.7% | 54.1% | 48.8% | 0.2500 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 8.4% | 50.7% | 50.4% | 0.2504 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 8.5% | 52.2% | 49.9% | 0.2501 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 7.3% | 52.7% | 49.2% | 0.2497 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 15.8% | 48.9% | 49.8% | 0.2508 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 21.4% | 52.7% | 47.5% | 0.2501 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 18.3% | 52.2% | 49.6% | 0.2511 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 25.0% | 50.9% | 49.8% | 0.2520 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 15.8% | 49.1% | 52.1% | 0.2516 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 6.0% | 48.8% | 51.2% | 0.2507 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 3.6% | 55.4% | 49.7% | 0.2499 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 10.0% | 48.3% | 50.1% | 0.2506 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 5.6% | 44.9% | 51.3% | 0.2512 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 3.1% | 50.5% | 49.8% | 0.2497 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 2.7% | 52.2% | 49.7% | 0.2499 | 0.2500 |
