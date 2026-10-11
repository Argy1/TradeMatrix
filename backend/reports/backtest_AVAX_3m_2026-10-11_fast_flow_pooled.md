# Backtest AVAX 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 57254 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.7% | naive 49.6%, always-up 49.8%, always-down 50.2% |
| Flat candles (close equal to the previous close) | 5.3% | |
| Coverage (share of non-neutral calls) | 15.2% | 100% |
| Brier score (lower is better) | 0.2505 | base rate 0.2500 |
| Log loss | 0.6941 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4169 / 53.5% / 7.8% | |
| Down calls: n / precision / recall | 4490 / 51.8% / 8.1% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 2.91% (1.17% to 4.57%)
- Accuracy minus the best simple rule: 1.71% (0.09% to 3.26%)
- Brier improvement over base rate: -0.00045 (-0.00082 to -0.00010)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -99.93 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -212.63 |
| Buy and hold | 37.3% | -28.7% | 1.57 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 464 | 0.380 | 0.494 |
| 0.4-0.5 | 30131 | 0.473 | 0.489 |
| 0.5-0.6 | 26128 | 0.526 | 0.509 |
| 0.6-0.7 | 529 | 0.619 | 0.537 |
| 0.7-0.8 | 2 | 0.700 | 0.000 |

## Most useful features (average gain)

- dist_ema9: 358.56
- dist_ema21: 191.48
- lower_wick_pct: 144.74
- log_ret_1: 123.25
- upper_wick_pct: 119.77
- stoch_k: 114.22
- ret_1: 107.74
- rsi14: 98.99

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 45 | 2026-06-04 to 2026-06-11 |  | 4.8% | 50.0% | 49.0% | 0.2495 | 0.2501 |
| 46 | 2026-06-11 to 2026-06-18 |  | 12.5% | 54.9% | 49.5% | 0.2503 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 15.7% | 53.7% | 48.4% | 0.2495 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 17.2% | 52.5% | 48.1% | 0.2498 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 17.9% | 54.9% | 48.4% | 0.2496 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 17.6% | 50.5% | 51.2% | 0.2514 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 16.0% | 52.1% | 51.0% | 0.2513 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 23.8% | 52.7% | 50.1% | 0.2506 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 31.2% | 52.6% | 49.1% | 0.2507 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 31.5% | 54.9% | 48.9% | 0.2508 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 30.4% | 50.8% | 49.4% | 0.2519 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 20.3% | 49.3% | 51.1% | 0.2514 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 7.1% | 47.8% | 49.5% | 0.2506 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 4.6% | 47.9% | 49.2% | 0.2493 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 12.6% | 57.1% | 49.0% | 0.2497 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 6.1% | 58.5% | 50.6% | 0.2514 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 2.1% | 58.0% | 49.5% | 0.2502 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 2.6% | 47.0% | 50.8% | 0.2502 | 0.2500 |
