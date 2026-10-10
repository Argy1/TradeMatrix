import 'package:dio/dio.dart';
import 'package:tradematrix/data/api.dart';
import 'package:tradematrix/data/live.dart';
import 'package:tradematrix/data/models.dart';
import 'package:tradematrix/data/providers.dart';

/// JSON exactly as the API sends it (docs/04), so the tests also cover the parsing.
Json predictionJson({String label = 'up', double pUp = 0.582, String status = 'ok', bool stale = false}) => {
      'symbol': 'BTC',
      'timeframe': '1h',
      'label': label,
      'p_up': pUp,
      'base_open_time': '2026-10-03T13:00:00Z',
      'target_open_time': '2026-10-03T14:00:00Z',
      'target_close_time': '2026-10-03T15:00:00Z',
      'base_close': '67123.45',
      'reasons': [
        {'code': 'rsi', 'text': 'RSI 38: momentum down', 'effect': 'down'},
        {'code': 'ema_trend', 'text': 'Close above EMA 50 by 0.6%', 'effect': 'up'},
        {'code': 'macd', 'text': 'MACD histogram positive', 'effect': 'up'},
      ],
      'sentiment_agg': 0.12,
      'sentiment_used': false,
      'model': {'id': 12, 'trained_at': '2026-09-28T02:10:00Z', 'status': status},
      'recent_accuracy': {'model': 0.541, 'naive_baseline': 0.512, 'n': 200, 'low_sample': false},
      'disclaimer': 'Signals are probabilistic estimates for information and education only, not financial advice.',
      'stale': stale,
    };

Json marketJson(String symbol, String name) => {
      'symbol': symbol,
      'name': name,
      'last_price': '67123.45',
      'change_24h_pct': 1.24,
      'signals': {
        '1h': {'label': 'up', 'p_up': 0.582, 'target_open_time': '2026-10-03T14:00:00Z', 'model_status': 'ok', 'stale': false},
        '4h': {'label': 'neutral', 'p_up': 0.51, 'target_open_time': '2026-10-03T16:00:00Z', 'model_status': 'degraded', 'stale': false},
        '1d': null,
      },
    };

Json candleJson(int hour, String close) => {
      't': '2026-10-03T${hour.toString().padLeft(2, '0')}:00:00Z',
      'o': '67000.00',
      'h': '67300.00',
      'l': '66900.00',
      'c': close,
      'v': '412.3',
      'ema9': 67050.5,
      'ema21': 67010.0,
      'ema50': null,
    };

/// Stands in for the server. The real [TmApi] methods are replaced, so no test ever opens
/// a network connection.
class FakeApi extends TmApi {
  FakeApi() : super(Dio(), accessToken: () => 'test-token');

  final rules = <AlertRule>[];
  var created = 0;

  @override
  Future<List<MarketRow>> markets() async =>
      [MarketRow.fromJson(marketJson('BTC', 'Bitcoin')), MarketRow.fromJson(marketJson('ETH', 'Ethereum'))];

  @override
  Future<Prediction> latestPrediction(String symbol, String tf) async => Prediction.fromJson(predictionJson());

  @override
  Future<CandlesData> candles(String symbol, String tf, {int limit = 200}) async => CandlesData.fromJson({
        'symbol': symbol,
        'timeframe': tf,
        'candles': [for (var h = 1; h <= 13; h++) candleJson(h, h.isEven ? '67200.00' : '66950.00')],
        'stale': false,
      });

  @override
  Future<List<HistoryItem>> history(String symbol, String tf, {int limit = 12}) async => [
        HistoryItem.fromJson({
          'label': 'up',
          'p_up': 0.58,
          'base_open_time': '2026-10-03T11:00:00Z',
          'target_open_time': '2026-10-03T12:00:00Z',
          'base_close': '67000',
          'model_status': 'ok',
          'outcome': {'target_close': '67100', 'actual_direction': 'up', 'correct': true, 'return_pct': 0.15},
        }),
        HistoryItem.fromJson({
          'label': 'neutral',
          'p_up': 0.5,
          'base_open_time': '2026-10-03T10:00:00Z',
          'target_open_time': '2026-10-03T11:00:00Z',
          'base_close': '67000',
          'model_status': 'ok',
          'outcome': {'target_close': '66900', 'actual_direction': 'down', 'correct': null, 'return_pct': -0.15},
        }),
      ];

  @override
  Future<PerformanceSummary> performanceSummary(int days) async {
    Json row(String? symbol, String? tf) => {
          'symbol': symbol,
          'timeframe': tf,
          'days': days,
          'n_predictions': 3666,
          'n_resolved': 3600,
          'coverage': 0.2,
          'accuracy': 0.499,
          'baseline': {'naive': 0.505, 'always_up': 0.5},
          'brier': 0.25,
          'brier_baseline': 0.25,
          'by_label': <String, dynamic>{},
          'low_sample': false,
        };
    return PerformanceSummary.fromJson({
      'days': days,
      'overall': row(null, null),
      'rows': [row('BTC', '1h'), row('ETH', '1h')],
    });
  }

  @override
  Future<List<NewsItem>> news(String symbol, {int limit = 8}) async => [
        NewsItem.fromJson({
          'id': 1,
          'source': 'coindesk',
          'source_name': 'CoinDesk',
          'title': 'A made-up headline for the test',
          'url': 'https://news.example.test/1',
          'published_at': '2026-10-03T12:00:00Z',
          'symbols': ['BTC'],
          'sentiment': {'label': 'bullish', 'score': 0.31, 'confidence': 0.7, 'event_type': 'etf', 'reason': 'x'},
        }),
      ];

  @override
  Future<List<String>> watchlist() async => ['BTC'];

  @override
  Future<AlertsData> alerts() async => AlertsData(items: List.of(rules), maxAlerts: 20);

  @override
  Future<AlertRule> createAlert({
    required String symbol,
    required String type,
    String? timeframe,
    String? threshold,
    int cooldownMinutes = 60,
  }) async {
    created += 1;
    final rule = AlertRule(
      id: 'rule-$created',
      symbol: symbol,
      type: type,
      timeframe: timeframe,
      threshold: threshold,
      cooldownMinutes: cooldownMinutes,
      active: true,
    );
    rules.add(rule);
    return rule;
  }

  @override
  Future<NotificationsData> notifications({int limit = 30}) async => NotificationsData(
        items: [
          AppNotification(
            id: 7,
            title: 'BTC 1h signal changed to Up',
            body: 'It was Neutral before. Not financial advice. Estimates only.',
            createdAt: DateTime.utc(2026, 10, 3, 13),
          ),
        ],
        unread: 1,
      );
}

/// The live stream without a socket: it just reports "live".
class FakeLive extends LiveController {
  @override
  LiveState build(CoinKey arg) => const LiveState(status: LiveStatus.live);
}
