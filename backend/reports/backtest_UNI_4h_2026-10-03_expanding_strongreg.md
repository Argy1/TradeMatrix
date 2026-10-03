# Backtest UNI 4h (2026-10-03)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-09 to 2026-09-29, 24 walk-forward folds, 4320 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.8% | naive 49.0%, always-up 48.9% |
| Coverage (share of non-neutral calls) | 18.7% | 100% |
| Brier score (lower is better) | 0.2502 | base rate 0.2499 |
| Log loss | 0.6936 | coin flip 0.6931 |
| Up calls: n / precision / recall | 109 / 49.5% / 2.6% | |
| Down calls: n / precision / recall | 700 / 54.4% / 17.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 2.47% (-4.82% to 10.42%)
- Brier improvement over base rate: -0.00032 (-0.00137 to 0.00078)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -20.6% | -43.3% | -0.40 |
| Naive (hold after an up candle) | -94.5% | -97.6% | -1.53 |
| Buy and hold | 20.2% | -87.1% | 0.60 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 27 | 0.393 | 0.444 |
| 0.4-0.5 | 2641 | 0.463 | 0.482 |
| 0.5-0.6 | 1652 | 0.517 | 0.501 |

## Most useful features (average gain)

- btc_ret_6: 11.91
- ret_6: 10.53
- btc_ret_1: 9.96
- dist_ema9: 9.68
- hour_sin: 8.55
- rsi14: 8.36
- atr_pct: 8.18
- dist_ema21: 8.13

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | 2024-10-09 to 2024-11-08 | 139 | 7.2% | 53.8% | 58.9% | 0.2506 | 0.2503 |
| 36 | 2024-11-08 to 2024-12-08 | 289 | 0.0% | n/a | 37.8% | 0.2460 | 0.2514 |
| 37 | 2024-12-08 to 2025-01-07 | 197 | 58.3% | 48.6% | 53.9% | 0.2557 | 0.2494 |
| 38 | 2025-01-07 to 2025-02-06 | 18 | 0.0% | n/a | 43.3% | 0.2529 | 0.2490 |
| 39 | 2025-02-06 to 2025-03-08 | 85 | 72.2% | 60.0% | 56.1% | 0.2453 | 0.2491 |
| 40 | 2025-03-08 to 2025-04-07 | 70 | 100.0% | 51.7% | 47.8% | 0.2525 | 0.2498 |
| 41 | 2025-04-07 to 2025-05-07 | 79 | 13.3% | 50.0% | 46.1% | 0.2474 | 0.2495 |
| 42 | 2025-05-07 to 2025-06-06 | 373 | 40.6% | 52.1% | 50.6% | 0.2530 | 0.2503 |
| 43 | 2025-06-06 to 2025-07-06 | 329 | 6.1% | 36.4% | 53.3% | 0.2532 | 0.2502 |
| 44 | 2025-07-06 to 2025-08-05 | 65 | 0.0% | n/a | 45.0% | 0.2500 | 0.2501 |
| 45 | 2025-08-05 to 2025-09-04 | 6 | 0.0% | n/a | 56.7% | 0.2501 | 0.2499 |
| 46 | 2025-09-04 to 2025-10-04 | 1 | 0.0% | n/a | 52.2% | 0.2501 | 0.2500 |
| 47 | 2025-10-04 to 2025-11-03 | 3 | 0.0% | n/a | 48.9% | 0.2505 | 0.2500 |
| 48 | 2025-11-03 to 2025-12-03 | 1 | 0.0% | n/a | 48.9% | 0.2495 | 0.2497 |
| 49 | 2025-12-03 to 2026-01-02 | 792 | 20.6% | 51.4% | 46.1% | 0.2526 | 0.2503 |
| 50 | 2026-01-02 to 2026-02-01 | 63 | 3.3% | 83.3% | 46.1% | 0.2486 | 0.2497 |
| 51 | 2026-02-01 to 2026-03-03 | 63 | 0.0% | n/a | 55.0% | 0.2500 | 0.2496 |
| 52 | 2026-03-03 to 2026-04-02 | 10 | 0.0% | n/a | 48.3% | 0.2502 | 0.2499 |
| 53 | 2026-04-02 to 2026-05-02 | 52 | 2.2% | 25.0% | 46.1% | 0.2488 | 0.2494 |
| 54 | 2026-05-02 to 2026-06-01 | 247 | 41.1% | 64.9% | 45.0% | 0.2444 | 0.2494 |
| 55 | 2026-06-01 to 2026-07-01 | 57 | 25.6% | 50.0% | 47.2% | 0.2507 | 0.2494 |
| 56 | 2026-07-01 to 2026-07-31 | 48 | 58.9% | 52.8% | 50.6% | 0.2541 | 0.2505 |
| 57 | 2026-07-31 to 2026-08-30 | 23 | 0.0% | n/a | 46.1% | 0.2494 | 0.2504 |
| 58 | 2026-08-30 to 2026-09-29 | 18 | 0.0% | n/a | 46.1% | 0.2496 | 0.2506 |
