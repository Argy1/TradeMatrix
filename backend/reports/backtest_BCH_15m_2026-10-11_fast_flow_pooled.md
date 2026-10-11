# Backtest BCH 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 14941 predictions. Neutral band 0.45-0.55.

**Verdict:** The model does NOT beat the baselines with a margin that survives the bootstrap check. Treat its signals as no better than the simple rules below.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 55.0% | naive 47.8%, reverse 52.2%, always-up 50.1%, always-down 49.9% |
| Flat candles (close equal to the previous close) | 7.4% | |
| Coverage (share of non-neutral calls) | 15.1% | 100% |
| Brier score (lower is better) | 0.2493 | base rate 0.2500 |
| Log loss | 0.6917 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1150 / 55.8% / 8.6% | |
| Down calls: n / precision / recall | 1130 / 54.2% / 8.2% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.12% (0.37% to 12.43%)
- Accuracy minus the best simple rule: 2.43% (-4.56% to 8.00%)
- Brier improvement over base rate: 0.00075 (0.00015 to 0.00137)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -91.0% | -91.0% | -21.13 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -52.12 |
| Buy and hold | -22.3% | -62.5% | -0.35 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.274 | 0.000 |
| 0.3-0.4 | 87 | 0.387 | 0.471 |
| 0.4-0.5 | 7507 | 0.473 | 0.478 |
| 0.5-0.6 | 7318 | 0.527 | 0.525 |
| 0.6-0.7 | 28 | 0.616 | 0.643 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 32.9% | 57.0% | 47.8% | 0.2495 | 0.2500 |
| 52 | 2026-04-26 to 2026-05-10 |  | 3.8% | 45.8% | 48.0% | 0.2494 | 0.2499 |
| 53 | 2026-05-10 to 2026-05-24 |  | 30.1% | 51.4% | 47.5% | 0.2499 | 0.2499 |
| 54 | 2026-05-24 to 2026-06-07 |  | 2.0% | 66.7% | 49.8% | 0.2506 | 0.2499 |
| 55 | 2026-06-07 to 2026-06-21 |  | 0.7% | 66.7% | 47.1% | 0.2491 | 0.2501 |
| 56 | 2026-06-21 to 2026-07-05 |  | 28.1% | 55.5% | 47.5% | 0.2489 | 0.2501 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.3% | 25.0% | 47.0% | 0.2487 | 0.2500 |
| 58 | 2026-07-19 to 2026-08-02 |  | 22.3% | 54.9% | 48.5% | 0.2499 | 0.2500 |
| 59 | 2026-08-02 to 2026-08-16 |  | 9.2% | 56.7% | 46.6% | 0.2485 | 0.2500 |
| 60 | 2026-08-16 to 2026-08-30 |  | 33.5% | 51.9% | 49.2% | 0.2514 | 0.2503 |
| 61 | 2026-08-30 to 2026-09-13 |  | 6.0% | 65.8% | 48.2% | 0.2483 | 0.2500 |
| 62 | 2026-09-13 to 2026-09-27 |  | 12.0% | 61.0% | 46.0% | 0.2470 | 0.2501 |
