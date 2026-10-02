# Backtest SOL 1h (2026-10-02)

Model settings: `expanding_strongreg` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-15 to 2026-09-05, 23 walk-forward folds, 16560 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.5% | naive 48.4%, always-up 50.4% |
| Coverage (share of non-neutral calls) | 9.5% | 100% |
| Brier score (lower is better) | 0.2497 | base rate 0.2500 |
| Log loss | 0.6925 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1087 / 56.0% / 7.3% | |
| Down calls: n / precision / recall | 487 / 54.4% / 3.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.61% (-2.43% to 20.51%)
- Brier improvement over base rate: 0.00038 (-0.00018 to 0.00099)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -62.4% | -64.6% | -1.69 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -12.74 |
| Buy and hold | -32.9% | -78.7% | 0.13 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 13 | 0.386 | 0.385 |
| 0.4-0.5 | 7820 | 0.478 | 0.490 |
| 0.5-0.6 | 8413 | 0.522 | 0.513 |
| 0.6-0.7 | 310 | 0.632 | 0.606 |
| 0.7-0.8 | 4 | 0.717 | 0.250 |

## Most useful features (average gain)

- dist_ema9: 37.12
- btc_ret_6: 19.08
- stoch_k: 18.83
- btc_ret_1: 17.79
- ret_3: 16.82
- bb_percent_b: 12.95
- obv_slope_10: 12.49
- dist_ema21: 11.95

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 2024-10-15 to 2024-11-14 | 27 | 8.3% | 68.3% | 45.0% | 0.2476 | 0.2504 |
| 43 | 2024-11-14 to 2024-12-14 | 82 | 38.9% | 56.4% | 45.0% | 0.2455 | 0.2502 |
| 44 | 2024-12-14 to 2025-01-13 | 155 | 42.2% | 55.9% | 47.5% | 0.2507 | 0.2500 |
| 45 | 2025-01-13 to 2025-02-12 | 540 | 35.7% | 57.2% | 45.4% | 0.2488 | 0.2501 |
| 46 | 2025-02-12 to 2025-03-14 | 708 | 8.8% | 61.9% | 49.4% | 0.2490 | 0.2497 |
| 47 | 2025-03-14 to 2025-04-13 | 168 | 37.8% | 50.7% | 48.8% | 0.2520 | 0.2500 |
| 48 | 2025-04-13 to 2025-05-13 | 330 | 0.0% | n/a | 50.8% | 0.2510 | 0.2503 |
| 49 | 2025-05-13 to 2025-06-12 | 22 | 2.4% | 64.7% | 49.2% | 0.2504 | 0.2500 |
| 50 | 2025-06-12 to 2025-07-12 | 16 | 0.0% | n/a | 51.1% | 0.2501 | 0.2500 |
| 51 | 2025-07-12 to 2025-08-11 | 404 | 0.1% | 100.0% | 46.7% | 0.2495 | 0.2501 |
| 52 | 2025-08-11 to 2025-09-10 | 9 | 0.0% | n/a | 49.0% | 0.2489 | 0.2503 |
| 53 | 2025-09-10 to 2025-10-10 | 15 | 1.8% | 61.5% | 50.8% | 0.2490 | 0.2502 |
| 54 | 2025-10-10 to 2025-11-09 | 131 | 35.3% | 52.0% | 52.5% | 0.2520 | 0.2500 |
| 55 | 2025-11-09 to 2025-12-09 | 592 | 4.7% | 55.9% | 47.8% | 0.2489 | 0.2500 |
| 56 | 2025-12-09 to 2026-01-08 | 31 | 0.0% | n/a | 49.3% | 0.2503 | 0.2501 |
| 57 | 2026-01-08 to 2026-02-07 | 35 | 0.0% | n/a | 48.9% | 0.2505 | 0.2499 |
| 58 | 2026-02-07 to 2026-03-09 | 120 | 2.2% | 62.5% | 46.4% | 0.2497 | 0.2499 |
| 59 | 2026-03-09 to 2026-04-08 | 57 | 0.4% | 0.0% | 47.8% | 0.2495 | 0.2499 |
| 60 | 2026-04-08 to 2026-05-08 | 64 | 0.0% | n/a | 49.3% | 0.2514 | 0.2500 |
| 61 | 2026-05-08 to 2026-06-07 | 32 | 0.0% | n/a | 48.6% | 0.2492 | 0.2499 |
| 62 | 2026-06-07 to 2026-07-07 | 18 | 0.0% | n/a | 49.7% | 0.2494 | 0.2501 |
| 63 | 2026-07-07 to 2026-08-06 | 62 | 0.0% | n/a | 48.1% | 0.2498 | 0.2500 |
| 64 | 2026-08-06 to 2026-09-05 | 102 | 0.0% | n/a | 46.5% | 0.2494 | 0.2501 |
