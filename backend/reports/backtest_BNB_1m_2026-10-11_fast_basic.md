# Backtest BNB 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 134786 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 53.9% | naive 50.6%, always-up 50.3%, always-down 49.7% |
| Flat candles (close equal to the previous close) | 4.5% | |
| Coverage (share of non-neutral calls) | 1.3% | 100% |
| Brier score (lower is better) | 0.2499 | base rate 0.2500 |
| Log loss | 0.6929 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1289 / 53.1% / 1.0% | |
| Down calls: n / precision / recall | 454 / 56.2% / 0.4% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 2.52% (-3.30% to 7.37%)
- Accuracy minus the best simple rule: 2.07% (-3.68% to 6.83%)
- Brier improvement over base rate: 0.00010 (-0.00005 to 0.00025)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -94.0% | -94.0% | -80.01 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -643.58 |
| Buy and hold | 39.1% | -9.6% | 3.64 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.3-0.4 | 9 | 0.391 | 0.444 |
| 0.4-0.5 | 43692 | 0.488 | 0.493 |
| 0.5-0.6 | 91032 | 0.511 | 0.508 |
| 0.6-0.7 | 53 | 0.615 | 0.453 |

## Most useful features (average gain)

- dist_ema21: 12.02
- macd_pct: 11.47
- dist_ema50: 11.08
- atr_pct: 10.55
- rsi14: 10.46
- macd_signal_pct: 10.35
- ret_24: 10.05
- dist_ema9: 9.94

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 262 | 0.6% | 53.6% | 48.8% | 0.2496 | 0.2500 |
| 29 | 2026-07-08 to 2026-07-15 | 232 | 0.8% | 60.7% | 50.0% | 0.2497 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 254 | 0.4% | 59.5% | 50.0% | 0.2496 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 490 | 2.1% | 48.0% | 50.6% | 0.2499 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 160 | 0.0% | n/a | 50.5% | 0.2501 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 27 | 0.0% | n/a | 50.2% | 0.2499 | 0.2499 |
| 34 | 2026-08-12 to 2026-08-19 | 1 | 0.0% | n/a | 52.3% | 0.2503 | 0.2501 |
| 35 | 2026-08-19 to 2026-08-26 | 165 | 0.3% | 37.9% | 50.1% | 0.2503 | 0.2500 |
| 36 | 2026-08-26 to 2026-09-02 | 156 | 0.0% | n/a | 51.5% | 0.2500 | 0.2500 |
| 37 | 2026-09-02 to 2026-09-09 | 5 | 0.0% | n/a | 50.1% | 0.2500 | 0.2499 |
| 38 | 2026-09-09 to 2026-09-16 | 74 | 0.0% | n/a | 50.7% | 0.2503 | 0.2501 |
| 39 | 2026-09-16 to 2026-09-23 | 29 | 0.0% | n/a | 50.4% | 0.2499 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 297 | 3.2% | 56.6% | 52.2% | 0.2492 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 367 | 10.6% | 54.0% | 50.9% | 0.2498 | 0.2500 |
