# Backtest LTC 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 48308 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.2% | naive 48.8%, always-up 50.4%, always-down 49.6% |
| Flat candles (close equal to the previous close) | 7.8% | |
| Coverage (share of non-neutral calls) | 17.2% | 100% |
| Brier score (lower is better) | 0.2495 | base rate 0.2500 |
| Log loss | 0.6921 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3652 / 56.3% / 8.4% | |
| Down calls: n / precision / recall | 4677 / 54.4% / 10.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.19% (5.06% to 7.30%)
- Accuracy minus the best simple rule: 4.33% (3.32% to 5.41%)
- Brier improvement over base rate: 0.00057 (0.00027 to 0.00093)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -75.32 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -181.31 |
| Buy and hold | 35.2% | -34.9% | 1.39 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 426 | 0.386 | 0.479 |
| 0.4-0.5 | 25928 | 0.471 | 0.487 |
| 0.5-0.6 | 21584 | 0.527 | 0.524 |
| 0.6-0.7 | 370 | 0.622 | 0.557 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 27.5% | 54.2% | 47.9% | 0.2502 | 0.2501 |
| 30 | 2026-04-19 to 2026-05-03 |  | 21.6% | 58.6% | 50.1% | 0.2483 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 34.2% | 54.0% | 48.8% | 0.2494 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 20.9% | 54.4% | 48.1% | 0.2496 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 8.7% | 53.4% | 49.8% | 0.2496 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 11.7% | 55.3% | 48.2% | 0.2498 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 14.6% | 54.9% | 47.9% | 0.2494 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 12.4% | 54.7% | 49.5% | 0.2497 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 20.3% | 58.9% | 49.0% | 0.2480 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 24.9% | 55.8% | 46.6% | 0.2492 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 14.5% | 53.9% | 48.9% | 0.2500 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 8.4% | 51.4% | 48.9% | 0.2500 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 4.3% | 55.3% | 50.7% | 0.2498 | 0.2500 |
