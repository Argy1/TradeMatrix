import 'package:dio/dio.dart';

import 'models.dart';

/// An error the screens can show: the API's own `{"error": {"code", "message"}}` (docs/04),
/// or a plain message when the phone could not reach the server at all.
class ApiException implements Exception {
  const ApiException(this.status, this.code, this.message);
  final int? status; // null = no answer (offline, timeout)
  final String code, message;

  bool get notFound => status == 404;

  @override
  String toString() => 'ApiException($status, $code, $message)';
}

/// The only place that talks to the TradeMatrix API. Every method returns ready-to-draw
/// data; the app never computes indicators or probabilities itself.
class TmApi {
  TmApi(this._dio, {required String? Function() accessToken}) : _accessToken = accessToken;

  final Dio _dio;
  final String? Function() _accessToken;

  static Dio createDio(String baseUrl) => Dio(BaseOptions(
        baseUrl: baseUrl,
        // A request stuck on a bad connection fails after 15 s instead of loading forever.
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
      ));

  Future<T> _call<T>(Future<Response<dynamic>> Function() request, T Function(dynamic data) parse) async {
    try {
      return parse((await request()).data);
    } on DioException catch (e) {
      final body = e.response?.data;
      final error = body is Map ? body['error'] : null;
      if (error is Map) {
        throw ApiException(e.response?.statusCode, '${error['code']}', '${error['message']}');
      }
      throw ApiException(
        e.response?.statusCode,
        'network',
        e.response == null ? 'No connection to the server.' : 'Request failed (${e.response?.statusCode}).',
      );
    }
  }

  /// The signed-in user's token. The API checks it and only ever returns that user's data.
  Options _auth() {
    final token = _accessToken();
    if (token == null) throw const ApiException(401, 'unauthorized', 'Please sign in first.');
    return Options(headers: {'Authorization': 'Bearer $token'});
  }

  // ---- public ----

  Future<List<MarketRow>> markets() => _call(
        () => _dio.get('/v1/markets'),
        (data) => [for (final row in data as List) MarketRow.fromJson(row as Json)],
      );

  Future<Prediction> latestPrediction(String symbol, String tf) => _call(
        () => _dio.get('/v1/predictions/latest', queryParameters: {'symbol': symbol, 'tf': tf}),
        (data) => Prediction.fromJson(data as Json),
      );

  Future<CandlesData> candles(String symbol, String tf, {int limit = 200}) => _call(
        () => _dio.get('/v1/candles', queryParameters: {'symbol': symbol, 'tf': tf, 'limit': limit}),
        (data) => CandlesData.fromJson(data as Json),
      );

  Future<List<HistoryItem>> history(String symbol, String tf, {int limit = 12}) => _call(
        () => _dio.get('/v1/predictions/history', queryParameters: {'symbol': symbol, 'tf': tf, 'limit': limit}),
        (data) => [for (final item in (data as Json)['items'] as List) HistoryItem.fromJson(item as Json)],
      );

  Future<PerformanceSummary> performanceSummary(int days) => _call(
        () => _dio.get('/v1/performance/summary', queryParameters: {'days': days}),
        (data) => PerformanceSummary.fromJson(data as Json),
      );

  Future<List<NewsItem>> news(String symbol, {int limit = 8}) => _call(
        () => _dio.get('/v1/news', queryParameters: {'symbol': symbol, 'limit': limit}),
        (data) => [for (final item in (data as Json)['items'] as List) NewsItem.fromJson(item as Json)],
      );

  // ---- signed-in ----

  List<String> _symbols(dynamic data) => [for (final s in (data as Json)['symbols'] as List) s as String];

  Future<List<String>> watchlist() => _call(() => _dio.get('/v1/watchlist', options: _auth()), _symbols);

  Future<List<String>> setWatched(String symbol, {required bool watched}) => _call(
        () => watched
            ? _dio.put('/v1/watchlist/$symbol', options: _auth())
            : _dio.delete('/v1/watchlist/$symbol', options: _auth()),
        _symbols,
      );

  Future<AlertsData> alerts() =>
      _call(() => _dio.get('/v1/alerts', options: _auth()), (data) => AlertsData.fromJson(data as Json));

  Future<AlertRule> createAlert({
    required String symbol,
    required String type,
    String? timeframe,
    String? threshold,
    int cooldownMinutes = 60,
  }) =>
      _call(
        () => _dio.post('/v1/alerts', options: _auth(), data: {
          'symbol': symbol,
          'type': type,
          'timeframe': timeframe,
          'threshold': threshold,
          'cooldown_minutes': cooldownMinutes,
        }),
        (data) => AlertRule.fromJson(data as Json),
      );

  Future<AlertRule> setAlertActive(String id, {required bool active}) => _call(
        () => _dio.patch('/v1/alerts/$id', options: _auth(), data: {'active': active}),
        (data) => AlertRule.fromJson(data as Json),
      );

  /// The API answers with the remaining rules.
  Future<AlertsData> deleteAlert(String id) => _call(
        () => _dio.delete('/v1/alerts/$id', options: _auth()),
        (data) => AlertsData.fromJson(data as Json),
      );

  Future<NotificationsData> notifications({int limit = 30}) => _call(
        () => _dio.get('/v1/notifications', options: _auth(), queryParameters: {'limit': limit}),
        (data) => NotificationsData.fromJson(data as Json),
      );

  Future<void> markNotificationRead(int id) =>
      _call(() => _dio.post('/v1/notifications/$id/read', options: _auth()), (_) {});
}
