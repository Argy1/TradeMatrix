# Backtest SOL 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 57053 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 52.9% | naive 49.4%, reverse 50.6%, always-up 49.9%, always-down 50.1% |
| Flat candles (close equal to the previous close) | 5.7% | |
| Coverage (share of non-neutral calls) | 10.8% | 100% |
| Brier score (lower is better) | 0.2500 | base rate 0.2500 |
| Log loss | 0.6931 | coin flip 0.6931 |
| Up calls: n / precision / recall | 2853 / 53.7% / 5.4% | |
| Down calls: n / precision / recall | 3167 / 52.3% / 5.8% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 3.38% (1.89% to 4.69%)
- Accuracy minus the best simple rule: 1.48% (0.26% to 2.58%)
- Brier improvement over base rate: 0.00004 (-0.00022 to 0.00030)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -99.9% | -99.9% | -88.74 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -248.31 |
| Buy and hold | 63.4% | -15.7% | 2.61 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 3 | 0.286 | 0.000 |
| 0.3-0.4 | 282 | 0.383 | 0.539 |
| 0.4-0.5 | 30802 | 0.476 | 0.486 |
| 0.5-0.6 | 25645 | 0.523 | 0.513 |
| 0.6-0.7 | 315 | 0.620 | 0.590 |
| 0.7-0.8 | 6 | 0.720 | 0.500 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 2.1% | 50.8% | 47.8% | 0.2491 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 7.6% | 53.7% | 48.7% | 0.2496 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 12.5% | 54.6% | 49.1% | 0.2499 | 0.2500 |
| 48 | 2026-06-25 to 2026-07-02 |  | 9.8% | 54.5% | 48.4% | 0.2495 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 9.4% | 53.4% | 48.5% | 0.2496 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 9.7% | 50.3% | 50.3% | 0.2503 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 8.0% | 54.3% | 50.2% | 0.2498 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 17.3% | 54.8% | 49.3% | 0.2497 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 24.5% | 53.9% | 50.2% | 0.2504 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 23.5% | 51.8% | 50.5% | 0.2512 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 25.7% | 53.8% | 46.5% | 0.2494 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 16.0% | 50.3% | 51.0% | 0.2508 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 4.1% | 50.7% | 48.7% | 0.2499 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 3.6% | 54.6% | 48.7% | 0.2494 | 0.2500 |
| 59 | 2026-09-10 to 2026-09-17 |  | 10.6% | 51.7% | 49.6% | 0.2503 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 4.6% | 46.7% | 52.0% | 0.2507 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 2.0% | 54.7% | 51.2% | 0.2503 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 2.8% | 55.6% | 48.7% | 0.2493 | 0.2500 |
