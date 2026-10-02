# Backtest XRP 1h (2026-10-02)

Out-of-sample period: 2025-05-05 to 2026-09-27, 17 walk-forward folds, 12240 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.8% | naive 49.1%, always-up 49.4% |
| Coverage (share of non-neutral calls) | 5.1% | 100% |
| Brier score (lower is better) | 0.2502 | base rate 0.2501 |
| Log loss | 0.6935 | coin flip 0.6931 |
| Up calls: n / precision / recall | 196 / 53.6% / 1.7% | |
| Down calls: n / precision / recall | 428 / 55.4% / 3.8% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 10.30% (4.28% to 16.32%)
- Brier improvement over base rate: -0.00010 (-0.00065 to 0.00040)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -27.7% | -30.1% | -1.85 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -13.34 |
| Buy and hold | -29.0% | -72.9% | -0.05 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 34 | 0.390 | 0.324 |
| 0.4-0.5 | 8796 | 0.477 | 0.490 |
| 0.5-0.6 | 3407 | 0.515 | 0.505 |
| 0.6-0.7 | 3 | 0.604 | 1.000 |

## Most useful features (average gain)

- dist_ema9: 7.23
- stoch_k: 7.20
- rsi14: 7.16
- ret_3: 7.15
- ret_24: 6.75
- dow_sin: 6.46
- lower_wick_pct: 6.41
- ret_1: 6.36

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2025-05-05 to 2025-06-04 | 21 | 7.5% | 68.5% | 50.4% | 0.2497 | 0.2500 |
| 2 | 2025-06-04 to 2025-07-04 | 319 | 0.0% | n/a | 50.8% | 0.2500 | 0.2500 |
| 3 | 2025-07-04 to 2025-08-03 | 1 | 0.0% | n/a | 52.2% | 0.2512 | 0.2500 |
| 4 | 2025-08-03 to 2025-09-02 | 1 | 0.0% | n/a | 49.4% | 0.2505 | 0.2500 |
| 5 | 2025-09-02 to 2025-10-02 | 87 | 5.8% | 61.9% | 47.4% | 0.2493 | 0.2500 |
| 6 | 2025-10-02 to 2025-11-01 | 5 | 0.0% | n/a | 49.4% | 0.2515 | 0.2499 |
| 7 | 2025-11-01 to 2025-12-01 | 8 | 20.1% | 49.7% | 47.6% | 0.2532 | 0.2503 |
| 8 | 2025-12-01 to 2025-12-31 | 5 | 0.0% | n/a | 50.7% | 0.2499 | 0.2505 |
| 9 | 2025-12-31 to 2026-01-30 | 39 | 0.0% | n/a | 49.3% | 0.2493 | 0.2500 |
| 10 | 2026-01-30 to 2026-03-01 | 2 | 0.0% | n/a | 52.9% | 0.2483 | 0.2503 |
| 11 | 2026-03-01 to 2026-03-31 | 2 | 0.0% | n/a | 47.2% | 0.2497 | 0.2498 |
| 12 | 2026-03-31 to 2026-04-30 | 45 | 53.2% | 54.0% | 47.5% | 0.2512 | 0.2499 |
| 13 | 2026-04-30 to 2026-05-30 | 26 | 0.0% | n/a | 49.6% | 0.2500 | 0.2505 |
| 14 | 2026-05-30 to 2026-06-29 | 1 | 0.0% | n/a | 47.9% | 0.2493 | 0.2490 |
| 15 | 2026-06-29 to 2026-07-29 | 5 | 0.0% | n/a | 48.1% | 0.2500 | 0.2500 |
| 16 | 2026-07-29 to 2026-08-28 | 10 | 0.0% | n/a | 47.4% | 0.2498 | 0.2499 |
| 17 | 2026-08-28 to 2026-09-27 | 36 | 0.0% | n/a | 47.4% | 0.2499 | 0.2507 |
