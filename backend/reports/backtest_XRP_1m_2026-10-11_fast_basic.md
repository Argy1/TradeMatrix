# Backtest XRP 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 128592 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.1% | naive 50.0%, reverse 50.0%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 8.9% | |
| Coverage (share of non-neutral calls) | 2.7% | 100% |
| Brier score (lower is better) | 0.2500 | base rate 0.2500 |
| Log loss | 0.6932 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1578 / 53.2% / 1.3% | |
| Down calls: n / precision / recall | 2011 / 51.3% / 1.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 12.71% (5.23% to 23.22%)
- Accuracy minus the best simple rule: 11.39% (3.77% to 22.03%)
- Brier improvement over base rate: 0.00001 (-0.00028 to 0.00025)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -96.9% | -96.9% | -48.16 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -551.13 |
| Buy and hold | 35.5% | -26.1% | 2.03 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 51 | 0.389 | 0.510 |
| 0.4-0.5 | 74524 | 0.490 | 0.495 |
| 0.5-0.6 | 53886 | 0.513 | 0.505 |
| 0.6-0.7 | 131 | 0.615 | 0.496 |

## Most useful features (average gain)

- dist_ema9: 18.21
- dist_ema21: 13.45
- rsi14: 12.98
- bb_percent_b: 12.48
- lower_wick_pct: 12.17
- log_ret_1: 10.81
- dist_ema50: 10.75
- stoch_k: 10.68

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 511 | 0.3% | 54.5% | 48.6% | 0.2499 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 136 | 0.6% | 58.6% | 49.0% | 0.2496 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 143 | 1.9% | 56.0% | 50.0% | 0.2498 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 136 | 0.3% | 73.1% | 50.1% | 0.2503 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 115 | 2.2% | 55.1% | 49.4% | 0.2495 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 218 | 7.1% | 55.3% | 49.5% | 0.2499 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 416 | 3.3% | 57.8% | 49.1% | 0.2492 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 370 | 22.2% | 49.5% | 49.8% | 0.2515 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 265 | 0.0% | n/a | 51.5% | 0.2500 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 1 | 0.0% | n/a | 50.0% | 0.2500 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 5 | 0.0% | n/a | 50.6% | 0.2501 | 0.2500 |
| 39 | 2026-09-16 to 2026-09-23 | 40 | 0.0% | n/a | 50.6% | 0.2500 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 1 | 0.0% | n/a | 51.0% | 0.2500 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 569 | 0.0% | 100.0% | 50.0% | 0.2500 | 0.2500 |
