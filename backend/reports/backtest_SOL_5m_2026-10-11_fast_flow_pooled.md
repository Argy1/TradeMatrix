# Backtest SOL 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 50081 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.7% | naive 48.6%, reverse 51.4%, always-up 50.0%, always-down 50.0% |
| Flat candles (close equal to the previous close) | 4.5% | |
| Coverage (share of non-neutral calls) | 15.3% | 100% |
| Brier score (lower is better) | 0.2494 | base rate 0.2500 |
| Log loss | 0.6919 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3563 / 54.5% / 7.8% | |
| Down calls: n / precision / recall | 4093 / 54.8% / 9.0% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.26% (4.84% to 7.68%)
- Accuracy minus the best simple rule: 3.29% (2.22% to 4.45%)
- Brier improvement over base rate: 0.00062 (0.00027 to 0.00104)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -99.9% | -99.9% | -65.70 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -167.19 |
| Buy and hold | 53.4% | -38.5% | 1.75 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 255 | 0.386 | 0.439 |
| 0.4-0.5 | 26802 | 0.473 | 0.480 |
| 0.5-0.6 | 22788 | 0.527 | 0.524 |
| 0.6-0.7 | 235 | 0.619 | 0.574 |
| 0.7-0.8 | 1 | 0.703 | 1.000 |

## Most useful features (average gain)

- dist_ema9: 222.13
- bb_percent_b: 165.37
- dist_ema21: 133.72
- rsi14: 99.11
- lower_wick_pct: 92.35
- upper_wick_pct: 81.22
- stoch_k: 71.15
- log_ret_1: 59.11

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 29 | 2026-04-05 to 2026-04-19 |  | 23.8% | 56.8% | 47.3% | 0.2478 | 0.2500 |
| 30 | 2026-04-19 to 2026-05-03 |  | 19.4% | 56.4% | 48.0% | 0.2482 | 0.2501 |
| 31 | 2026-05-03 to 2026-05-17 |  | 32.6% | 53.4% | 48.0% | 0.2501 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 18.7% | 52.2% | 50.0% | 0.2502 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 8.4% | 55.4% | 48.5% | 0.2492 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 10.5% | 56.1% | 47.8% | 0.2489 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 10.5% | 52.8% | 47.1% | 0.2494 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 10.7% | 53.0% | 49.1% | 0.2497 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 18.7% | 54.3% | 50.3% | 0.2500 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 22.2% | 54.4% | 48.1% | 0.2496 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 11.8% | 57.8% | 48.6% | 0.2494 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 7.2% | 52.0% | 49.9% | 0.2499 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 4.0% | 58.5% | 49.0% | 0.2496 | 0.2500 |
