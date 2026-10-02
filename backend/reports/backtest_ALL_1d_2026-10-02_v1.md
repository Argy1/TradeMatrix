# Backtest ALL 1d (2026-10-02)

Model settings: `v1` (chosen on the 2021-2024 development window only, see `reports/tuning_*.md`). Test folds start on or after 2024-10-01. Note: this period was also scored once in the first run (before the improvement round), so it is not perfectly unseen.

Out-of-sample period: 2024-10-11 to 2026-09-30, 8 walk-forward folds, 3600 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 47.5% | naive 50.2%, always-up 50.2% |
| Coverage (share of non-neutral calls) | 44.5% | 100% |
| Brier score (lower is better) | 0.2544 | base rate 0.2506 |
| Log loss | 0.7020 | coin flip 0.6931 |
| Up calls: n / precision / recall | 327 / 46.5% / 8.4% | |
| Down calls: n / precision / recall | 1274 / 47.8% / 33.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: -2.26% (-4.85% to 0.33%)
- Brier improvement over base rate: -0.00373 (-0.00895 to 0.00091)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -22.7% | -32.3% | -0.67 |
| Naive (hold after an up candle) | 25.8% | -52.4% | 0.15 |
| Buy and hold | 47.7% | -65.4% | 0.56 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 161 | 0.383 | 0.503 |
| 0.4-0.5 | 1455 | 0.441 | 0.500 |
| 0.5-0.6 | 1984 | 0.520 | 0.503 |

## Most useful features (average gain)

- log_ret_1: 10.70
- ret_1: 9.22
- btc_rsi14: 8.45
- btc_ret_6: 8.39
- dow_cos: 8.30
- dow_sin: 8.16
- btc_ret_1: 8.14
- upper_wick_pct: 8.10

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 2024-10-11 to 2025-01-08 | 2 | 0.0% | n/a | 46.9% | 0.2498 | 0.2500 |
| 9 | 2025-01-09 to 2025-04-08 | 1 | 0.0% | n/a | 47.3% | 0.2501 | 0.2501 |
| 10 | 2025-04-09 to 2025-07-07 | 46 | 83.1% | 46.3% | 50.9% | 0.2629 | 0.2495 |
| 11 | 2025-07-08 to 2025-10-05 | 40 | 0.0% | n/a | 52.7% | 0.2477 | 0.2490 |
| 12 | 2025-10-06 to 2026-01-03 | 5 | 72.7% | 46.5% | 51.6% | 0.2567 | 0.2510 |
| 13 | 2026-01-04 to 2026-04-03 | 8 | 0.0% | n/a | 56.2% | 0.2495 | 0.2545 |
| 14 | 2026-04-04 to 2026-07-02 | 1 | 100.0% | 52.0% | 51.8% | 0.2506 | 0.2506 |
| 15 | 2026-07-03 to 2026-09-30 | 1 | 100.0% | 44.9% | 44.4% | 0.2676 | 0.2503 |
