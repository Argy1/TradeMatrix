# Backtest ADA 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 45795 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.7% | naive 48.5%, always-up 49.6%, always-down 50.4% |
| Flat candles (close equal to the previous close) | 12.6% | |
| Coverage (share of non-neutral calls) | 21.8% | 100% |
| Brier score (lower is better) | 0.2487 | base rate 0.2500 |
| Log loss | 0.6904 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4677 / 57.4% / 11.8% | |
| Down calls: n / precision / recall | 5201 / 56.1% / 12.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.15% (6.98% to 9.17%)
- Accuracy minus the best simple rule: 6.07% (5.09% to 6.88%)
- Brier improvement over base rate: 0.00135 (0.00086 to 0.00185)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -76.14 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -139.49 |
| Buy and hold | 2.5% | -51.9% | 0.44 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.286 | 0.000 |
| 0.3-0.4 | 587 | 0.381 | 0.422 |
| 0.4-0.5 | 23621 | 0.469 | 0.469 |
| 0.5-0.6 | 21044 | 0.530 | 0.525 |
| 0.6-0.7 | 540 | 0.620 | 0.617 |
| 0.7-0.8 | 2 | 0.709 | 1.000 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 29.9% | 54.9% | 49.4% | 0.2493 | 0.2499 |
| 30 | 2026-04-19 to 2026-05-03 |  | 26.9% | 58.8% | 47.7% | 0.2469 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 38.1% | 56.1% | 48.0% | 0.2485 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 25.5% | 57.5% | 49.0% | 0.2490 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 13.0% | 53.5% | 49.4% | 0.2502 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 15.7% | 56.8% | 48.0% | 0.2488 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 18.4% | 56.1% | 47.5% | 0.2486 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 20.3% | 57.6% | 48.2% | 0.2480 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 24.9% | 58.9% | 48.8% | 0.2469 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 30.9% | 57.1% | 46.4% | 0.2481 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 19.2% | 56.4% | 48.6% | 0.2492 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 12.4% | 55.7% | 50.2% | 0.2492 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 8.1% | 56.9% | 49.3% | 0.2495 | 0.2500 |
