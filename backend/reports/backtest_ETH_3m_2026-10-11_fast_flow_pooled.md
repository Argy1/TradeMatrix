# Backtest ETH 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 60091 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.9% | naive 49.0%, always-up 50.1%, always-down 49.9% |
| Flat candles (close equal to the previous close) | 0.6% | |
| Coverage (share of non-neutral calls) | 7.8% | 100% |
| Brier score (lower is better) | 0.2496 | base rate 0.2500 |
| Log loss | 0.6924 | coin flip 0.6931 |
| Up calls: n / precision / recall | 2591 / 54.5% / 4.7% | |
| Down calls: n / precision / recall | 2033 / 53.3% / 3.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 4.26% (2.01% to 6.41%)
- Accuracy minus the best simple rule: 2.61% (0.21% to 4.79%)
- Brier improvement over base rate: 0.00039 (0.00017 to 0.00061)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -99.7% | -99.7% | -81.52 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -275.39 |
| Buy and hold | 43.4% | -18.2% | 2.28 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 157 | 0.384 | 0.452 |
| 0.4-0.5 | 32151 | 0.479 | 0.485 |
| 0.5-0.6 | 27548 | 0.522 | 0.519 |
| 0.6-0.7 | 222 | 0.626 | 0.613 |
| 0.7-0.8 | 13 | 0.731 | 0.538 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 1.0% | 39.4% | 47.0% | 0.2490 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 3.3% | 55.0% | 47.5% | 0.2491 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 7.5% | 51.8% | 48.7% | 0.2494 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 6.4% | 53.1% | 48.2% | 0.2489 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 5.7% | 55.2% | 48.7% | 0.2495 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 5.7% | 57.5% | 50.2% | 0.2499 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 3.3% | 51.8% | 49.6% | 0.2492 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 12.4% | 56.0% | 47.8% | 0.2491 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 16.9% | 56.1% | 48.4% | 0.2498 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 17.9% | 52.8% | 48.8% | 0.2498 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 22.0% | 53.5% | 48.8% | 0.2505 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 12.7% | 52.9% | 51.4% | 0.2497 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 5.0% | 53.9% | 49.3% | 0.2500 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 2.8% | 65.6% | 49.2% | 0.2489 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 8.7% | 53.1% | 48.7% | 0.2501 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 3.5% | 47.0% | 49.8% | 0.2502 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 1.9% | 52.3% | 50.4% | 0.2502 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 2.9% | 51.5% | 49.4% | 0.2497 | 0.2500 |
