import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'features/about/about_screen.dart';
import 'features/alerts/alerts_screen.dart';
import 'features/auth/login_screen.dart';
import 'features/details/details_screen.dart';
import 'features/markets/markets_screen.dart';
import 'features/more/more_screen.dart';
import 'features/shell/shell.dart';
import 'features/signals/signals_screen.dart';
import 'features/splash/splash_screen.dart';
import 'features/track_record/track_record_screen.dart';
import 'features/watchlist/watchlist_screen.dart';
import 'theme/tokens.dart';

/// Every screen and its address. The five tabs live in one shell so the tab bar stays put;
/// the splash and the sign-in screen cover the whole display.
GoRouter buildRouter({String initialLocation = '/splash'}) {
  return GoRouter(
    initialLocation: initialLocation,
    routes: [
      GoRoute(path: '/splash', builder: (_, _) => const SplashScreen()),
      GoRoute(path: '/login', builder: (_, _) => const LoginScreen()),
      StatefulShellRoute.indexedStack(
        builder: (_, _, shell) => AppShell(shell: shell),
        branches: [
          StatefulShellBranch(routes: [
            GoRoute(path: '/markets', builder: (_, _) => const MarketsScreen()),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: '/signals',
              builder: (_, _) => const SignalsScreen(),
              routes: [GoRoute(path: 'details', builder: (_, _) => const DetailsScreen())],
            ),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(path: '/watchlist', builder: (_, _) => const WatchlistScreen()),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(path: '/alerts', builder: (_, _) => const AlertsScreen()),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: '/more',
              builder: (_, _) => const MoreScreen(),
              routes: [
                GoRoute(path: 'track-record', builder: (_, _) => const TrackRecordScreen()),
                GoRoute(path: 'about', builder: (_, _) => const AboutScreen()),
              ],
            ),
          ]),
        ],
      ),
    ],
  );
}

class TradeMatrixApp extends StatefulWidget {
  const TradeMatrixApp({super.key});

  @override
  State<TradeMatrixApp> createState() => _TradeMatrixAppState();
}

class _TradeMatrixAppState extends State<TradeMatrixApp> {
  late final GoRouter _router = buildRouter();

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'TradeMatrix AI',
      debugShowCheckedModeBanner: false,
      theme: buildTheme().copyWith(
        snackBarTheme: SnackBarThemeData(
          behavior: SnackBarBehavior.floating,
          backgroundColor: const Color(0xFF16203C),
          contentTextStyle: TmText.body(14, color: Tm.fg),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
      routerConfig: _router,
    );
  }
}
