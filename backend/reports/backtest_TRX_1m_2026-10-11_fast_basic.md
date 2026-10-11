# Backtest TRX 1m (2026-10-11)

Model settings: `fast_basic` (chosen on test folds before 2026-07-01 only, see `reports/tuning_*.md`). The folds below start on or after that date and were scored once. A candle that closes at exactly the previous close is flat: it has no result and is counted neither right nor wrong.

Out-of-sample period: 2026-07-01 to 2026-10-07, 14 walk-forward folds, 70940 predictions. Neutral band 0.45-0.55.

**Verdict:** The model beats the simple rules, and the 95% interval of the edge stays above zero.

| Measure | Model | Baseline |
| --- | --- | --- |
| Accuracy of Up/Down calls | 82.7% | naive 37.1%, reverse 62.9%, always-up 50.5%, always-down 49.5% |
| Flat candles (close equal to the previous close) | 49.7% | |
| Coverage (share of non-neutral calls) | 95.4% | 100% |
| Brier score (lower is better) | 0.1413 | base rate 0.2500 |
| Log loss | 0.4479 | coin flip 0.6931 |
| Up calls: n / precision / recall | 31703 / 85.6% / 75.8% | |
| Down calls: n / precision / recall | 35846 / 80.1% / 81.7% | |

Bootstrap over folds (mean, 95% interval):
- Accuracy minus naive: 45.77% (43.34% to 48.07%)
- Accuracy minus the best simple rule: 19.81% (18.69% to 20.86%)
- Brier improvement over base rate: 0.10929 (0.09904 to 0.11890)

## Simulated long-only strategy (0.1% fee + 0.05% slippage per trade, per coin average)

| Strategy | Total return | Max drawdown | Sharpe |
| --- | --- | --- | --- |
| Model (hold while Up) | -100.0% | -100.0% | -603.16 |
| Naive (hold after an up candle) | -100.0% | -100.0% | -651.26 |
| Buy and hold | 5.5% | -8.1% | 1.09 |

## Reliability (does p mean what it says?)

| p bucket | n | mean p | share that went up |
| --- | --- | --- | --- |
| 0.0-0.1 | 3848 | 0.080 | 0.090 |
| 0.1-0.2 | 15124 | 0.150 | 0.159 |
| 0.2-0.3 | 9908 | 0.244 | 0.228 |
| 0.3-0.4 | 5130 | 0.346 | 0.288 |
| 0.4-0.5 | 3580 | 0.449 | 0.380 |
| 0.5-0.6 | 3225 | 0.550 | 0.522 |
| 0.6-0.7 | 2922 | 0.649 | 0.696 |
| 0.7-0.8 | 3816 | 0.757 | 0.802 |
| 0.8-0.9 | 10780 | 0.858 | 0.875 |
| 0.9-1.0 | 12607 | 0.938 | 0.930 |

## Most useful features (average gain)

- lower_wick_pct: 462.46
- log_ret_1: 385.08
- upper_wick_pct: 265.79
- ret_1: 215.40
- stoch_k: 200.08
- dist_ema9: 133.35
- body_pct: 41.83
- ema9_gt_ema21: 35.81

## Folds

| # | test period | trees | coverage | accuracy | naive | Brier | Brier base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | 2026-07-01 to 2026-07-08 | 792 | 94.1% | 78.8% | 38.5% | 0.1649 | 0.2499 |
| 29 | 2026-07-08 to 2026-07-15 | 796 | 94.9% | 82.4% | 36.1% | 0.1460 | 0.2500 |
| 30 | 2026-07-15 to 2026-07-22 | 799 | 95.5% | 86.2% | 36.5% | 0.1215 | 0.2500 |
| 31 | 2026-07-22 to 2026-07-29 | 795 | 96.3% | 86.0% | 37.0% | 0.1199 | 0.2500 |
| 32 | 2026-07-29 to 2026-08-05 | 799 | 97.0% | 85.8% | 36.0% | 0.1219 | 0.2500 |
| 33 | 2026-08-05 to 2026-08-12 | 797 | 95.8% | 85.6% | 35.3% | 0.1231 | 0.2500 |
| 34 | 2026-08-12 to 2026-08-19 | 799 | 95.9% | 86.3% | 35.2% | 0.1197 | 0.2500 |
| 35 | 2026-08-19 to 2026-08-26 | 800 | 94.5% | 77.7% | 38.3% | 0.1712 | 0.2499 |
| 36 | 2026-08-26 to 2026-09-02 | 798 | 94.2% | 78.9% | 39.7% | 0.1638 | 0.2501 |
| 37 | 2026-09-02 to 2026-09-09 | 799 | 95.8% | 83.5% | 36.1% | 0.1362 | 0.2499 |
| 38 | 2026-09-09 to 2026-09-16 | 793 | 96.0% | 81.7% | 38.8% | 0.1485 | 0.2500 |
| 39 | 2026-09-16 to 2026-09-23 | 800 | 94.2% | 79.4% | 39.0% | 0.1614 | 0.2500 |
| 40 | 2026-09-23 to 2026-09-30 | 800 | 95.2% | 80.5% | 37.0% | 0.1525 | 0.2500 |
| 41 | 2026-09-30 to 2026-10-07 | 800 | 95.7% | 86.3% | 34.7% | 0.1191 | 0.2500 |
