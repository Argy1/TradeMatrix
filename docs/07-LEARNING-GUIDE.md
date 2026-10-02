# 07 — Learning guide for Argy

*Created by Argy*

Claude Code: while building, point Argy to the matching concept below in one line when you introduce it. Argy is here to learn, so prefer clear code over clever code.

## Glossary

| Term | Meaning |
| --- | --- |
| Candle (OHLCV) | Open, High, Low, Close price and Volume for one period (1h, 4h or 1d) |
| Closed candle | A finished period; the open candle is still changing and must not be used for features |
| RSI | Momentum indicator 0–100; above ~70 often "overbought", below ~30 "oversold" |
| EMA | Exponential moving average; reacts faster than a simple average |
| MACD | Difference of two EMAs plus a signal line; shows momentum shifts |
| Bollinger Bands | Moving average with bands at ±2 standard deviations; shows volatility |
| ATR | Average true range; typical candle size, a volatility measure |
| Label | The answer the model learns: did the next candle close higher (1) or not (0) |
| Data leakage | Using information from the future when building features; makes backtests look fake-good |
| Walk-forward | Train on the past, test on the next period, roll forward; mimics live use |
| Baseline | A dumb strategy to beat (e.g. "same direction as last candle") |
| Calibration | Making `0.60` really mean "right about 60% of the time" |
| Brier score | Mean squared error of probabilities; lower is better, 0.25 is a coin flip |
| Overfitting | A model memorizing noise; great on past data, poor on new data |
| Shadow mode | Computing and storing a signal without using it yet, so it can be evaluated safely |
| JWT | The signed login token issued by Supabase Auth and verified by the API |
| RLS | Row Level Security: Postgres rules that decide which rows a user may read or write |
| Idempotent | Running it twice gives the same result as running it once |

## Learning order (matches the roadmap)

| # | Skill | Practice task | Needed in |
| --- | --- | --- | --- |
| 1 | Python + pandas | Download 1 year of BTC 1h candles, compute returns, plot them | Phase 1 |
| 2 | Technical indicators | Compute RSI and EMA by hand in pandas and compare with a library | Phase 1–2 |
| 3 | ML for time series | Train XGBoost on next-candle direction and compare with the naive baseline | Phase 2 |
| 4 | Backtesting | Walk-forward test with 0.1% fees; read the report | Phase 2 |
| 5 | FastAPI + Postgres | Build `/v1/candles` over a real table and test it with pytest | Phase 1 |
| 6 | Next.js + Lightweight Charts | Render a live BTC chart from your API | Phase 3 |
| 7 | Gemini structured output | Score 50 headlines and compare with your own labels | Phase 4 |
| 8 | Flutter + Riverpod | Coin list screen, then a chart screen against the same API | Phase 5 |
| 9 | Deployment + CI | Deploy API/worker to Railway and web to Vercel; add GitHub Actions | Phase 1, 3, 6 |

## Habits

- Write the baseline and the backtest before the fancy model.
- Commit small and often; one working feature per day beats a big rewrite.
- When a result looks too good, assume a bug first.
- After each phase, explain the system out loud (or in writing) in five minutes. If you cannot, ask Claude Code to walk through the part you missed.
