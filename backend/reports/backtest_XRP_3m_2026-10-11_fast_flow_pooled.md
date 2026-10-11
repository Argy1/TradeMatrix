# Backtest XRP 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 57947 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.0% | naive 49.2%, always-up 49.5%, always-down 50.5% |
| Flat candles (close equal to the previous close) | 4.2% | |
| Coverage (share of non-neutral calls) | 11.0% | 100% |
| Brier score (lower is better) | 0.2499 | base rate 0.2500 |
| Log loss | 0.6930 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3353 / 51.7% / 6.0% | |
| Down calls: n / precision / recall | 2907 / 54.5% / 5.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.46% (2.08% to 4.82%)
- Accuracy minus the best simple rule: 1.80% (0.62% to 2.93%)
- Brier improvement over base rate: 0.00009 (-0.00020 to 0.00036)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -87.30 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -239.51 |
| Buy and hold | 17.7% | -26.0% | 1.04 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.284 | 1.000 |
| 0.3-0.4 | 244 | 0.382 | 0.439 |
| 0.4-0.5 | 30126 | 0.477 | 0.482 |
| 0.5-0.6 | 27193 | 0.524 | 0.508 |
| 0.6-0.7 | 370 | 0.625 | 0.559 |
| 0.7-0.8 | 13 | 0.714 | 0.462 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 2.1% | 48.5% | 48.5% | 0.2497 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 6.9% | 53.8% | 47.5% | 0.2495 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 11.7% | 55.4% | 48.8% | 0.2492 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 12.3% | 52.6% | 49.7% | 0.2500 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 11.1% | 51.7% | 48.8% | 0.2501 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 10.1% | 51.2% | 50.2% | 0.2499 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 8.0% | 56.2% | 49.4% | 0.2493 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 18.5% | 56.6% | 48.6% | 0.2493 | 0.2501 |
| 53 | 2026-07-30 to 2026-08-06 |  | 23.9% | 54.6% | 48.6% | 0.2496 | 0.2501 |
| 54 | 2026-08-06 to 2026-08-13 |  | 22.6% | 51.0% | 50.2% | 0.2510 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 27.5% | 53.6% | 47.4% | 0.2501 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 17.1% | 49.2% | 51.3% | 0.2514 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 4.6% | 49.0% | 48.2% | 0.2499 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 2.7% | 56.7% | 48.8% | 0.2489 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 9.8% | 52.7% | 49.4% | 0.2502 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 4.0% | 51.5% | 51.6% | 0.2502 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 1.8% | 52.6% | 49.8% | 0.2503 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 2.8% | 51.1% | 48.9% | 0.2499 | 0.2500 |
