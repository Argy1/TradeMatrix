# Backtest LINK 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 129024 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.7% | naive 50.1%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 8.6% | |
| Coverage (share of non-neutral calls) | 1.4% | 100% |
| Brier score (lower is better) | 0.2500 | base rate 0.2500 |
| Log loss | 0.6931 | coin flip 0.6931 |
| Up calls: n / precision / recall | 635 / 53.1% / 0.5% | |
| Down calls: n / precision / recall | 1152 / 52.5% / 0.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.49% (0.92% to 6.12%)
- Accuracy minus the best simple rule: 2.78% (0.19% to 5.56%)
- Brier improvement over base rate: 0.00001 (-0.00011 to 0.00013)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -79.3% | -79.4% | -48.57 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -545.98 |
| Buy and hold | 80.7% | -22.3% | 3.65 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 71 | 0.386 | 0.465 |
| 0.4-0.5 | 71879 | 0.490 | 0.493 |
| 0.5-0.6 | 57039 | 0.511 | 0.506 |
| 0.6-0.7 | 35 | 0.614 | 0.486 |

## Most useful features (average gain)

- dist_ema9: 58.82
- log_ret_1: 57.87
- ret_1: 46.93
- stoch_k: 42.42
- upper_wick_pct: 34.74
- btc_ret_1: 33.51
- lower_wick_pct: 31.63
- vol_ratio_20: 29.64

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 7 | 1.6% | 52.8% | 48.1% | 0.2497 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 30 | 3.6% | 47.7% | 50.0% | 0.2504 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 30 | 0.0% | n/a | 50.7% | 0.2500 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 11 | 0.0% | n/a | 49.8% | 0.2500 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 338 | 4.1% | 55.4% | 49.8% | 0.2496 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 391 | 1.6% | 60.5% | 50.4% | 0.2497 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 202 | 3.6% | 52.2% | 49.6% | 0.2500 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 201 | 0.0% | 50.0% | 49.5% | 0.2502 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 29 | 0.0% | n/a | 52.0% | 0.2500 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 5 | 0.0% | n/a | 48.8% | 0.2500 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 1 | 0.0% | n/a | 49.7% | 0.2500 | 0.2500 |
| 39 | 2026-09-16 to 2026-09-23 | 20 | 0.0% | n/a | 50.5% | 0.2499 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 301 | 4.5% | 51.7% | 51.7% | 0.2503 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 443 | 0.1% | 57.1% | 50.4% | 0.2499 | 0.2500 |
