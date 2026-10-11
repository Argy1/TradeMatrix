# Backtest SOL 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 125569 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.7% | naive 49.7%, reverse 50.3%, always-up 50.2%, always-down 49.8% |
| Flat candles (close equal to the previous close) | 11.0% | |
| Coverage (share of non-neutral calls) | 8.4% | 100% |
| Brier score (lower is better) | 0.2496 | base rate 0.2500 |
| Log loss | 0.6923 | coin flip 0.6931 |
| Up calls: n / precision / recall | 5274 / 57.3% / 4.8% | |
| Down calls: n / precision / recall | 5066 / 54.0% / 4.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 4.90% (-2.20% to 9.85%)
- Accuracy minus the best simple rule: 3.19% (-3.43% to 7.72%)
- Brier improvement over base rate: 0.00045 (-0.00021 to 0.00110)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -139.18 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -585.15 |
| Buy and hold | 50.8% | -15.9% | 3.02 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 53 | 0.274 | 0.566 |
| 0.3-0.4 | 951 | 0.374 | 0.478 |
| 0.4-0.5 | 48621 | 0.482 | 0.486 |
| 0.5-0.6 | 74940 | 0.516 | 0.511 |
| 0.6-0.7 | 989 | 0.629 | 0.639 |
| 0.7-0.8 | 15 | 0.716 | 0.800 |

## Most useful features (average gain)

- dist_ema21: 23.58
- dist_ema9: 18.03
- lower_wick_pct: 17.37
- upper_wick_pct: 16.74
- dist_ema50: 16.13
- log_ret_1: 15.15
- rsi14: 14.71
- ret_1: 14.58

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 261 | 4.2% | 61.8% | 47.8% | 0.2488 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 130 | 11.6% | 56.6% | 49.5% | 0.2490 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 231 | 7.1% | 55.8% | 49.1% | 0.2494 | 0.2499 |
| 31 | 2026-07-22 to 2026-07-29 | 423 | 3.9% | 60.0% | 49.0% | 0.2495 | 0.2501 |
| 32 | 2026-07-29 to 2026-08-05 | 608 | 12.4% | 54.7% | 48.9% | 0.2494 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 403 | 10.9% | 60.6% | 48.7% | 0.2483 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 757 | 27.2% | 59.0% | 48.2% | 0.2467 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 783 | 39.6% | 51.7% | 49.6% | 0.2525 | 0.2499 |
| 36 | 2026-08-26 to 2026-09-02 | 783 | 0.0% | 25.0% | 50.8% | 0.2500 | 0.2501 |
| 37 | 2026-09-02 to 2026-09-09 | 26 | 0.0% | n/a | 50.2% | 0.2500 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 23 | 0.5% | 61.1% | 50.2% | 0.2499 | 0.2500 |
| 39 | 2026-09-16 to 2026-09-23 | 52 | 0.0% | 50.0% | 50.5% | 0.2500 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 59 | 0.0% | n/a | 51.6% | 0.2499 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 14 | 0.0% | n/a | 50.7% | 0.2500 | 0.2500 |
