# Backtest LINK 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 47280 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 58.0% | naive 48.1%, always-up 49.8%, always-down 50.2% |
| Flat candles (close equal to the previous close) | 9.8% | |
| Coverage (share of non-neutral calls) | 21.4% | 100% |
| Brier score (lower is better) | 0.2480 | base rate 0.2500 |
| Log loss | 0.6892 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4437 / 58.5% / 11.0% | |
| Down calls: n / precision / recall | 4913 / 57.6% / 11.9% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.95% (3.13% to 13.86%)
- Accuracy minus the best simple rule: 5.13% (1.53% to 9.41%)
- Brier improvement over base rate: 0.00266 (-0.00004 to 0.00611)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -75.84 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -160.27 |
| Buy and hold | 65.7% | -35.5% | 1.88 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 16 | 0.292 | 0.312 |
| 0.3-0.4 | 806 | 0.373 | 0.320 |
| 0.4-0.5 | 24526 | 0.471 | 0.475 |
| 0.5-0.6 | 21235 | 0.529 | 0.524 |
| 0.6-0.7 | 689 | 0.625 | 0.691 |
| 0.7-0.8 | 8 | 0.715 | 0.875 |

## Most useful features (average gain)

- dist_ema9: 222.13
- bb_percent_b: 165.37
- dist_ema21: 133.72
- rsi14: 99.11
- lower_wick_pct: 92.35
- upper_wick_pct: 81.22
- stoch_k: 71.15
- log_ret_1: 59.11

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 29 | 2026-04-05 to 2026-04-19 |  | 43.7% | 64.6% | 43.8% | 0.2400 | 0.2500 |
| 30 | 2026-04-19 to 2026-05-03 |  | 42.9% | 73.3% | 40.0% | 0.2322 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 49.2% | 61.9% | 44.9% | 0.2417 | 0.2500 |
| 32 | 2026-05-17 to 2026-05-31 |  | 26.0% | 52.7% | 49.9% | 0.2495 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 8.9% | 57.6% | 49.3% | 0.2496 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 10.8% | 54.9% | 48.5% | 0.2491 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 13.8% | 49.4% | 48.0% | 0.2505 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 13.7% | 48.9% | 50.1% | 0.2511 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 20.9% | 51.8% | 50.2% | 0.2508 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 23.9% | 51.1% | 48.7% | 0.2512 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 12.8% | 57.3% | 48.1% | 0.2494 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 7.5% | 53.4% | 49.8% | 0.2500 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 4.1% | 46.7% | 49.1% | 0.2502 | 0.2500 |
