# Backtest XLM 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 49906 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 57.8% | naive 48.0%, reverse 52.0%, always-up 49.2%, always-down 50.8% |
| Flat candles (close equal to the previous close) | 17.5% | |
| Coverage (share of non-neutral calls) | 27.5% | 100% |
| Brier score (lower is better) | 0.2477 | base rate 0.2500 |
| Log loss | 0.6886 | coin flip 0.6931 |
| Up calls: n / precision / recall | 6130 / 58.0% / 14.5% | |
| Down calls: n / precision / recall | 7063 / 57.7% / 16.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.02% (6.49% to 11.51%)
- Accuracy minus the best simple rule: 4.39% (2.91% to 5.83%)
- Brier improvement over base rate: 0.00252 (0.00117 to 0.00400)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -127.38 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -201.94 |
| Buy and hold | -5.5% | -39.2% | 0.24 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 19 | 0.281 | 0.263 |
| 0.3-0.4 | 1467 | 0.373 | 0.365 |
| 0.4-0.5 | 25161 | 0.468 | 0.462 |
| 0.5-0.6 | 21759 | 0.531 | 0.526 |
| 0.6-0.7 | 1489 | 0.623 | 0.619 |
| 0.7-0.8 | 11 | 0.713 | 0.636 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 5.2% | 56.0% | 47.9% | 0.2487 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 16.1% | 55.4% | 47.9% | 0.2490 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 24.6% | 54.4% | 47.3% | 0.2492 | 0.2501 |
| 48 | 2026-06-25 to 2026-07-02 |  | 27.0% | 57.8% | 47.4% | 0.2489 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 19.4% | 56.4% | 47.7% | 0.2475 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 29.3% | 59.5% | 47.6% | 0.2470 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 28.5% | 60.5% | 46.8% | 0.2462 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 42.6% | 61.4% | 47.1% | 0.2437 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 51.2% | 61.0% | 45.8% | 0.2430 | 0.2501 |
| 54 | 2026-08-06 to 2026-08-13 |  | 51.0% | 62.8% | 45.0% | 0.2409 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 54.1% | 62.0% | 44.9% | 0.2421 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 31.0% | 51.0% | 50.0% | 0.2515 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 20.5% | 52.7% | 49.8% | 0.2495 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 15.7% | 59.5% | 47.9% | 0.2475 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 33.2% | 54.9% | 48.0% | 0.2492 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 20.1% | 49.5% | 51.6% | 0.2519 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 9.2% | 50.4% | 49.7% | 0.2510 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 16.7% | 59.4% | 49.9% | 0.2481 | 0.2500 |
