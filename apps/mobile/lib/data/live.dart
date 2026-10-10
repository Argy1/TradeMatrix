import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../config.dart';
import 'models.dart';
import 'providers.dart';

enum LiveStatus { connecting, live, offline }

class LiveState {
  const LiveState({this.status = LiveStatus.connecting, this.updating = false});
  final LiveStatus status;

  /// True for up to 30 s after a candle closes, while the worker makes the next signal
  /// (docs/08: "Updating signal...").
  final bool updating;

  LiveState copyWith({LiveStatus? status, bool? updating}) =>
      LiveState(status: status ?? this.status, updating: updating ?? this.updating);
}

/// Live candles and signals for one coin and candle size over `/ws/stream` (docs/04).
///
/// The screens keep working without it, because every provider also refreshes on a timer.
/// The socket reconnects with a growing pause, and it is closed while the app is in the
/// background so the phone is not kept awake for a screen nobody is looking at.
class LiveController extends AutoDisposeFamilyNotifier<LiveState, CoinKey> {
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _messages;
  Timer? _retry, _updatingTimer, _refetchTimer;
  AppLifecycleListener? _lifecycle;
  int _attempt = 0;
  bool _stopped = false, _paused = false;

  @override
  LiveState build(CoinKey arg) {
    _lifecycle = AppLifecycleListener(
      onPause: () {
        _paused = true;
        _close();
      },
      onResume: () {
        if (!_paused) return;
        _paused = false;
        _attempt = 1; // counts as a reconnect: fetch what changed while we were away
        _connect();
      },
    );
    ref.onDispose(() {
      _stopped = true;
      _lifecycle?.dispose();
      _updatingTimer?.cancel();
      _refetchTimer?.cancel();
      _close();
    });
    // Connect after build() returns: a provider may not change its own state while building.
    Future.microtask(_connect);
    return const LiveState();
  }

  void _close() {
    _retry?.cancel();
    _messages?.cancel();
    _channel?.sink.close();
    _channel = null;
  }

  Future<void> _connect() async {
    if (_stopped || _paused) return;
    state = state.copyWith(status: LiveStatus.connecting);
    final uri = Uri.parse('${AppConfig.wsUrl}/ws/stream?symbols=${arg.symbol}&tf=${arg.tf}');
    try {
      final channel = WebSocketChannel.connect(uri);
      _channel = channel;
      await channel.ready;
      if (_stopped || _paused || _channel != channel) return;
      if (_attempt > 0) {
        ref.invalidate(candlesProvider(arg));
        ref.invalidate(predictionProvider(arg));
      }
      _attempt = 0;
      state = state.copyWith(status: LiveStatus.live);
      _messages = channel.stream.listen(_onMessage, onDone: _onClosed, onError: (_) => _onClosed());
    } catch (_) {
      _onClosed();
    }
  }

  void _onClosed() {
    if (_stopped || _paused) return;
    state = state.copyWith(status: LiveStatus.offline);
    _attempt += 1;
    // 2 s, 4 s, 8 s ... up to 30 s between tries.
    final wait = Duration(seconds: math.min(math.pow(2, _attempt).toInt(), 30));
    _retry?.cancel();
    _retry = Timer(wait, _connect);
  }

  void _stopUpdating() {
    _updatingTimer?.cancel();
    if (state.updating) state = state.copyWith(updating: false);
  }

  void _onMessage(dynamic raw) {
    final Json message;
    try {
      message = jsonDecode(raw as String) as Json;
    } catch (_) {
      return; // not ours to understand; ignore it
    }
    final type = message['type'];
    if (type == 'ping') {
      _channel?.sink.add(jsonEncode({'type': 'pong'}));
      return;
    }
    if (message['symbol'] != arg.symbol || message['tf'] != arg.tf) return;

    if (type == 'candle') {
      final candle = message['candle'] as Json;
      ref.read(candlesProvider(arg).notifier).mergeLive(Candle.fromJson(candle));
      if (candle['closed'] == true) {
        state = state.copyWith(updating: true);
        _updatingTimer?.cancel();
        _updatingTimer = Timer(const Duration(seconds: 30), _stopUpdating);
        // The closed candle gets its indicator values from the server a few seconds later.
        _refetchTimer?.cancel();
        _refetchTimer = Timer(const Duration(seconds: 10), () => ref.invalidate(candlesProvider(arg)));
      }
    } else if (type == 'prediction') {
      ref.read(predictionProvider(arg).notifier).setLive(Prediction.fromJson(message['prediction'] as Json));
      ref.invalidate(historyProvider(arg));
      ref.invalidate(marketsProvider);
      _stopUpdating();
    }
  }
}

final liveProvider =
    NotifierProvider.autoDispose.family<LiveController, LiveState, CoinKey>(LiveController.new);
