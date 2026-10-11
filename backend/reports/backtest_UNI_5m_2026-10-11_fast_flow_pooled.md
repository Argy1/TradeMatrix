# Backtest UNI 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 49232 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.8% | naive 48.8%, always-up 50.0%, always-down 50.0% |
| Flat candles (close equal to the previous close) | 6.1% | |
| Coverage (share of non-neutral calls) | 19.2% | 100% |
| Brier score (lower is better) | 0.2497 | base rate 0.2500 |
| Log loss | 0.6927 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4353 / 53.8% / 9.5% | |
| Down calls: n / precision / recall | 5023 / 53.7% / 11.0% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 4.89% (3.96% to 5.83%)
- Accuracy minus the best simple rule: 2.91% (2.20% to 3.62%)
- Brier improvement over base rate: 0.00027 (0.00001 to 0.00054)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -58.53 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -113.35 |
| Buy and hold | 193.2% | -44.2% | 2.75 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 439 | 0.384 | 0.474 |
| 0.4-0.5 | 25740 | 0.470 | 0.484 |
| 0.5-0.6 | 22624 | 0.529 | 0.517 |
| 0.6-0.7 | 428 | 0.620 | 0.584 |
| 0.7-0.8 | 1 | 0.711 | 0.000 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 31.8% | 53.3% | 49.4% | 0.2500 | 0.2501 |
| 30 | 2026-04-19 to 2026-05-03 |  | 27.2% | 54.5% | 47.4% | 0.2489 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 38.2% | 53.8% | 48.0% | 0.2503 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 27.1% | 56.0% | 49.1% | 0.2488 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 11.0% | 55.0% | 48.9% | 0.2497 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 12.5% | 53.1% | 49.0% | 0.2502 | 0.2501 |
| 35 | 2026-06-28 to 2026-07-12 |  | 16.0% | 52.5% | 48.8% | 0.2499 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 12.8% | 51.5% | 49.1% | 0.2503 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 21.9% | 52.7% | 49.7% | 0.2500 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 26.7% | 54.6% | 48.1% | 0.2492 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 12.9% | 52.6% | 49.3% | 0.2503 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 8.6% | 51.8% | 48.2% | 0.2498 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 3.3% | 56.2% | 48.8% | 0.2495 | 0.2500 |
