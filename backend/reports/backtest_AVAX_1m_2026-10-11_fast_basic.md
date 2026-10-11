# Backtest AVAX 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 125464 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.4% | naive 49.9%, reverse 50.1%, always-up 50.2%, always-down 49.8% |
| Flat candles (close equal to the previous close) | 11.1% | |
| Coverage (share of non-neutral calls) | 2.2% | 100% |
| Brier score (lower is better) | 0.2500 | base rate 0.2500 |
| Log loss | 0.6931 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1666 / 54.5% / 1.4% | |
| Down calls: n / precision / recall | 1100 / 51.7% / 0.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 2.98% (-3.15% to 7.48%)
- Accuracy minus the best simple rule: 1.09% (-4.83% to 5.06%)
- Brier improvement over base rate: 0.00004 (-0.00011 to 0.00019)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -98.5% | -98.5% | -90.77 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -525.13 |
| Buy and hold | 68.0% | -15.4% | 3.04 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 26 | 0.382 | 0.269 |
| 0.4-0.5 | 55652 | 0.490 | 0.497 |
| 0.5-0.6 | 69768 | 0.511 | 0.506 |
| 0.6-0.7 | 18 | 0.631 | 0.500 |

## Most useful features (average gain)

- dist_ema9: 53.62
- log_ret_1: 50.55
- stoch_k: 43.67
- ret_1: 40.11
- bb_bandwidth: 34.43
- vol_ratio_20: 32.87
- dist_ema21: 31.16
- btc_ret_1: 30.22

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 13 | 5.7% | 57.0% | 48.5% | 0.2494 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 25 | 15.3% | 51.1% | 50.6% | 0.2506 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 34 | 0.0% | n/a | 51.1% | 0.2500 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 3 | 0.0% | n/a | 49.9% | 0.2500 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 325 | 0.9% | 58.0% | 49.2% | 0.2494 | 0.2499 |
| 33 | 2026-08-05 to 2026-08-12 | 185 | 5.7% | 55.8% | 49.1% | 0.2498 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 209 | 1.9% | 52.3% | 48.8% | 0.2499 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 330 | 1.5% | 56.1% | 48.8% | 0.2499 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 58 | 0.0% | n/a | 51.7% | 0.2499 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 33 | 0.0% | n/a | 49.4% | 0.2499 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 405 | 0.3% | 35.7% | 50.1% | 0.2504 | 0.2501 |
| 39 | 2026-09-16 to 2026-09-23 | 43 | 0.0% | n/a | 50.3% | 0.2502 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 1 | 0.0% | n/a | 51.3% | 0.2501 | 0.2501 |
| 41 | 2026-09-30 to 2026-10-07 | 11 | 0.0% | n/a | 50.1% | 0.2500 | 0.2500 |
