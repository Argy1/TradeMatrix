# Backtest AVAX 15m (2026-10-11)

Model settings: `fast_flow_pooled` (chosen on test folds before 2026-04-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-04-12 to 2026-09-27, 12 walk-forward folds, 15134 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 54.4% | naive 48.1%, always-up 50.1%, always-down 49.9% |
| Flat candles (close equal to the previous close) | 6.2% | |
| Coverage (share of non-neutral calls) | 16.4% | 100% |
| Brier score (lower is better) | 0.2492 | base rate 0.2500 |
| Log loss | 0.6916 | coin flip 0.6931 |
| Up calls: n / precision / recall | 1142 / 54.7% / 8.2% | |
| Down calls: n / precision / recall | 1301 / 54.1% / 9.3% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 7.22% (3.22% to 11.97%)
- Accuracy minus the best simple rule: 4.15% (0.34% to 8.75%)
- Brier improvement over base rate: 0.00087 (0.00029 to 0.00152)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -91.9% | -92.0% | -21.41 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -52.90 |
| Buy and hold | 22.4% | -45.3% | 0.98 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.2-0.3 | 1 | 0.287 | 0.000 |
| 0.3-0.4 | 130 | 0.388 | 0.408 |
| 0.4-0.5 | 7777 | 0.472 | 0.479 |
| 0.5-0.6 | 7209 | 0.526 | 0.526 |
| 0.6-0.7 | 17 | 0.611 | 0.529 |

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
| 51 | 2026-04-12 to 2026-04-26 |  | 38.0% | 57.9% | 44.4% | 0.2469 | 0.2501 |
| 52 | 2026-04-26 to 2026-05-10 |  | 9.1% | 53.3% | 45.3% | 0.2475 | 0.2503 |
| 53 | 2026-05-10 to 2026-05-24 |  | 33.7% | 53.6% | 49.1% | 0.2500 | 0.2500 |
| 54 | 2026-05-24 to 2026-06-07 |  | 3.2% | 55.8% | 51.1% | 0.2491 | 0.2497 |
| 55 | 2026-06-07 to 2026-06-21 |  | 0.6% | 75.0% | 47.3% | 0.2492 | 0.2500 |
| 56 | 2026-06-21 to 2026-07-05 |  | 26.3% | 50.4% | 48.7% | 0.2506 | 0.2500 |
| 57 | 2026-07-05 to 2026-07-19 |  | 0.5% | 42.9% | 48.8% | 0.2494 | 0.2499 |
| 58 | 2026-07-19 to 2026-08-02 |  | 23.9% | 56.1% | 48.3% | 0.2493 | 0.2501 |
| 59 | 2026-08-02 to 2026-08-16 |  | 10.1% | 50.8% | 47.6% | 0.2499 | 0.2500 |
| 60 | 2026-08-16 to 2026-08-30 |  | 34.6% | 54.3% | 48.2% | 0.2496 | 0.2502 |
| 61 | 2026-08-30 to 2026-09-13 |  | 4.8% | 59.4% | 47.2% | 0.2483 | 0.2501 |
| 62 | 2026-09-13 to 2026-09-27 |  | 12.2% | 53.0% | 49.9% | 0.2503 | 0.2501 |
