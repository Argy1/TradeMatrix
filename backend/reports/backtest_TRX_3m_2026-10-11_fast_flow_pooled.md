# Backtest TRX 3m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-06-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-06-04 to 2026-10-08, 18 walk-forward folds, 36892 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 74.0% | naive 41.4%, reverse 58.6%, always-up 50.9%, always-down 49.1% |
| Flat candles (close equal to the previous close) | 39.0% | |
| Coverage (share of non-neutral calls) | 54.1% | 100% |
| Brier score (lower is better) | 0.2268 | base rate 0.2500 |
| Log loss | 0.6457 | coin flip 0.6931 |
| Up calls: n / precision / recall | 9359 / 78.6% / 39.2% | |
| Down calls: n / precision / recall | 9900 / 69.6% / 38.0% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 32.03% (28.40% to 35.33%)
- Accuracy minus the best simple rule: 14.69% (12.93% to 16.35%)
- Brier improvement over base rate: 0.02382 (0.01884 to 0.02874)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -275.26 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -388.60 |
| Buy and hold | 0.6% | -8.1% | 0.19 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 241 | 0.280 | 0.178 |
| 0.3-0.4 | 3771 | 0.370 | 0.277 |
| 0.4-0.5 | 14427 | 0.457 | 0.377 |
| 0.5-0.6 | 13723 | 0.539 | 0.609 |
| 0.6-0.7 | 3924 | 0.637 | 0.817 |
| 0.7-0.8 | 762 | 0.734 | 0.845 |
| 0.8-0.9 | 44 | 0.813 | 0.886 |

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
| 45 | 2026-06-04 to 2026-06-11 |  | 22.1% | 59.3% | 46.6% | 0.2467 | 0.2500 |
| 46 | 2026-06-11 to 2026-06-18 |  | 44.9% | 67.1% | 42.1% | 0.2401 | 0.2500 |
| 47 | 2026-06-18 to 2026-06-25 |  | 54.5% | 69.1% | 41.9% | 0.2356 | 0.2499 |
| 48 | 2026-06-25 to 2026-07-02 |  | 53.5% | 71.1% | 42.6% | 0.2338 | 0.2500 |
| 49 | 2026-07-02 to 2026-07-09 |  | 49.6% | 68.8% | 41.8% | 0.2360 | 0.2500 |
| 50 | 2026-07-09 to 2026-07-16 |  | 52.4% | 75.9% | 40.2% | 0.2287 | 0.2500 |
| 51 | 2026-07-16 to 2026-07-23 |  | 55.2% | 80.8% | 37.9% | 0.2204 | 0.2500 |
| 52 | 2026-07-23 to 2026-07-30 |  | 65.2% | 77.6% | 40.5% | 0.2153 | 0.2500 |
| 53 | 2026-07-30 to 2026-08-06 |  | 69.2% | 77.5% | 39.3% | 0.2117 | 0.2500 |
| 54 | 2026-08-06 to 2026-08-13 |  | 69.0% | 80.0% | 36.7% | 0.2067 | 0.2500 |
| 55 | 2026-08-13 to 2026-08-20 |  | 68.5% | 76.1% | 39.3% | 0.2094 | 0.2500 |
| 56 | 2026-08-20 to 2026-08-27 |  | 57.6% | 67.0% | 44.3% | 0.2346 | 0.2500 |
| 57 | 2026-08-27 to 2026-09-03 |  | 40.0% | 73.8% | 44.6% | 0.2348 | 0.2500 |
| 58 | 2026-09-03 to 2026-09-10 |  | 50.9% | 77.9% | 40.3% | 0.2246 | 0.2501 |
| 59 | 2026-09-10 to 2026-09-17 |  | 63.1% | 73.0% | 43.4% | 0.2214 | 0.2500 |
| 60 | 2026-09-17 to 2026-09-24 |  | 51.5% | 72.2% | 40.9% | 0.2281 | 0.2500 |
| 61 | 2026-09-24 to 2026-10-01 |  | 49.8% | 75.3% | 40.5% | 0.2259 | 0.2500 |
| 62 | 2026-10-01 to 2026-10-08 |  | 56.4% | 78.2% | 40.9% | 0.2172 | 0.2500 |
