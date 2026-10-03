# Backtest ALL 1d (2026-10-03)

Model settings: `v1` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-11 to 2026-09-30, 8 walk-forward folds, 11520 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.7% | naive 50.1%, always-up 48.7% |
| Coverage (share of non-neutral calls) | 38.5% | 100% |
| Brier score (lower is better) | 0.2508 | base rate 0.2505 |
| Log loss | 0.6947 | coin flip 0.6931 |
| Up calls: n / precision / recall | 114 / 66.7% / 1.4% | |
| Down calls: n / precision / recall | 4320 / 53.3% / 39.0% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.25% (1.39% to 13.61%)
- Brier improvement over base rate: -0.00028 (-0.00344 to 0.00345)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | 14.6% | -5.1% | 0.80 |
| Naive (hold after an up candle) | 40.2% | -60.2% | 0.22 |
| Buy and hold | 22.1% | -75.0% | 0.44 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.4-0.5 | 7620 | 0.450 | 0.492 |
| 0.5-0.6 | 3900 | 0.515 | 0.478 |

## Most useful features (average gain)

- btc_rsi14: 21.45
- dow_cos: 20.96
- btc_ret_6: 20.89
- btc_ret_1: 18.22
- dow_sin: 16.57
- ret_1: 15.08
- macd_hist_pct: 14.42
- stoch_k: 14.12

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 2024-10-11 to 2025-01-08 | 5 | 7.9% | 66.7% | 49.6% | 0.2478 | 0.2499 |
| 9 | 2025-01-09 to 2025-04-08 | 32 | 0.0% | n/a | 46.5% | 0.2501 | 0.2501 |
| 10 | 2025-04-09 to 2025-07-07 | 208 | 0.0% | n/a | 49.5% | 0.2530 | 0.2500 |
| 11 | 2025-07-08 to 2025-10-05 | 59 | 0.0% | n/a | 51.7% | 0.2509 | 0.2496 |
| 12 | 2025-10-06 to 2026-01-03 | 1 | 0.0% | n/a | 51.7% | 0.2534 | 0.2505 |
| 13 | 2026-01-04 to 2026-04-03 | 13 | 100.0% | 59.4% | 55.1% | 0.2419 | 0.2528 |
| 14 | 2026-04-04 to 2026-07-02 | 1 | 100.0% | 53.2% | 50.0% | 0.2498 | 0.2499 |
| 15 | 2026-07-03 to 2026-09-30 | 2 | 100.0% | 47.4% | 46.9% | 0.2593 | 0.2512 |
