# Backtest DOGE 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 124915 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.7% | naive 49.3%, always-up 50.0%, always-down 50.0% |
| Flat candles (close equal to the previous close) | 11.5% | |
| Coverage (share of non-neutral calls) | 7.7% | 100% |
| Brier score (lower is better) | 0.2501 | base rate 0.2500 |
| Log loss | 0.6935 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4681 / 54.8% / 4.1% | |
| Down calls: n / precision / recall | 5176 / 52.7% / 4.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 8.39% (5.64% to 11.21%)
- Accuracy minus the best simple rule: 6.61% (4.39% to 8.83%)
- Brier improvement over base rate: -0.00005 (-0.00144 to 0.00088)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -93.61 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -555.64 |
| Buy and hold | 20.9% | -21.8% | 1.39 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.1-0.2 | 5 | 0.189 | 1.000 |
| 0.2-0.3 | 125 | 0.275 | 0.576 |
| 0.3-0.4 | 1522 | 0.362 | 0.472 |
| 0.4-0.5 | 57081 | 0.485 | 0.488 |
| 0.5-0.6 | 64889 | 0.515 | 0.511 |
| 0.6-0.7 | 1139 | 0.635 | 0.512 |
| 0.7-0.8 | 153 | 0.737 | 0.614 |
| 0.8-0.9 | 1 | 0.806 | 0.000 |

## Most useful features (average gain)

- dist_ema21: 19.46
- rsi14: 19.18
- dist_ema50: 18.64
- dist_ema9: 17.67
- log_ret_1: 16.85
- ret_1: 15.53
- lower_wick_pct: 14.61
- upper_wick_pct: 14.10

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 286 | 5.1% | 55.2% | 48.7% | 0.2496 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 123 | 2.6% | 57.7% | 49.3% | 0.2494 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 197 | 2.5% | 57.0% | 48.8% | 0.2493 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 83 | 3.2% | 59.7% | 48.3% | 0.2493 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 793 | 11.6% | 57.8% | 48.5% | 0.2486 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 603 | 15.7% | 55.2% | 48.7% | 0.2494 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 580 | 9.7% | 61.8% | 46.2% | 0.2471 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 232 | 57.3% | 50.7% | 49.7% | 0.2579 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 799 | 0.0% | n/a | 51.3% | 0.2500 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 3 | 0.0% | n/a | 49.5% | 0.2500 | 0.2500 |
| 38 | 2026-09-09 to 2026-09-16 | 6 | 0.0% | n/a | 49.1% | 0.2501 | 0.2500 |
| 39 | 2026-09-16 to 2026-09-23 | 51 | 0.0% | n/a | 50.1% | 0.2502 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 39 | 0.0% | n/a | 51.5% | 0.2500 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 5 | 0.0% | n/a | 50.1% | 0.2500 | 0.2500 |
