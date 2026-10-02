# Backtest SOL 4h (2026-10-02)

Out-of-sample period: 2024-11-10 to 2026-10-01, 23 walk-forward folds, 4140 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 50.0% | naive 49.8%, always-up 49.4% |
| Coverage (share of non-neutral calls) | 49.4% | 100% |
| Brier score (lower is better) | 0.2531 | base rate 0.2502 |
| Log loss | 0.6995 | coin flip 0.6931 |
| Up calls: n / precision / recall | 711 / 48.0% / 16.7% | |
| Down calls: n / precision / recall | 1333 / 51.2% / 32.6% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 0.58% (-2.08% to 3.13%)
- Brier improvement over base rate: -0.00293 (-0.00522 to -0.00083)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -46.2% | -58.9% | -1.04 |
| Naive (hold after an up candle) | -91.7% | -92.8% | -2.22 |
| Buy and hold | -43.0% | -78.5% | -0.02 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 280 | 0.391 | 0.482 |
| 0.4-0.5 | 2488 | 0.457 | 0.497 |
| 0.5-0.6 | 1192 | 0.536 | 0.493 |
| 0.6-0.7 | 180 | 0.611 | 0.489 |

## Most useful features (average gain)

- ret_6: 6.39
- dist_ema21: 6.30
- bb_percent_b: 5.94
- ret_12: 5.93
- btc_ret_6: 5.92
- rsi14: 5.90
- lower_wick_pct: 5.87
- btc_ret_1: 5.86

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2024-11-10 to 2024-12-10 | 28 | 100.0% | 50.6% | 47.2% | 0.2525 | 0.2501 |
| 2 | 2024-12-10 to 2025-01-09 | 1 | 100.0% | 50.6% | 50.6% | 0.2525 | 0.2505 |
| 3 | 2025-01-09 to 2025-02-08 | 59 | 19.4% | 57.1% | 48.9% | 0.2478 | 0.2517 |
| 4 | 2025-02-08 to 2025-03-10 | 60 | 100.0% | 51.7% | 54.4% | 0.2586 | 0.2506 |
| 5 | 2025-03-10 to 2025-04-09 | 61 | 0.0% | n/a | 50.6% | 0.2500 | 0.2505 |
| 6 | 2025-04-09 to 2025-05-09 | 13 | 100.0% | 42.8% | 49.4% | 0.2644 | 0.2492 |
| 7 | 2025-05-09 to 2025-06-08 | 7 | 88.3% | 47.2% | 52.2% | 0.2546 | 0.2501 |
| 8 | 2025-06-08 to 2025-07-08 | 30 | 100.0% | 51.1% | 54.4% | 0.2581 | 0.2504 |
| 9 | 2025-07-08 to 2025-08-07 | 1 | 0.0% | n/a | 50.0% | 0.2499 | 0.2498 |
| 10 | 2025-08-07 to 2025-09-06 | 19 | 31.7% | 42.1% | 49.4% | 0.2574 | 0.2495 |
| 11 | 2025-09-06 to 2025-10-06 | 1 | 0.0% | n/a | 57.2% | 0.2507 | 0.2501 |
| 12 | 2025-10-06 to 2025-11-05 | 5 | 100.0% | 57.8% | 51.1% | 0.2440 | 0.2512 |
| 13 | 2025-11-05 to 2025-12-05 | 12 | 76.7% | 53.6% | 50.6% | 0.2519 | 0.2499 |
| 14 | 2025-12-05 to 2026-01-04 | 153 | 19.4% | 48.6% | 47.2% | 0.2523 | 0.2504 |
| 15 | 2026-01-04 to 2026-02-03 | 4 | 100.0% | 48.9% | 41.7% | 0.2648 | 0.2499 |
| 16 | 2026-02-03 to 2026-03-05 | 128 | 0.0% | n/a | 59.4% | 0.2503 | 0.2500 |
| 17 | 2026-03-05 to 2026-04-04 | 5 | 0.0% | n/a | 48.3% | 0.2500 | 0.2500 |
| 18 | 2026-04-04 to 2026-05-04 | 17 | 0.0% | n/a | 53.3% | 0.2500 | 0.2501 |
| 19 | 2026-05-04 to 2026-06-03 | 1 | 100.0% | 44.4% | 46.7% | 0.2619 | 0.2505 |
| 20 | 2026-06-03 to 2026-07-03 | 45 | 100.0% | 53.9% | 48.3% | 0.2493 | 0.2501 |
| 21 | 2026-07-03 to 2026-08-02 | 2 | 0.0% | n/a | 39.4% | 0.2489 | 0.2494 |
| 22 | 2026-08-02 to 2026-09-01 | 4 | 0.0% | n/a | 46.7% | 0.2530 | 0.2504 |
| 23 | 2026-09-01 to 2026-10-01 | 33 | 0.0% | n/a | 47.2% | 0.2495 | 0.2505 |
