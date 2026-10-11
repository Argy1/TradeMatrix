# Backtest ETH 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 52243 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.7% | naive 48.3%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 0.3% | |
| Coverage (share of non-neutral calls) | 13.7% | 100% |
| Brier score (lower is better) | 0.2491 | base rate 0.2500 |
| Log loss | 0.6913 | coin flip 0.6931 |
| Up calls: n / precision / recall | 3808 / 56.0% / 8.2% | |
| Down calls: n / precision / recall | 3370 / 55.3% / 7.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.44% (7.06% to 9.79%)
- Accuracy minus the best simple rule: 6.02% (4.64% to 7.43%)
- Brier improvement over base rate: 0.00090 (0.00059 to 0.00119)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -73.03 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -185.40 |
| Buy and hold | 32.1% | -38.5% | 1.36 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 129 | 0.387 | 0.426 |
| 0.4-0.5 | 26992 | 0.474 | 0.477 |
| 0.5-0.6 | 24892 | 0.527 | 0.522 |
| 0.6-0.7 | 230 | 0.620 | 0.626 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 23.0% | 54.6% | 48.6% | 0.2485 | 0.2501 |
| 30 | 2026-04-19 to 2026-05-03 |  | 18.4% | 57.0% | 48.2% | 0.2483 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 31.0% | 54.8% | 47.2% | 0.2490 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 19.5% | 52.1% | 48.9% | 0.2502 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 6.4% | 57.0% | 47.7% | 0.2490 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 7.3% | 60.5% | 48.3% | 0.2488 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 7.7% | 56.9% | 47.3% | 0.2487 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 7.9% | 60.1% | 48.5% | 0.2491 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 17.8% | 54.6% | 48.8% | 0.2494 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 18.7% | 53.8% | 48.2% | 0.2501 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 10.6% | 58.8% | 48.8% | 0.2489 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 6.3% | 58.7% | 49.4% | 0.2489 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 4.2% | 59.2% | 48.4% | 0.2496 | 0.2500 |
