# Backtest BNB 5m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-05 to 2026-10-04, 13 walk-forward folds, 51903 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 51.4% | naive 49.5%, always-up 50.3%, always-down 49.7% |
| Flat candles (close equal to the previous close) | 1.0% | |
| Coverage (share of non-neutral calls) | 15.4% | 100% |
| Brier score (lower is better) | 0.2503 | base rate 0.2500 |
| Log loss | 0.6937 | coin flip 0.6931 |
| Up calls: n / precision / recall | 4244 / 52.9% / 8.6% | |
| Down calls: n / precision / recall | 3735 / 49.6% / 7.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 1.94% (0.54% to 3.40%)
- Accuracy minus the best simple rule: 0.74% (-0.38% to 1.92%)
- Brier improvement over base rate: -0.00027 (-0.00060 to 0.00006)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -87.57 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -211.68 |
| Buy and hold | 33.2% | -27.4% | 1.65 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 203 | 0.386 | 0.522 |
| 0.4-0.5 | 26195 | 0.473 | 0.488 |
| 0.5-0.6 | 25196 | 0.528 | 0.518 |
| 0.6-0.7 | 309 | 0.619 | 0.563 |

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
| 29 | 2026-04-05 to 2026-04-19 |  | 26.1% | 50.8% | 50.8% | 0.2507 | 0.2501 |
| 30 | 2026-04-19 to 2026-05-03 |  | 21.7% | 53.9% | 50.2% | 0.2497 | 0.2500 |
| 31 | 2026-05-03 to 2026-05-17 |  | 33.4% | 51.5% | 49.2% | 0.2513 | 0.2501 |
| 32 | 2026-05-17 to 2026-05-31 |  | 17.6% | 48.5% | 51.8% | 0.2510 | 0.2500 |
| 33 | 2026-05-31 to 2026-06-14 |  | 6.3% | 56.1% | 48.9% | 0.2492 | 0.2500 |
| 34 | 2026-06-14 to 2026-06-28 |  | 8.6% | 51.0% | 48.2% | 0.2495 | 0.2500 |
| 35 | 2026-06-28 to 2026-07-12 |  | 10.6% | 52.0% | 48.1% | 0.2498 | 0.2500 |
| 36 | 2026-07-12 to 2026-07-26 |  | 10.9% | 50.7% | 50.2% | 0.2504 | 0.2500 |
| 37 | 2026-07-26 to 2026-08-09 |  | 18.9% | 50.7% | 49.4% | 0.2501 | 0.2500 |
| 38 | 2026-08-09 to 2026-08-23 |  | 21.7% | 50.8% | 49.0% | 0.2511 | 0.2500 |
| 39 | 2026-08-23 to 2026-09-06 |  | 12.3% | 53.5% | 48.1% | 0.2503 | 0.2500 |
| 40 | 2026-09-06 to 2026-09-20 |  | 6.9% | 49.3% | 49.6% | 0.2503 | 0.2500 |
| 41 | 2026-09-20 to 2026-10-04 |  | 5.0% | 49.5% | 49.7% | 0.2503 | 0.2500 |
