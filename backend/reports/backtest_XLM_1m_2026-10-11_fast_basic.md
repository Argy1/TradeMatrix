# Backtest XLM 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 97287 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 61.5% | naive 46.3%, always-up 49.5%, always-down 50.5% |
| Flat candles (close equal to the previous close) | 31.1% | |
| Coverage (share of non-neutral calls) | 50.9% | 100% |
| Brier score (lower is better) | 0.2417 | base rate 0.2500 |
| Log loss | 0.6760 | coin flip 0.6931 |
| Up calls: n / precision / recall | 20936 / 62.3% / 27.1% | |
| Down calls: n / precision / recall | 26568 / 60.9% / 33.0% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 15.61% (11.54% to 19.81%)
- Accuracy minus the best simple rule: 10.94% (8.49% to 13.28%)
- Brier improvement over base rate: 0.00975 (0.00392 to 0.01628)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -360.57 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -520.03 |
| Buy and hold | -0.1% | -29.2% | 0.38 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.1-0.2 | 164 | 0.181 | 0.134 |
| 0.2-0.3 | 2311 | 0.265 | 0.261 |
| 0.3-0.4 | 10379 | 0.361 | 0.372 |
| 0.4-0.5 | 40972 | 0.461 | 0.458 |
| 0.5-0.6 | 33111 | 0.538 | 0.547 |
| 0.6-0.7 | 7703 | 0.640 | 0.635 |
| 0.7-0.8 | 2259 | 0.740 | 0.707 |
| 0.8-0.9 | 388 | 0.829 | 0.817 |

## Most useful features (average gain)

- stoch_k: 69.02
- log_ret_1: 63.74
- dist_ema9: 57.22
- ret_1: 47.50
- upper_wick_pct: 43.23
- lower_wick_pct: 43.17
- btc_ret_1: 34.80
- atr_pct: 27.63

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 66 | 40.7% | 59.2% | 46.7% | 0.2461 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 250 | 59.3% | 62.5% | 45.1% | 0.2399 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 480 | 60.5% | 58.9% | 47.0% | 0.2447 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 788 | 57.5% | 66.3% | 43.8% | 0.2344 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 800 | 76.6% | 66.9% | 43.7% | 0.2235 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 798 | 80.9% | 66.2% | 41.9% | 0.2249 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 794 | 81.1% | 70.0% | 38.0% | 0.2128 | 0.2499 |
| 35 | 2026-08-19 to 2026-08-26 | 799 | 70.2% | 53.2% | 48.6% | 0.2570 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 800 | 27.7% | 65.3% | 47.8% | 0.2437 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 12 | 19.0% | 59.1% | 46.7% | 0.2473 | 0.2501 |
| 38 | 2026-09-09 to 2026-09-16 | 800 | 59.9% | 60.5% | 47.4% | 0.2426 | 0.2499 |
| 39 | 2026-09-16 to 2026-09-23 | 797 | 50.8% | 54.6% | 49.9% | 0.2498 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 537 | 20.2% | 55.8% | 50.1% | 0.2491 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 48 | 8.8% | 63.2% | 46.6% | 0.2474 | 0.2499 |
