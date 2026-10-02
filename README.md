# TradeMatrix AI

*Created by Argy*

Crypto market signals (Up / Down / Neutral with a probability) on web and mobile, powered by technical indicators, an XGBoost model and Gemini news sentiment.

This repository starts as a **plan**. The plan lives in `CLAUDE.md` and `docs/`. Claude Code reads it and builds the product phase by phase.

## Plan files

| File | Contents |
| --- | --- |
| `CLAUDE.md` | Rules, stack, conventions, status. Claude Code loads it automatically. |
| `docs/01-PRODUCT.md` | Vision, scope, screens, brand, disclaimer |
| `docs/02-ARCHITECTURE.md` | Architecture, stack, jobs, env vars, deployment |
| `docs/03-PREDICTION-ENGINE.md` | Data, features, model, backtest, Gemini sentiment, blending |
| `docs/04-DATABASE-AND-API.md` | Database tables, RLS, REST and WebSocket contract |
| `docs/05-ROADMAP.md` | Six phases with task checklists and gates |
| `docs/06-RISKS-AND-RULES.md` | Legal, security, honesty rules, disclaimer text |
| `docs/07-LEARNING-GUIDE.md` | Glossary and what to learn in which order |
| `docs/08-DESIGN.md` | "Matrix Glass" 3D design system, signal card spec, UX and accessibility rules |
| `supabase/migrations/` | Ready-to-apply SQL for the first schema |

## Prerequisites

Install: Git, Node.js (current LTS), Python 3.12 and `uv`, the Flutter SDK, the Supabase CLI, the Railway CLI. Accounts: Supabase, Railway, Vercel, Firebase (later), Google AI Studio (Gemini key).

## How to start with Claude Code

1. Open a terminal in this folder and run `claude`.
2. Paste this first message:

```
Read CLAUDE.md and every file in docs/. Summarize in 10 lines what we are building and the order of work. Then start Phase 0 in docs/05-ROADMAP.md. Ask me only for things you cannot decide yourself (accounts, keys, the Gemini model name).
```

3. After each phase, ask: `Run the gate checks for this phase and tell me if we can move on.`

## Copy-paste prompts per phase

- Phase 1: `Do Phase 1 (Foundations) from docs/05-ROADMAP.md. Explain each file you create in one line.`
- Phase 2: `Do Phase 2 (Prediction engine v1). Show me the walk-forward backtest report and whether the model beats the baseline.`
- Phase 3: `Do Phase 3 (Web MVP).`
- Phase 4: `Do Phase 4 (Sentiment and alerts), starting with sentiment in shadow mode.`
- Phase 5: `Do Phase 5 (Flutter app).`
- Phase 6: `Do Phase 6 (Hardening and launch).`
