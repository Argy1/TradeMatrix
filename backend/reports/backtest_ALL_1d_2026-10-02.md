# Backtest ALL 1d (2026-10-02)

Out-of-sample period: 2024-02-20 to 2026-08-07, 10 walk-forward folds, 4500 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 49.0% | naive 50.1%, always-up 50.0% |
| Coverage (share of non-neutral calls) | 35.6% | 100% |
| Brier score (lower is better) | 0.2535 | base rate 0.2504 |
| Log loss | 0.7003 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1486 / 49.3% / 32.6% | |
| Down calls: n / precision / recall | 115 / 45.2% / 2.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: -0.61% (-5.22% to 3.90%)
- Brier improvement over base rate: -0.00314 (-0.00589 to -0.00056)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -17.8% | -57.8% | -0.22 |
| Naive (hold after an up candle) | 7.6% | -55.1% | 0.01 |
| Buy and hold | 22.3% | -65.2% | 0.42 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 1 | 0.383 | 0.000 |
| 0.4-0.5 | 1137 | 0.469 | 0.499 |
| 0.5-0.6 | 3299 | 0.547 | 0.503 |
| 0.6-0.7 | 63 | 0.616 | 0.349 |

## Most useful features (average gain)

- log_ret_1: 10.02
- ret_1: 10.02
- btc_rsi14: 8.62
- dow_cos: 8.48
- upper_wick_pct: 8.17
- btc_ret_6: 8.14
- rsi14: 8.11
- btc_ret_1: 8.00

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2024-02-20 to 2024-05-19 | 37 | 31.3% | 51.8% | 44.9% | 0.2485 | 0.2509 |
| 2 | 2024-05-20 to 2024-08-17 | 9 | 14.4% | 46.2% | 48.4% | 0.2503 | 0.2498 |
| 3 | 2024-08-18 to 2024-11-15 | 15 | 0.0% | n/a | 50.7% | 0.2484 | 0.2503 |
| 4 | 2024-11-16 to 2025-02-13 | 48 | 100.0% | 50.7% | 45.6% | 0.2533 | 0.2500 |
| 5 | 2025-02-14 to 2025-05-14 | 64 | 4.9% | 54.5% | 46.9% | 0.2491 | 0.2504 |
| 6 | 2025-05-15 to 2025-08-12 | 43 | 39.3% | 45.8% | 56.4% | 0.2578 | 0.2488 |
| 7 | 2025-08-13 to 2025-11-10 | 3 | 100.0% | 49.8% | 47.8% | 0.2604 | 0.2502 |
| 8 | 2025-11-11 to 2026-02-08 | 9 | 14.4% | 50.8% | 55.6% | 0.2567 | 0.2529 |
| 9 | 2026-02-09 to 2026-05-09 | 4 | 0.0% | n/a | 51.3% | 0.2524 | 0.2499 |
| 10 | 2026-05-10 to 2026-08-07 | 22 | 51.3% | 45.0% | 53.8% | 0.2582 | 0.2507 |
