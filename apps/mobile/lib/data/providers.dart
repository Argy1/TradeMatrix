import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../config.dart';
import 'api.dart';
import 'models.dart';

/// One coin at one candle size, e.g. (symbol: 'BTC', tf: '1h'). A Dart record compares by
/// value, so it works as a key for the per-coin providers below.
typedef CoinKey = ({String symbol, String tf});

const timeframes = ['1h', '4h', '1d'];

// ---- session ----

/// The login session, or null when signed out (or when this build has no Supabase values).
final sessionProvider = StreamProvider<Session?>((ref) {
  if (!AppConfig.authConfigured) return Stream.value(null);
  final auth = Supabase.instance.client.auth;
  final controller = StreamController<Session?>();
  controller.add(auth.currentSession);
  final sub = auth.onAuthStateChange.listen((event) => controller.add(event.session));
  ref.onDispose(() {
    sub.cancel();
    controller.close();
  });
  return controller.stream;
});

final apiProvider = Provider<TmApi>((ref) {
  return TmApi(
    TmApi.createDio(AppConfig.apiBaseUrl),
    // Read at call time, so a refreshed token is always the one that is sent.
    accessToken: () =>
        AppConfig.authConfigured ? Supabase.instance.client.auth.currentSession?.accessToken : null,
  );
});

/// Re-run a provider on a timer while a screen is watching it. The worker makes a new
/// signal once per candle, so polling every 30-60 s is plenty next to the live stream.
void _refreshEvery(Ref ref, Duration every) {
  final timer = Timer.periodic(every, (_) => ref.invalidateSelf());
  ref.onDispose(timer.cancel);
}

// ---- what the person is looking at ----

final selectedSymbolProvider = StateProvider<String>((ref) => 'BTC');
final selectedTimeframeProvider = StateProvider<String>((ref) => '1h');

// ---- public data ----

final marketsProvider = FutureProvider.autoDispose<List<MarketRow>>((ref) {
  _refreshEvery(ref, const Duration(seconds: 60));
  return ref.watch(apiProvider).markets();
});

/// The current signal. A class (not a plain FutureProvider) because the live stream can
/// hand it a newer signal the moment the worker makes one.
class PredictionNotifier extends AutoDisposeFamilyAsyncNotifier<Prediction, CoinKey> {
  @override
  Future<Prediction> build(CoinKey arg) {
    _refreshEvery(ref, const Duration(seconds: 30));
    return ref.watch(apiProvider).latestPrediction(arg.symbol, arg.tf);
  }

  void setLive(Prediction prediction) => state = AsyncData(prediction);
}

final predictionProvider =
    AsyncNotifierProvider.autoDispose.family<PredictionNotifier, Prediction, CoinKey>(PredictionNotifier.new);

/// Merge a live candle into the list: replace the bar that is still forming, or append a
/// new one. A late message about an older bar is ignored.
List<Candle> mergeCandle(List<Candle> candles, Candle live) {
  if (candles.isEmpty) return [live];
  final last = candles.last;
  if (last.t == live.t) {
    // Same bar: new prices, and it keeps the indicator values it already had.
    final merged = Candle(
        t: live.t, o: live.o, h: live.h, l: live.l, c: live.c, v: live.v,
        ema9: last.ema9, ema21: last.ema21, ema50: last.ema50); // dart format off
    return [...candles.take(candles.length - 1), merged];
  }
  if (live.t.isBefore(last.t)) return candles;
  // A new bar: indicators exist only for closed candles, so they stay empty here.
  return [...candles, live];
}

class CandlesNotifier extends AutoDisposeFamilyAsyncNotifier<CandlesData, CoinKey> {
  @override
  Future<CandlesData> build(CoinKey arg) {
    _refreshEvery(ref, const Duration(seconds: 60));
    return ref.watch(apiProvider).candles(arg.symbol, arg.tf);
  }

  void mergeLive(Candle live) {
    final current = state.valueOrNull;
    if (current != null) state = AsyncData(current.withCandles(mergeCandle(current.candles, live)));
  }
}

final candlesProvider =
    AsyncNotifierProvider.autoDispose.family<CandlesNotifier, CandlesData, CoinKey>(CandlesNotifier.new);

final historyProvider = FutureProvider.autoDispose.family<List<HistoryItem>, CoinKey>((ref, key) {
  _refreshEvery(ref, const Duration(seconds: 60));
  return ref.watch(apiProvider).history(key.symbol, key.tf);
});

final newsProvider = FutureProvider.autoDispose.family<List<NewsItem>, String>((ref, symbol) {
  _refreshEvery(ref, const Duration(minutes: 5));
  return ref.watch(apiProvider).news(symbol);
});

/// Every coin x candle size in one request (the track-record screen).
final performanceProvider = FutureProvider.autoDispose.family<PerformanceSummary, int>((ref, days) {
  _refreshEvery(ref, const Duration(minutes: 5));
  return ref.watch(apiProvider).performanceSummary(days);
});

// ---- signed-in data ----

class WatchlistNotifier extends AutoDisposeAsyncNotifier<List<String>> {
  @override
  Future<List<String>> build() async {
    final session = await ref.watch(sessionProvider.future);
    if (session == null) return const [];
    return ref.watch(apiProvider).watchlist();
  }

  Future<void> toggle(String symbol) async {
    final watching = state.valueOrNull?.contains(symbol) ?? false;
    state = AsyncData(await ref.read(apiProvider).setWatched(symbol, watched: !watching));
  }
}

final watchlistProvider =
    AsyncNotifierProvider.autoDispose<WatchlistNotifier, List<String>>(WatchlistNotifier.new);

class AlertsNotifier extends AutoDisposeAsyncNotifier<AlertsData> {
  @override
  Future<AlertsData> build() async {
    final session = await ref.watch(sessionProvider.future);
    if (session == null) return const AlertsData(items: [], maxAlerts: 20);
    return ref.watch(apiProvider).alerts();
  }

  Future<void> _reload() async => state = AsyncData(await ref.read(apiProvider).alerts());

  /// Throws [ApiException] with the API's own message when the rule is refused.
  Future<void> create({
    required String symbol,
    required String type,
    String? timeframe,
    String? threshold,
    int cooldownMinutes = 60,
  }) async {
    await ref.read(apiProvider).createAlert(
        symbol: symbol, type: type, timeframe: timeframe, threshold: threshold, cooldownMinutes: cooldownMinutes);
    await _reload();
  }

  Future<void> setActive(String id, {required bool active}) async {
    await ref.read(apiProvider).setAlertActive(id, active: active);
    await _reload();
  }

  Future<void> delete(String id) async => state = AsyncData(await ref.read(apiProvider).deleteAlert(id));
}

final alertsProvider = AsyncNotifierProvider.autoDispose<AlertsNotifier, AlertsData>(AlertsNotifier.new);

class NotificationsNotifier extends AutoDisposeAsyncNotifier<NotificationsData> {
  @override
  Future<NotificationsData> build() async {
    final session = await ref.watch(sessionProvider.future);
    if (session == null) return const NotificationsData(items: [], unread: 0);
    // Signal alerts arrive once per candle and price alerts once a minute.
    _refreshEvery(ref, const Duration(seconds: 60));
    return ref.watch(apiProvider).notifications();
  }

  Future<void> markRead(int id) async {
    await ref.read(apiProvider).markNotificationRead(id);
    state = AsyncData(await ref.read(apiProvider).notifications());
  }
}

final notificationsProvider =
    AsyncNotifierProvider.autoDispose<NotificationsNotifier, NotificationsData>(NotificationsNotifier.new);
