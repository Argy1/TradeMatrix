# 08 — Design system: "Matrix Glass" 3D

*Created by Argy*

Visual reference (private design canvas with 4 screens): https://claude.ai/artifact/BUz76hjCKjqaqFWxXSgt9Y
Screens in it: Web coin detail (interactive), Web markets home, Mobile signal, Mobile details. If a mockup and this file disagree, **this file wins**. All numbers in the mockups are sample data.

## Design goals

1. **Understandable by everyone.** A first-time user must read a signal in 10 seconds without knowing trading terms.
2. **Informative.** Direction, probability, validity window, reasons, and proof of past performance are always visible together.
3. **3D, but calm.** Depth through glass, bevels, extruded buttons, one hero 3D orb and one isometric 3D scene. Motion is gentle and optional.
4. **Honest.** Neutral is a first-class state; the baseline and disclaimer are always shown.

## Look in one line

Deep navy space background, frosted-glass panels with a lit top edge, tactile extruded "keycap" buttons, a glowing 3D orb with a probability ring as the hero, and an isometric 3D candlestick scene on the home page.

## Tokens

### Color

| Token | Value | Use |
| --- | --- | --- |
| `bg-base` | `#060913` | Page background |
| `bg-glow-violet` | `rgba(124,92,255,.26)` | Radial glow top right |
| `bg-glow-cyan` | `rgba(77,216,255,.16)` | Radial glow top left |
| `glass` | gradient `rgba(255,255,255,.075)` to `.025`, border `rgba(255,255,255,.10)` | Cards |
| `text-primary` | `#EAF0FF` | Main text |
| `text-secondary` | `#B4C0DC` / `#C9D4EE` | Body copy |
| `text-muted` | `#9AA8C7` / `#8FA0C4` | Captions (never below 12px) |
| `brand-cyan` | `#4DD8FF` (button gradient `#7BE8FF` to `#3FC4EE`) | Brand accent, primary button |
| `brand-violet` | `#7C5CFF` | Selected state, logo gradient |
| `up` | `#2EE6A6` (soft `rgba(46,230,166,.16)`, border `.45`) | Up signal, rising candle |
| `down` | `#FF5C7A` (text on dark `#FF8FA3`) | Down signal, falling candle |
| `neutral` | `#FFC857` | Neutral signal and the 45-55% zone |
| `ema9 / ema21 / ema50` | `#4DD8FF` / `#B49BFF` / `#FFC857` | Chart lines |

Rules: up/down/neutral are **never the only cue**; always add the arrow/dash icon and the word. Text on dark must reach AA contrast (4.5:1, 3:1 for 24px+). The accent can be swapped (cyan, violet or green) from a single token.

### Typography

- Display and headings: **Sora** (600/700/800).
- Body and UI: **DM Sans** (400/500/600/700).
- Prices, percentages, tables: **JetBrains Mono** (tabular numbers).
- Sizes (web): H1 40–54, H2 22–30, signal word 38, body 15–17, caption 12–13. Mobile: H1 28, body 14.5–15, caption 12 (never smaller).

### Shape, depth, motion

- Radii: cards 24, buttons and chips 14–16, tiles 16, pills 999.
- Glass shadow: `inset 0 1px 0 rgba(255,255,255,.14), 0 28px 50px -22px rgba(0,0,0,.75), 0 3px 0 rgba(0,0,0,.35)`; blur 14px on web.
- Keycap (secondary button): gradient `rgba(255,255,255,.12)` to `.04`, border `rgba(255,255,255,.12)`, extrusion `0 4px 0 rgba(0,0,0,.5)`; pressed = translateY(3px) and extrusion 1px.
- Primary button: gradient `#7BE8FF` to `#3FC4EE`, extrusion `0 4px 0 #1B7FA3`, glow `0 12px 26px rgba(63,196,238,.32)`, dark text `#04121A`.
- Motion: orb bobs 6px over 5 s; press transitions 80 ms. **Honor `prefers-reduced-motion`** (disable the bob). No parallax, no auto-playing heavy 3D.

## 3D building blocks (web, pure CSS, no WebGL needed)

1. **Glass card:** the glass style above.
2. **Signal orb (hero):** a 156 px circle with two radial gradients (a white specular highlight at 32%/26% and a color body `c1` to `c2` to near-black), outer glow, inner shadows `inset -16px -20px 34px rgba(0,0,0,.55)` and `inset 10px 12px 22px rgba(255,255,255,.22)`. Around it a **probability ring**: `conic-gradient(color X deg, rgba(255,255,255,.09) 0)` with a radial mask to make a 12 px donut, where `X = displayed_probability * 3.6`. Under it a blurred glow ellipse as a floor shadow. The word (UP / DOWN / NEUTRAL) and the percentage are centered on the orb.
   - Up: `c1 #34F0B0`, `c2 #0A6E53`, glow `rgba(46,230,166,.55)`.
   - Down: `c1 #FF7E96`, `c2 #8C1B38`, glow `rgba(255,92,122,.5)`.
   - Neutral: `c1 #FFD98A`, `c2 #8A5F0E`, glow `rgba(255,200,87,.45)`.
3. **Perspective floor grid** behind the page header: a 56 px cyan grid with `transform: perspective(520px) rotateX(64deg)` fading out with a mask.
4. **Isometric candle scene (home hero):** a `perspective: 1400px` scene; inside, a group with `transform-style: preserve-3d; transform: rotateX(58deg) rotateZ(-40deg)`; a glowing floor tile; each candle is a box made of 3 faces (top at `translateZ(h)`, front `rotateX(90deg)` from `transform-origin: top`, side `rotateY(-90deg)` from `transform-origin: left`), shaded light/mid/dark. Five solid candles (green/red) plus one dashed translucent "ghost" candle for the predicted next move. It is decorative: `role="img"` with an `aria-label`.
5. **Logo mark:** 42 px rounded square, cyan-to-violet gradient with a faint 10 px grid, extruded `0 4px 0 #3B2FA8`. The brand text is `TradeMatrix AI` with `AI` in the accent color, and **"Created by Argy"** under it in 12 px muted text. This lockup appears in the web header and footer, the Flutter app bar and splash screen, and the About page.

### Flutter equivalents

- Glass: `Container` with `LinearGradient`, 1 px border, `BoxShadow` list; use `BackdropFilter` sparingly (not inside long lists) for performance.
- Keycap/primary buttons: `DecoratedBox` with gradient and a second `BoxShadow(offset: Offset(0, 4), blurRadius: 0)`; animate the offset to 1 on press.
- Orb: `RadialGradient` circles stacked in a `Stack`; ring with a `CustomPainter` drawing an arc with `SweepGradient`/stroke cap round; wrap in `RepaintBoundary`; bob with an `AnimationController` that respects `MediaQuery.disableAnimations`.
- Isometric scene is **web only**; on mobile use a static image or skip it.

## Layout

### Web
- Max content width 1376 px, 32 px side padding; header with logo lockup, nav (Markets, Track record, Watchlist, How it works) and Sign in / Create free account.
- **Coin page:** page title as a question ("Will Bitcoin rise or fall in the next 1h?") with a one-line subtitle; coin selector (each coin button shows its current direction word) and candle-size selector (1h/4h/1d); dismissible 3-step "How to read a signal" strip. Two columns: left = chart, recent signals, news; right = **the signal card**. Columns wrap to one column below ~1050 px with the signal card first on phones.
- **Markets page:** hero (headline, subtitle, two buttons, three trust points, 3D scene), "Today's signals" list where each coin row shows price, change and **three chips (1h, 4h, 1d)** with direction + probability, a 3-card "How a signal is made" section, and a track-record strip.

### Mobile (390 px reference)
- Screen 1 (above the fold): app bar (logo lockup + bell), horizontally scrollable coin chips with direction words, candle-size segmented keys, **the signal card** (orb, headline, plain-language sentence, meter), primary button "Alert me on change" and a "Why?" button, disclaimer one-liner.
- Screen 2 (details): back button + title + signal chip; chart with a dashed NEXT column; Why this signal; How reliable is it; Recent signals tiles; full disclaimer.
- Bottom tab bar: Markets, Signals, Watchlist, Alerts, More. Icons plus visible 12 px labels; touch targets at least 44 px (56 px for tabs).

## The signal card (the most important component)

Order, top to bottom:

1. Caption: `TRADEMATRIX SIGNAL` and `for the next {tf} candle`.
2. Orb with ring: word (UP / DOWN / NEUTRAL) and probability (for Down show the down probability; for Neutral show the up probability and the word NEUTRAL).
3. Headline: `Buyers have the edge` / `Sellers have the edge` / `Too close to call`.
4. One sentence in plain words, for example `58.2% chance the next 1h candle closes higher than $67,123.45. That leaves 41.8% that it does not.` Neutral: `Up 50.8% versus down 49.2%. When the odds are this close we make no call and show Neutral.`
5. **Probability meter:** a bar from `Down more likely` (red) through the neutral zone (amber outline from 45% to 55%) to `Up more likely` (green) with a 3D knob at `p_up`, plus the labels 0%, 45%, 55%, 100% and the text `Neutral zone: too close to call`.
6. Validity line with a clock icon: `Valid for the 1h candle that closes at 22:00 WIB, in 41 min. A new signal appears right after it closes.` (WIB display; data in UTC).
7. **Why this signal** (up to 3): icon bubble (arrow or dash), bold title, one plain sentence, and a tag `Pushes up` / `Pushes down` / `No clear push`. Texts come from deterministic templates (docs/03), never free LLM text.
8. **How reliable is it?** Two bars (model accuracy vs the baseline "repeat the last move") on a 40%–60% scale, `n` resolved signals, and a sentence such as `The model beat the baseline by 2.9 points. That is a small edge, which is normal for crypto.` If the model does not beat the baseline, say so in the same place.
9. Amber disclaimer box (text in docs/06).
10. Primary button `Alert me when this signal changes`.

## Other components

- **Chart:** candles with a soft glow and a lit left edge, volume bars under them, EMA 9/21/50 lines, a dashed last-price line with a white price tag on the right axis, relative time labels (`48h ago`, `Now`), and the **NEXT ghost column** on the right edge: dashed border in the signal color, tint, icon, probability. The legend names every line and candle color.
- **Coin buttons:** keycap with symbol and the direction word in its color; selected = violet gradient and border.
- **Recent signals tiles:** 68 × 76 px keycaps with an arrow/dash icon and the word `Hit`, `Miss` or `Skip`; summary line `7 of 11 calls correct, 1 skipped as Neutral`.
- **News row:** headline, `[Source] · time`, and a sentiment badge `Bullish +0.31` / `Bearish -0.22` / `Neutral +0.02`.
- **Track-record strip:** three stat tiles (signals recorded, accuracy last 30 days, simple baseline) with the title `We show our results, even when they are poor`.
- **How-to-read strip:** three numbered steps (Direction, Chance, Reliability), dismissible, with a `Show the 3-step guide` link after hiding. Remember the choice per user.

## Copy rules

- Plain words first. Say `chance` and `candle`, explain jargon in one sentence the first time (`RSI 38, recovering: momentum is turning up after a dip`).
- Always say what a number means (`58.2% chance ... closes higher than $67,123.45`).
- Forbidden: guaranteed, sure, risk-free, 100%, will reach $X, buy now, sell now.
- Label sample or placeholder data clearly in mockups and demos; never ship sample numbers to production.

## States to design and build

- **Loading:** skeleton glass cards with a shimmer (reduced-motion: static).
- **Empty:** watchlist and alerts get a short explanation and one clear button.
- **Error / offline:** plain message, retry button, last known data marked `Updated 12 min ago`.
- **Stale data:** banner `Data is delayed. Signals may be out of date.` (from the API `stale` flag).
- **Degraded model:** banner above the signal card `This model is performing below the baseline right now. Treat the signal with extra caution.`
- **Candle just closed:** show `Updating signal...` for up to 30 seconds, then the new signal with a brief highlight (no flashing).

## Accessibility checklist

- [ ] Real buttons and links, visible focus ring (3 px white outline), keyboard operable on web.
- [ ] Icon-only buttons have `aria-label`; decorative 3D has `aria-hidden` or a short `aria-label`.
- [ ] Contrast AA on all text; direction is never conveyed by color alone.
- [ ] Touch targets at least 44 px; text at least 12 px on mobile.
- [ ] `prefers-reduced-motion` respected; the app is fully usable with the orb static.
- [ ] Works at 360 px width and with 200% text zoom.
- [ ] Screen reader reads the signal as one sentence: `Bitcoin, next 1 hour candle: Up, 58.2 percent chance. Neutral zone is 45 to 55 percent.`

## Implementation order

1. Create the tokens first: Tailwind theme (colors, radii, shadows, fonts) and CSS utilities `glass`, `btn-3d`, `key`, `orb`, `tile`; mirror them as a Flutter `ThemeData` and `ThemeExtension` in Phase 5.
2. Build components in this order: SignalCard (with the orb and meter), CoinChip, TimeframeSwitch, Chart, ReasonRow, ReliabilityBars, SignalTile, NewsRow, GuideStrip, AppHeader/TabBar.
3. Then pages: Coin detail, Markets, Track record, Watchlist, Alerts, About.
4. Take screenshots with Playwright at 1440, 1024, 768 and 390 px and compare with the design canvas; fix differences before moving on.
