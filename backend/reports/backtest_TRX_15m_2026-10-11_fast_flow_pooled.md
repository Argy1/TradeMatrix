# Backtest TRX 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 13026 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 56.1% | naive 48.2%, always-up 51.9%, always-down 48.1% |
| Flat candles (close equal to the previous close) | 19.2% | |
| Coverage (share of non-neutral calls) | 9.6% | 100% |
| Brier score (lower is better) | 0.2496 | base rate 0.2502 |
| Log loss | 0.6923 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1131 / 56.7% / 9.5% | |
| Down calls: n / precision / recall | 158 / 51.9% / 1.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 6.21% (-0.28% to 11.31%)
- Accuracy minus the best simple rule: 2.53% (-3.24% to 7.51%)
- Brier improvement over base rate: 0.00066 (0.00003 to 0.00130)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -92.7% | -92.7% | -54.48 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -142.04 |
| Buy and hold | 3.4% | -17.1% | 0.49 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 5 | 0.372 | 0.800 |
| 0.4-0.5 | 4523 | 0.484 | 0.507 |
| 0.5-0.6 | 8466 | 0.526 | 0.524 |
| 0.6-0.7 | 32 | 0.612 | 0.719 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 19.9% | 56.6% | 48.6% | 0.2490 | 0.2504 |
| 52 | 2026-04-26 to 2026-05-10 |  | 0.4% | 50.0% | 48.6% | 0.2489 | 0.2506 |
| 53 | 2026-05-10 to 2026-05-24 |  | 22.4% | 56.7% | 48.0% | 0.2479 | 0.2507 |
| 54 | 2026-05-24 to 2026-06-07 |  | 0.7% | 66.7% | 53.3% | 0.2509 | 0.2498 |
| 55 | 2026-06-07 to 2026-06-21 |  | 0.0% | n/a | 45.7% | 0.2500 | 0.2505 |
| 56 | 2026-06-21 to 2026-07-05 |  | 4.5% | 51.9% | 47.7% | 0.2501 | 0.2501 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.0% | n/a | 44.9% | 0.2489 | 0.2501 |
| 58 | 2026-07-19 to 2026-08-02 |  | 5.9% | 57.8% | 45.3% | 0.2488 | 0.2502 |
| 59 | 2026-08-02 to 2026-08-16 |  | 8.8% | 64.1% | 45.7% | 0.2490 | 0.2500 |
| 60 | 2026-08-16 to 2026-08-30 |  | 27.9% | 59.2% | 49.6% | 0.2495 | 0.2502 |
| 61 | 2026-08-30 to 2026-09-13 |  | 20.6% | 53.4% | 49.9% | 0.2503 | 0.2500 |
| 62 | 2026-09-13 to 2026-09-27 |  | 4.5% | 32.1% | 49.7% | 0.2512 | 0.2500 |
