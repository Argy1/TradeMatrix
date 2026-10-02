# Backtest SOL 1h (2026-10-02)

Out-of-sample period: 2025-05-05 to 2026-09-27, 17 walk-forward folds, 12240 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 50.9% | naive 48.8%, always-up 50.3% |
| Coverage (share of non-neutral calls) | 12.8% | 100% |
| Brier score (lower is better) | 0.2509 | base rate 0.2502 |
| Log loss | 0.6949 | coin flip 0.6931 |
| Up calls: n / precision / recall | 287 / 55.4% / 2.6% | |
| Down calls: n / precision / recall | 1279 / 49.9% / 10.5% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.68% (1.58% to 15.30%)
- Brier improvement over base rate: -0.00071 (-0.00209 to 0.00022)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -45.8% | -46.6% | -3.49 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -13.14 |
| Buy and hold | -15.9% | -75.8% | 0.16 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 14 | 0.282 | 0.429 |
| 0.3-0.4 | 249 | 0.362 | 0.510 |
| 0.4-0.5 | 3654 | 0.473 | 0.501 |
| 0.5-0.6 | 8316 | 0.519 | 0.504 |
| 0.6-0.7 | 7 | 0.612 | 1.000 |

## Most useful features (average gain)

- ret_3: 6.78
- vol_ratio_20: 6.66
- upper_wick_pct: 6.66
- stoch_k: 6.61
- dist_ema9: 6.60
- macd_pct: 6.56
- ret_24: 6.55
- log_ret_1: 6.51

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2025-05-05 to 2025-06-04 | 8 | 10.3% | 56.8% | 49.3% | 0.2490 | 0.2499 |
| 2 | 2025-06-04 to 2025-07-04 | 104 | 0.0% | n/a | 51.2% | 0.2504 | 0.2501 |
| 3 | 2025-07-04 to 2025-08-03 | 6 | 0.0% | n/a | 47.5% | 0.2499 | 0.2500 |
| 4 | 2025-08-03 to 2025-09-02 | 92 | 1.4% | 50.0% | 47.6% | 0.2498 | 0.2502 |
| 5 | 2025-09-02 to 2025-10-02 | 17 | 12.8% | 53.3% | 52.1% | 0.2502 | 0.2500 |
| 6 | 2025-10-02 to 2025-11-01 | 55 | 0.0% | n/a | 51.9% | 0.2500 | 0.2499 |
| 7 | 2025-11-01 to 2025-12-01 | 9 | 0.0% | n/a | 47.5% | 0.2502 | 0.2506 |
| 8 | 2025-12-01 to 2025-12-31 | 35 | 19.2% | 49.3% | 51.1% | 0.2511 | 0.2497 |
| 9 | 2025-12-31 to 2026-01-30 | 3 | 0.0% | n/a | 47.1% | 0.2511 | 0.2504 |
| 10 | 2026-01-30 to 2026-03-01 | 56 | 71.4% | 48.8% | 47.9% | 0.2606 | 0.2504 |
| 11 | 2026-03-01 to 2026-03-31 | 132 | 0.0% | n/a | 47.5% | 0.2500 | 0.2509 |
| 12 | 2026-03-31 to 2026-04-30 | 3 | 100.0% | 51.1% | 47.1% | 0.2521 | 0.2501 |
| 13 | 2026-04-30 to 2026-05-30 | 36 | 2.1% | 80.0% | 50.0% | 0.2493 | 0.2502 |
| 14 | 2026-05-30 to 2026-06-29 | 112 | 0.4% | 66.7% | 49.3% | 0.2501 | 0.2498 |
| 15 | 2026-06-29 to 2026-07-29 | 54 | 0.0% | n/a | 47.5% | 0.2494 | 0.2503 |
| 16 | 2026-07-29 to 2026-08-28 | 1 | 0.0% | n/a | 48.8% | 0.2497 | 0.2504 |
| 17 | 2026-08-28 to 2026-09-27 | 10 | 0.0% | n/a | 46.5% | 0.2519 | 0.2499 |
