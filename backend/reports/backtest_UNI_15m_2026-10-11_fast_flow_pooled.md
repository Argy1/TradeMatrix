# Backtest UNI 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 15569 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.3% | naive 48.3%, always-up 49.6%, always-down 50.4% |
| Flat candles (close equal to the previous close) | 3.5% | |
| Coverage (share of non-neutral calls) | 18.2% | 100% |
| Brier score (lower is better) | 0.2501 | base rate 0.2500 |
| Log loss | 0.6935 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1287 / 53.1% / 8.8% | |
| Down calls: n / precision / recall | 1515 / 53.5% / 10.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 9.07% (4.97% to 14.07%)
- Accuracy minus the best simple rule: 6.11% (2.16% to 11.05%)
- Brier improvement over base rate: -0.00016 (-0.00091 to 0.00048)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -91.8% | -91.8% | -18.85 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -36.53 |
| Buy and hold | 215.1% | -43.7% | 3.08 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.291 | 1.000 |
| 0.3-0.4 | 137 | 0.386 | 0.533 |
| 0.4-0.5 | 8211 | 0.471 | 0.481 |
| 0.5-0.6 | 7203 | 0.528 | 0.513 |
| 0.6-0.7 | 17 | 0.608 | 0.529 |

## Most useful features (average gain)

- dist_ema9: 148.33
- log_ret_1: 106.96
- ret_1: 105.80
- stoch_k: 71.16
- dist_ema21: 47.48
- btc_ret_1: 45.09
- ret_6: 40.41
- rsi14: 35.17

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51 | 2026-04-12 to 2026-04-26 |  | 38.5% | 50.0% | 48.6% | 0.2524 | 0.2501 |
| 52 | 2026-04-26 to 2026-05-10 |  | 9.8% | 53.5% | 49.5% | 0.2496 | 0.2503 |
| 53 | 2026-05-10 to 2026-05-24 |  | 33.3% | 50.8% | 48.0% | 0.2510 | 0.2497 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.6% | 63.6% | 49.5% | 0.2496 | 0.2498 |
| 55 | 2026-06-07 to 2026-06-21 |  | 1.2% | 78.6% | 46.8% | 0.2495 | 0.2501 |
| 56 | 2026-06-21 to 2026-07-05 |  | 31.5% | 53.0% | 48.3% | 0.2507 | 0.2500 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.4% | 60.0% | 47.4% | 0.2495 | 0.2499 |
| 58 | 2026-07-19 to 2026-08-02 |  | 31.6% | 52.7% | 45.3% | 0.2495 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 13.9% | 60.3% | 46.7% | 0.2487 | 0.2498 |
| 60 | 2026-08-16 to 2026-08-30 |  | 34.1% | 51.9% | 50.6% | 0.2527 | 0.2502 |
| 61 | 2026-08-30 to 2026-09-13 |  | 6.0% | 51.9% | 48.7% | 0.2499 | 0.2499 |
| 62 | 2026-09-13 to 2026-09-27 |  | 15.3% | 61.6% | 49.6% | 0.2485 | 0.2501 |
