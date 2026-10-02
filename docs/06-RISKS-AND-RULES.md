# 06 — Risks, legal, security and honesty rules

*Created by Argy*

This is general information, not legal advice. Argy should consult a lawyer before any public launch.

## Mandatory disclaimer text

Show on every signal screen (web and mobile), the About page and the footer:

> Signals are probabilistic estimates for information and education only, not financial advice. Crypto is volatile and you can lose all the money you invest. Past performance does not guarantee future results. TradeMatrix AI does not execute trades.

Short version for tight spaces: `Not financial advice. Estimates only.`

## Honesty rules

- Never claim or display an accuracy number that is not computed from stored predictions and outcomes.
- Always show the baseline next to the model, and show `low_sample` warnings when `n` is small.
- Forbidden words in copy: "guaranteed", "sure", "risk-free", "100%", "never loses", "profit assured".
- Neutral is a valid, shown answer. Do not force Up/Down when probability is between 45% and 55%.
- If the model is marked `degraded` or data is `stale`, show a visible warning instead of a confident signal.

## Risk register

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Accuracy near a coin flip | Users over-trust signals | Probabilities, Neutral band, baseline + live track record on every signal screen |
| Overfitting / data leakage | Great backtest, bad live results | Time-based splits, walk-forward, closed candles only, no-leakage tests |
| Model drift | Markets change regime | Weekly retrain, rolling live accuracy, `degraded` flag |
| Regulation | Publishing trading signals can count as investment advice in some jurisdictions; crypto is supervised by financial regulators in Indonesia | Legal check (OJK rules) before a public launch; start as a private beta; keep the disclaimer |
| Data terms and limits | Free APIs restrict commercial use, rate and region | Read provider terms, adapters with a fallback exchange, caching, respect rate limits |
| LLM errors | Gemini can misread sarcasm, rumors or fake news | JSON schema, confidence threshold, shadow mode (`k = 0`) until evaluated, small max `k`, headlines treated as untrusted text |
| Prompt injection via headlines | A headline could contain instructions | Prompt says to ignore instructions in headlines, schema-validated output only, no tools or actions given to the model |
| Cost creep | LLM calls and hosting grow | Score each headline once, batch, daily budget guard, monthly budget alerts on Railway/Google |
| Exchange outage / ban of region | No data | Adapter interface, stale flag, retry with backoff |
| Duplicate worker runs | Duplicate predictions or pushes | One worker replica, advisory locks, unique constraints, idempotent upserts |

## Security checklist

- [ ] No secrets in git (check with a secret scanner before the first push). `.env*` ignored.
- [ ] Gemini key, service-role key and Firebase credentials only in Railway variables.
- [ ] Web/mobile only hold the Supabase URL + anon key.
- [ ] RLS enabled on every table; policies reviewed; the API filters by JWT `user_id` on every user query.
- [ ] JWT verification checks signature, expiry and audience; protected routes reject missing/invalid tokens.
- [ ] Input validation with pydantic everywhere; limits on list sizes; parameterized SQL only.
- [ ] CORS restricted to the real web origins in production.
- [ ] Rate limiting on public endpoints; WebSocket connection and symbol limits.
- [ ] Dependency updates and `npm audit` / `pip-audit` before launch.
- [ ] Account deletion removes the user's rows (cascade) — needed for privacy.
- [ ] Privacy policy lists what is stored: email, watchlist, alerts, device tokens.

## Things Claude Code must never do in this project

- Add exchange trading, withdrawal, or any key that can move money.
- Show "profit" projections or price targets as facts.
- Commit credentials, call Gemini from a client app, or disable RLS to "make it work".
- Change the disclaimer or brand line without Argy's approval.
