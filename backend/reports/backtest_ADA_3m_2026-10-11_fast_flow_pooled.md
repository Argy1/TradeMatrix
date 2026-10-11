# Backtest ADA 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 51001 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 58.4% | naive 48.2%, reverse 51.8%, always-up 49.7%, always-down 50.3% |
| Flat candles (close equal to the previous close) | 15.7% | |
| Coverage (share of non-neutral calls) | 23.1% | 100% |
| Brier score (lower is better) | 0.2478 | base rate 0.2500 |
| Log loss | 0.6888 | coin flip 0.6931 |
| Up calls: n / precision / recall | 5350 / 59.2% / 12.5% | |
| Down calls: n / precision / recall | 5982 / 57.7% / 13.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.60% (7.70% to 11.35%)
- Accuracy minus the best simple rule: 5.60% (4.42% to 6.75%)
- Brier improvement over base rate: 0.00227 (0.00138 to 0.00322)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -99.92 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -205.85 |
| Buy and hold | 28.4% | -30.3% | 1.27 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 5 | 0.288 | 0.600 |
| 0.3-0.4 | 980 | 0.376 | 0.374 |
| 0.4-0.5 | 26156 | 0.470 | 0.467 |
| 0.5-0.6 | 22784 | 0.529 | 0.529 |
| 0.6-0.7 | 1070 | 0.621 | 0.641 |
| 0.7-0.8 | 6 | 0.728 | 0.833 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 7.4% | 56.5% | 48.0% | 0.2491 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 19.4% | 58.9% | 48.2% | 0.2478 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 30.8% | 57.6% | 46.3% | 0.2474 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 33.2% | 59.0% | 48.0% | 0.2469 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 24.8% | 59.1% | 47.8% | 0.2473 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 31.4% | 61.8% | 48.0% | 0.2454 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 27.9% | 59.1% | 47.8% | 0.2475 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 40.3% | 61.5% | 45.9% | 0.2433 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 37.6% | 57.5% | 46.5% | 0.2473 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 40.0% | 57.2% | 47.0% | 0.2466 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 46.7% | 60.3% | 46.6% | 0.2441 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 23.0% | 54.0% | 51.2% | 0.2507 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 10.1% | 57.3% | 49.0% | 0.2489 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 6.9% | 57.6% | 48.3% | 0.2488 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 18.5% | 56.1% | 48.5% | 0.2488 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 9.1% | 51.3% | 50.9% | 0.2507 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 4.1% | 52.3% | 49.6% | 0.2503 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 4.8% | 61.9% | 48.6% | 0.2485 | 0.2500 |
