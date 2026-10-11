# Backtest LTC 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 114996 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 58.9% | naive 48.3%, always-up 50.7%, always-down 49.3% |
| Flat candles (close equal to the previous close) | 18.5% | |
| Coverage (share of non-neutral calls) | 28.9% | 100% |
| Brier score (lower is better) | 0.2474 | base rate 0.2500 |
| Log loss | 0.6878 | coin flip 0.6931 |
| Up calls: n / precision / recall | 18529 / 60.0% / 19.1% | |
| Down calls: n / precision / recall | 12841 / 57.3% / 13.0% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 10.71% (7.06% to 14.52%)
- Accuracy minus the best simple rule: 7.54% (4.83% to 10.23%)
- Brier improvement over base rate: 0.00315 (0.00010 to 0.00683)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -344.01 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -585.24 |
| Buy and hold | 55.9% | -15.4% | 3.13 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.1-0.2 | 1 | 0.193 | 0.000 |
| 0.2-0.3 | 276 | 0.277 | 0.388 |
| 0.3-0.4 | 3877 | 0.367 | 0.413 |
| 0.4-0.5 | 48412 | 0.476 | 0.475 |
| 0.5-0.6 | 55256 | 0.529 | 0.525 |
| 0.6-0.7 | 6277 | 0.633 | 0.630 |
| 0.7-0.8 | 852 | 0.735 | 0.709 |
| 0.8-0.9 | 45 | 0.817 | 0.800 |

## Most useful features (average gain)

- lower_wick_pct: 45.00
- log_ret_1: 43.65
- upper_wick_pct: 36.95
- dist_ema9: 33.72
- ret_1: 33.15
- dist_ema21: 28.29
- stoch_k: 22.80
- atr_pct: 19.80

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 408 | 37.1% | 55.3% | 47.8% | 0.2489 | 0.2499 |
| 29 | 2026-07-08 to 2026-07-15 | 190 | 22.5% | 61.4% | 47.2% | 0.2460 | 0.2498 |
| 30 | 2026-07-15 to 2026-07-22 | 135 | 47.5% | 57.4% | 48.4% | 0.2471 | 0.2499 |
| 31 | 2026-07-22 to 2026-07-29 | 727 | 44.9% | 58.1% | 48.0% | 0.2462 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 438 | 47.5% | 60.6% | 47.5% | 0.2441 | 0.2499 |
| 33 | 2026-08-05 to 2026-08-12 | 554 | 55.1% | 63.3% | 44.9% | 0.2382 | 0.2499 |
| 34 | 2026-08-12 to 2026-08-19 | 799 | 71.5% | 66.7% | 44.0% | 0.2288 | 0.2499 |
| 35 | 2026-08-19 to 2026-08-26 | 798 | 65.3% | 52.0% | 49.5% | 0.2574 | 0.2499 |
| 36 | 2026-08-26 to 2026-09-02 | 800 | 3.7% | 61.2% | 49.6% | 0.2490 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 11 | 0.0% | n/a | 49.0% | 0.2497 | 0.2499 |
| 38 | 2026-09-09 to 2026-09-16 | 550 | 5.8% | 57.1% | 47.8% | 0.2493 | 0.2502 |
| 39 | 2026-09-16 to 2026-09-23 | 32 | 3.7% | 49.8% | 50.5% | 0.2506 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 82 | 0.0% | n/a | 50.4% | 0.2500 | 0.2501 |
| 41 | 2026-09-30 to 2026-10-07 | 1 | 0.0% | n/a | 49.7% | 0.2500 | 0.2500 |
