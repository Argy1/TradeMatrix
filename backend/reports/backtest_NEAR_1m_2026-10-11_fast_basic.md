# Backtest NEAR 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 109553 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 58.2% | naive 48.5%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 22.4% | |
| Coverage (share of non-neutral calls) | 22.1% | 100% |
| Brier score (lower is better) | 0.2482 | base rate 0.2500 |
| Log loss | 0.6895 | coin flip 0.6931 |
| Up calls: n / precision / recall | 11965 / 58.8% / 12.9% | |
| Down calls: n / precision / recall | 9310 / 57.3% / 9.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.67% (6.60% to 12.62%)
- Accuracy minus the best simple rule: 6.47% (3.95% to 8.87%)
- Brier improvement over base rate: 0.00218 (0.00078 to 0.00372)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -227.60 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -406.53 |
| Buy and hold | 176.4% | -27.0% | 3.93 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 40 | 0.285 | 0.325 |
| 0.3-0.4 | 2026 | 0.374 | 0.410 |
| 0.4-0.5 | 66701 | 0.479 | 0.477 |
| 0.5-0.6 | 36623 | 0.530 | 0.527 |
| 0.6-0.7 | 3918 | 0.637 | 0.624 |
| 0.7-0.8 | 245 | 0.720 | 0.743 |

## Most useful features (average gain)

- log_ret_1: 38.66
- stoch_k: 36.10
- ret_1: 29.24
- upper_wick_pct: 25.26
- lower_wick_pct: 21.50
- dist_ema9: 19.05
- vol_ratio_20: 18.58
- btc_ret_1: 18.17

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 133 | 9.6% | 55.1% | 47.0% | 0.2491 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 109 | 12.3% | 56.4% | 47.5% | 0.2484 | 0.2499 |
| 30 | 2026-07-15 to 2026-07-22 | 263 | 21.5% | 62.5% | 46.6% | 0.2452 | 0.2499 |
| 31 | 2026-07-22 to 2026-07-29 | 363 | 40.9% | 61.6% | 46.4% | 0.2439 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 786 | 54.1% | 57.5% | 46.9% | 0.2464 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 775 | 44.8% | 58.9% | 45.9% | 0.2458 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 762 | 51.7% | 62.3% | 45.3% | 0.2411 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 338 | 47.3% | 53.6% | 48.2% | 0.2511 | 0.2499 |
| 36 | 2026-08-26 to 2026-09-02 | 773 | 15.8% | 57.9% | 49.1% | 0.2488 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 84 | 11.3% | 52.2% | 49.3% | 0.2501 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 233 | 0.0% | 50.0% | 49.2% | 0.2501 | 0.2502 |
| 39 | 2026-09-16 to 2026-09-23 | 17 | 0.0% | n/a | 51.3% | 0.2503 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 6 | 0.0% | n/a | 51.4% | 0.2500 | 0.2501 |
| 41 | 2026-09-30 to 2026-10-07 | 1 | 0.0% | n/a | 50.4% | 0.2496 | 0.2501 |
