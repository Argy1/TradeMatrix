# TradeMatrix AI — mobile app (Flutter)

*Created by Argy*

The phone app for TradeMatrix AI. It talks to the same API as the website and shows the same
signals. It is a **thin client**: it never computes an indicator or a probability, it only
draws what the API sends (CLAUDE.md rule 5).

## Run it

```bash
cd apps/mobile
flutter pub get
flutter run --dart-define-from-file=dart_defines.json
```

`dart_defines.json` holds the build values. Copy `dart_defines.example.json` to
`dart_defines.json` and fill in the Supabase URL and anon key (the same public values the
website uses). The file is git-ignored, like the website's `.env.local`.

| Value | What it is |
| --- | --- |
| `API_BASE_URL` | The TradeMatrix API (default: the production API) |
| `WS_URL` | The live stream (default: the production API) |
| `SUPABASE_URL`, `SUPABASE_ANON_KEY` | Sign-in. Without them the app still shows every public signal; only sign-in, watchlist and alerts are off |

Only public values belong in a mobile app. The Gemini key and the Supabase service key never
leave the server.

## Check it

```bash
flutter analyze        # must report no issues
flutter test           # unit and widget tests
```

The widget tests run the whole app on fake data at a phone size. They also check that six
screens do not overflow at 360 px wide with the phone's text size at 200% (docs/08).

### Preview in a browser

There is no Android emulator on the development machine, so the screens are previewed as a
web build. The `web/` folder exists only for this; the product targets Android and iOS.

```bash
flutter build web --dart-define-from-file=dart_defines.json
python -m http.server 3000 --bind 127.0.0.1 --directory build/web
```

Port 3000 matters: the API only accepts browser requests from the website's own addresses,
and `http://localhost:3000` is one of them.

## How the code is laid out

```
lib/
  main.dart, app.dart      start-up, every screen and its address (go_router)
  config.dart              build values (public ones only)
  theme/tokens.dart        "Matrix Glass" colors, type and shape (docs/08)
  core/                    formatting and the words around a signal (same sentences as the web)
  data/                    API client, models, providers (Riverpod), live stream
  widgets/                 the 3D building blocks: glass card, keycap buttons, orb, meter, logo
  features/                one folder per screen: signals, details, markets, watchlist,
                           alerts, more, track_record, about, auth, splash, shell (tab bar)
test/                      formatting and wording, the signal card, the app on fake data
assets/fonts/              Sora, DM Sans, JetBrains Mono (SIL Open Font License, texts included)
tool/make_icons.py         draws the app icon in every size (see "App icon" below)
```

## Install it on an Android phone

```bash
flutter build apk --release --dart-define-from-file=dart_defines.json
```

The file is `build/app/outputs/flutter-apk/app-release.apk` (about 51 MB). Copy it to the
phone and open it; Android asks once to allow installing from that source. This build is
signed with Flutter's debug key: fine for your own phone, not for a store.

Add `--split-per-abi` for smaller files, one per processor type (about 18 MB each). Almost
every phone from the last years takes `app-arm64-v8a-release.apk`.

## App icon

The icon is the logo tile from `lib/widgets/brand.dart`, drawn again by a small Python script
so that the icon and the in-app logo stay the same:

```bash
uv run --with pillow python tool/make_icons.py
```

It writes the Android icons (old style and "adaptive"), the iOS icons and the web preview
icons. The window is dark from the first moment the app starts (`res/values/colors.xml`), so
there is no white flash before the splash screen.

## The 3D look

Everything is drawn with Flutter's own painting, no images and no 3D engine:

- **Orb** (`widgets/orb.dart`): a sphere made of five painted layers (glow, body, shade, rim,
  highlight) inside a probability ring. It bobs 5 px and stands still when the phone asks for
  reduced motion.
- **Keycap buttons** (`widgets/keycap.dart`): a face over a hard shadow; pressing moves the
  face 3 px toward the shadow.
- **Glass cards** (`widgets/glass.dart`): gradient, hairline border, lit top edge, two shadows.
- **Isometric candle scene and logo** (`widgets/brand.dart`), **floor grid**
  (`widgets/background.dart`): plain geometry, explained in the comments.
- **Chart** (`features/details/candle_chart.dart`): candles, volume, EMA lines and the dashed
  NEXT column, painted by hand.

## Not in the app yet

- **Push notifications.** They need a Firebase project, which Argy has to create. Alerts and
  the notification list already work inside the app.
- **Google sign-in.** It needs a Google OAuth client. Email sign-in works.
