import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:supabase_flutter/supabase_flutter.dart' show Session, User;
import 'package:tradematrix/app.dart';
import 'package:tradematrix/data/models.dart';
import 'package:tradematrix/data/providers.dart';
import 'package:tradematrix/features/signals/signal_card.dart';
import 'package:tradematrix/theme/tokens.dart';
import 'package:tradematrix/data/live.dart';

import 'fakes.dart';

/// A phone-sized screen with "remove animations" switched on, so the orb stands still and
/// the test can wait for the screen to settle. A layout that overflows at this size fails.
void usePhone(WidgetTester tester) {
  tester.view.physicalSize = const Size(390 * 3, 844 * 3);
  tester.view.devicePixelRatio = 3;
  tester.platformDispatcher.accessibilityFeaturesTestValue =
      const FakeAccessibilityFeatures(disableAnimations: true);
  addTearDown(tester.view.reset);
  addTearDown(tester.platformDispatcher.clearAllTestValues);
}

final _user = User(
  id: '11111111-1111-4111-8111-111111111111',
  appMetadata: const {},
  userMetadata: const {},
  aud: 'authenticated',
  createdAt: '2026-10-01T00:00:00Z',
  email: 'argy@example.test',
);

/// The whole app on fake data: no network, no Supabase, no socket.
Widget appAt(String location, FakeApi api, {bool signedIn = false}) {
  final session = signedIn ? Session(accessToken: 'test-token', tokenType: 'bearer', user: _user) : null;
  return ProviderScope(
    overrides: [
      apiProvider.overrideWithValue(api),
      sessionProvider.overrideWith((ref) => Stream.value(session)),
      liveProvider.overrideWith(FakeLive.new),
    ],
    child: MaterialApp.router(theme: buildTheme(), routerConfig: buildRouter(initialLocation: location)),
  );
}

Widget card(Prediction prediction) => MaterialApp(
      theme: buildTheme(),
      home: Scaffold(
        body: SingleChildScrollView(child: SignalCard(prediction: prediction, coinName: 'Bitcoin')),
      ),
    );

/// Load the app's own typefaces. Without this, tests draw every letter as a wide square
/// and layouts look nothing like the phone.
Future<void> loadAppFonts() async {
  for (final family in const ['Sora', 'DMSans', 'JetBrainsMono']) {
    final loader = FontLoader(family)..addFont(rootBundle.load('assets/fonts/$family.ttf'));
    await loader.load();
  }
}

Future<void> tapVisible(WidgetTester tester, Finder finder) async {
  await tester.ensureVisible(finder);
  await tester.pumpAndSettle();
  await tester.tap(finder);
  await tester.pumpAndSettle();
}

void main() {
  setUpAll(loadAppFonts);

  group('signal card', () {
    testWidgets('shows word, chance, headline, plain sentence and the meter together', (tester) async {
      usePhone(tester);
      await tester.pumpWidget(card(Prediction.fromJson(predictionJson())));
      await tester.pumpAndSettle();

      expect(find.text('UP'), findsOneWidget); // the direction as a word, never color alone
      expect(find.text('58.2%'), findsOneWidget);
      expect(find.text('Buyers have the edge'), findsOneWidget);
      expect(
        find.text(r'58.2% chance the next 1 hour candle closes higher than $67,123.45. '
            'That leaves 41.8% that it does not.'),
        findsOneWidget,
      );
      expect(find.text('Down more likely'), findsOneWidget);
      expect(find.text('Up more likely'), findsOneWidget);
      expect(find.text('Neutral zone 45% to 55%: too close to call'), findsOneWidget);
      // One sentence for screen readers (docs/08 accessibility).
      expect(
        find.bySemanticsLabel(RegExp('Bitcoin, next 1 hour candle: up, 58.2 percent chance')),
        findsOneWidget,
      );
    });

    testWidgets('a Down signal shows the Down chance', (tester) async {
      usePhone(tester);
      await tester.pumpWidget(card(Prediction.fromJson(predictionJson(label: 'down', pUp: 0.38))));
      await tester.pumpAndSettle();
      expect(find.text('DOWN'), findsOneWidget);
      expect(find.text('62.0%'), findsOneWidget);
      expect(find.text('Sellers have the edge'), findsOneWidget);
    });

    testWidgets('Neutral is a first-class answer', (tester) async {
      usePhone(tester);
      await tester.pumpWidget(card(Prediction.fromJson(predictionJson(label: 'neutral', pUp: 0.508))));
      await tester.pumpAndSettle();
      expect(find.text('NEUTRAL'), findsOneWidget);
      expect(find.text('Too close to call'), findsOneWidget);
      expect(find.textContaining('we make no call and show Neutral'), findsOneWidget);
    });
  });

  group('app', () {
    testWidgets('signals screen, then the details behind "Why?"', (tester) async {
      usePhone(tester);
      await tester.pumpWidget(appAt('/signals', FakeApi()));
      await tester.pumpAndSettle();

      expect(find.text('Created by Argy'), findsOneWidget); // the brand line
      expect(find.text('TRADEMATRIX SIGNAL'), findsOneWidget);
      expect(find.text('Buyers have the edge'), findsOneWidget);
      expect(find.text('Sign in to get alerts'), findsOneWidget); // signed out: no dead button
      expect(find.textContaining('Not financial advice. Estimates only.'), findsOneWidget);

      await tapVisible(tester, find.text('Why?'));
      expect(find.text('Bitcoin · 1h'), findsOneWidget);
      expect(find.text('NEXT'), findsOneWidget); // the dashed column for the coming candle
      await tester.scrollUntilVisible(find.text('How reliable is it?'), 300);
      expect(find.text('Why this signal'), findsOneWidget);
      expect(find.text('Baseline: repeat the last move'), findsOneWidget); // never accuracy alone
      await tester.scrollUntilVisible(find.text('A made-up headline for the test'), 300);
      expect(find.textContaining('news is context only'), findsOneWidget);
    });

    testWidgets('markets list shows three chips per coin and flags a weak model', (tester) async {
      usePhone(tester);
      await tester.pumpWidget(appAt('/markets', FakeApi()));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(find.text('Ethereum'), 300);
      expect(find.text('Bitcoin'), findsOneWidget);
      expect(find.text('1d · no signal'), findsWidgets); // a missing signal is said, not hidden
      expect(find.bySemanticsLabel(RegExp('4h: Neutral, 51.0%, model below baseline')), findsWidgets);
    });

    testWidgets('alerts ask a signed-out visitor to sign in', (tester) async {
      usePhone(tester);
      await tester.pumpWidget(appAt('/alerts', FakeApi()));
      await tester.pumpAndSettle();
      expect(find.text('Alerts need an account'), findsOneWidget);
      expect(find.text('New alert'), findsNothing);
    });

    testWidgets('a signed-in person sees notifications and can set an alert in one tap', (tester) async {
      usePhone(tester);
      final api = FakeApi();
      await tester.pumpWidget(appAt('/alerts', api, signedIn: true));
      await tester.pumpAndSettle();
      expect(find.text('BTC 1h signal changed to Up'), findsOneWidget);
      expect(find.text('Mark as read'), findsOneWidget);
      expect(find.text('No alerts yet'), findsOneWidget);
      expect(find.text('0 of 20 used'), findsOneWidget);

      await tester.tap(find.bySemanticsLabel('Signals tab'));
      await tester.pumpAndSettle();
      await tapVisible(tester, find.text('Alert me on change'));
      expect(api.created, 1);
      expect(api.rules.single.type, 'signal_change');
      expect(find.text('Alert is set'), findsOneWidget);

      await tester.tap(find.bySemanticsLabel('Alerts tab'));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(find.text('When the BTC 1h signal changes'), 300);
      expect(find.text('1 of 20 used'), findsOneWidget);
    });
  });

  group('large text and small phones (docs/08 accessibility)', () {
    const screens = ['/signals', '/signals/details', '/markets', '/alerts', '/more', '/more/track-record'];
    for (final location in screens) {
      testWidgets('$location has no overflow at 360 px wide with text at 200%', (tester) async {
        usePhone(tester);
        tester.view.physicalSize = const Size(360 * 3, 780 * 3);
        tester.platformDispatcher.textScaleFactorTestValue = 2.0;
        await tester.pumpWidget(appAt(location, FakeApi(), signedIn: true));
        await tester.pumpAndSettle();
        // Scroll through the whole screen: an overflow anywhere fails the test.
        final scrollable = find.byType(Scrollable).first;
        for (var i = 0; i < 12; i++) {
          await tester.drag(scrollable, const Offset(0, -600));
          await tester.pumpAndSettle();
        }
        expect(tester.takeException(), isNull);
      });
    }
  });

  group('live candles', () {
    Candle bar(int hour, String close, {double? ema}) => Candle(
        t: DateTime.utc(2026, 10, 3, hour), o: '100', h: '110', l: '90', c: close, v: '1', ema9: ema);

    test('a live update replaces the forming candle and keeps its indicator values', () {
      final merged = mergeCandle([bar(13, '100', ema: 99.5)], bar(13, '104'));
      expect(merged, hasLength(1));
      expect(merged.single.c, '104');
      expect(merged.single.ema9, 99.5);
    });

    test('a newer candle is appended, an older message is ignored', () {
      final start = [bar(13, '100', ema: 99.5)];
      final next = mergeCandle(start, bar(14, '105'));
      expect(next, hasLength(2));
      expect(next.last.ema9, isNull); // indicators exist only for closed candles
      expect(mergeCandle(next, bar(12, '1')), same(next));
    });
  });
}
