/// Immutable copies of the API's JSON (the contract is the FastAPI OpenAPI schema, docs/04).
/// Written by hand so every field is easy to read; prices stay strings, exactly as sent.
library;

typedef Json = Map<String, dynamic>;

DateTime _time(Object? value) => DateTime.parse(value as String).toUtc();
DateTime? _timeOrNull(Object? value) => value == null ? null : _time(value);
double? _double(Object? value) => (value as num?)?.toDouble();

class Candle {
  const Candle({
    required this.t,
    required this.o,
    required this.h,
    required this.l,
    required this.c,
    required this.v,
    this.ema9,
    this.ema21,
    this.ema50,
  });

  final DateTime t;
  final String o, h, l, c, v; // exact strings from the exchange
  final double? ema9, ema21, ema50; // computed on the server; empty for the candle still forming

  factory Candle.fromJson(Json j) => Candle(
        t: _time(j['t']),
        o: j['o'] as String,
        h: j['h'] as String,
        l: j['l'] as String,
        c: j['c'] as String,
        v: j['v'] as String,
        ema9: _double(j['ema9']),
        ema21: _double(j['ema21']),
        ema50: _double(j['ema50']),
      );

  // Only for drawing positions on the chart; shown numbers always use the strings.
  double get open => double.parse(o);
  double get high => double.parse(h);
  double get low => double.parse(l);
  double get close => double.parse(c);
  double get volume => double.parse(v);
  bool get rising => close >= open;
}

class CandlesData {
  const CandlesData({required this.candles, required this.stale});
  final List<Candle> candles;
  final bool stale;

  factory CandlesData.fromJson(Json j) => CandlesData(
        candles: [for (final c in j['candles'] as List) Candle.fromJson(c as Json)],
        stale: j['stale'] as bool? ?? false,
      );

  CandlesData withCandles(List<Candle> next) => CandlesData(candles: next, stale: stale);
}

class Reason {
  const Reason({required this.code, required this.text, required this.effect});
  final String code, text, effect; // effect: up / down / none

  factory Reason.fromJson(Json j) =>
      Reason(code: j['code'] as String, text: j['text'] as String, effect: j['effect'] as String);
}

class RecentAccuracy {
  const RecentAccuracy({this.model, this.naiveBaseline, required this.n, required this.lowSample});
  final double? model, naiveBaseline;
  final int n;
  final bool lowSample;

  factory RecentAccuracy.fromJson(Json j) => RecentAccuracy(
        model: _double(j['model']),
        naiveBaseline: _double(j['naive_baseline']),
        n: j['n'] as int,
        lowSample: j['low_sample'] as bool,
      );
}

class Prediction {
  const Prediction({
    required this.symbol,
    required this.timeframe,
    required this.label,
    required this.pUp,
    required this.targetOpenTime,
    required this.targetCloseTime,
    required this.baseClose,
    required this.reasons,
    required this.sentimentAgg,
    required this.sentimentUsed,
    required this.modelStatus,
    required this.recentAccuracy,
    required this.disclaimer,
    required this.stale,
  });

  final String symbol, timeframe, label, baseClose, modelStatus, disclaimer;
  final double pUp, sentimentAgg;
  final DateTime targetOpenTime, targetCloseTime;
  final List<Reason> reasons;
  final bool sentimentUsed, stale;
  final RecentAccuracy recentAccuracy;

  bool get degraded => modelStatus == 'degraded';

  factory Prediction.fromJson(Json j) => Prediction(
        symbol: j['symbol'] as String,
        timeframe: j['timeframe'] as String,
        label: j['label'] as String,
        pUp: (j['p_up'] as num).toDouble(),
        targetOpenTime: _time(j['target_open_time']),
        targetCloseTime: _time(j['target_close_time']),
        baseClose: j['base_close'] as String,
        reasons: [for (final r in j['reasons'] as List) Reason.fromJson(r as Json)],
        sentimentAgg: (j['sentiment_agg'] as num?)?.toDouble() ?? 0,
        sentimentUsed: j['sentiment_used'] as bool? ?? false,
        modelStatus: (j['model'] as Json)['status'] as String,
        recentAccuracy: RecentAccuracy.fromJson(j['recent_accuracy'] as Json),
        disclaimer: j['disclaimer'] as String,
        stale: j['stale'] as bool? ?? false,
      );
}

class HistoryItem {
  const HistoryItem({
    required this.label,
    required this.targetOpenTime,
    this.actualDirection,
    this.correct,
    required this.resolved,
  });

  final String label;
  final DateTime targetOpenTime;
  final String? actualDirection;
  final bool? correct; // null when the call was Neutral (a "Skip")
  final bool resolved;

  factory HistoryItem.fromJson(Json j) {
    final outcome = j['outcome'] as Json?;
    return HistoryItem(
      label: j['label'] as String,
      targetOpenTime: _time(j['target_open_time']),
      actualDirection: outcome?['actual_direction'] as String?,
      correct: outcome?['correct'] as bool?,
      resolved: outcome != null,
    );
  }
}

class SignalChip {
  const SignalChip({required this.label, required this.pUp, required this.modelStatus, required this.stale});
  final String label, modelStatus;
  final double pUp;
  final bool stale;

  factory SignalChip.fromJson(Json j) => SignalChip(
        label: j['label'] as String,
        pUp: (j['p_up'] as num).toDouble(),
        modelStatus: j['model_status'] as String,
        stale: j['stale'] as bool? ?? false,
      );
}

class MarketRow {
  const MarketRow({
    required this.symbol,
    required this.name,
    this.lastPrice,
    this.change24hPct,
    required this.signals,
  });

  final String symbol, name;
  final String? lastPrice;
  final double? change24hPct;
  final Map<String, SignalChip?> signals; // keyed by 1h / 4h / 1d

  factory MarketRow.fromJson(Json j) => MarketRow(
        symbol: j['symbol'] as String,
        name: j['name'] as String,
        lastPrice: j['last_price'] as String?,
        change24hPct: _double(j['change_24h_pct']),
        signals: {
          for (final entry in (j['signals'] as Json).entries)
            entry.key: entry.value == null ? null : SignalChip.fromJson(entry.value as Json),
        },
      );
}

class Performance {
  const Performance({
    this.symbol,
    this.timeframe,
    required this.nPredictions,
    required this.nResolved,
    this.accuracy,
    this.naive,
    this.coverage,
    required this.lowSample,
  });

  final String? symbol, timeframe;
  final int nPredictions, nResolved;
  final double? accuracy, naive, coverage;
  final bool lowSample;

  factory Performance.fromJson(Json j) => Performance(
        symbol: j['symbol'] as String?,
        timeframe: j['timeframe'] as String?,
        nPredictions: j['n_predictions'] as int,
        nResolved: j['n_resolved'] as int,
        accuracy: _double(j['accuracy']),
        naive: _double((j['baseline'] as Json)['naive']),
        coverage: _double(j['coverage']),
        lowSample: j['low_sample'] as bool,
      );
}

class PerformanceSummary {
  const PerformanceSummary({required this.days, required this.overall, required this.rows});
  final int days;
  final Performance overall;
  final List<Performance> rows;

  factory PerformanceSummary.fromJson(Json j) => PerformanceSummary(
        days: j['days'] as int,
        overall: Performance.fromJson(j['overall'] as Json),
        rows: [for (final r in j['rows'] as List) Performance.fromJson(r as Json)],
      );
}

class NewsSentiment {
  const NewsSentiment({required this.label, required this.score});
  final String label; // bullish / bearish / neutral, decided by the server
  final double score;
}

class NewsItem {
  const NewsItem({
    required this.id,
    required this.sourceName,
    required this.title,
    required this.url,
    required this.publishedAt,
    this.sentiment,
  });

  final int id;
  final String sourceName, title, url;
  final DateTime publishedAt;
  final NewsSentiment? sentiment; // null = not rated yet

  factory NewsItem.fromJson(Json j) {
    final s = j['sentiment'] as Json?;
    return NewsItem(
      id: j['id'] as int,
      sourceName: j['source_name'] as String,
      title: j['title'] as String,
      url: j['url'] as String,
      publishedAt: _time(j['published_at']),
      sentiment:
          s == null ? null : NewsSentiment(label: s['label'] as String, score: (s['score'] as num).toDouble()),
    );
  }
}

class AlertRule {
  const AlertRule({
    required this.id,
    required this.symbol,
    required this.type,
    this.timeframe,
    this.threshold,
    required this.cooldownMinutes,
    required this.active,
    this.lastTriggeredAt,
  });

  final String id, symbol, type;
  final String? timeframe, threshold;
  final int cooldownMinutes;
  final bool active;
  final DateTime? lastTriggeredAt;

  factory AlertRule.fromJson(Json j) => AlertRule(
        id: j['id'] as String,
        symbol: j['symbol'] as String,
        type: j['type'] as String,
        timeframe: j['timeframe'] as String?,
        threshold: j['threshold'] as String?,
        cooldownMinutes: j['cooldown_minutes'] as int,
        active: j['active'] as bool,
        lastTriggeredAt: _timeOrNull(j['last_triggered_at']),
      );
}

class AlertsData {
  const AlertsData({required this.items, required this.maxAlerts});
  final List<AlertRule> items;
  final int maxAlerts;

  factory AlertsData.fromJson(Json j) => AlertsData(
        items: [for (final a in j['items'] as List) AlertRule.fromJson(a as Json)],
        maxAlerts: j['max_alerts'] as int? ?? 20,
      );
}

class AppNotification {
  const AppNotification({
    required this.id,
    required this.title,
    required this.body,
    required this.createdAt,
    this.readAt,
  });

  final int id;
  final String title, body;
  final DateTime createdAt;
  final DateTime? readAt;

  factory AppNotification.fromJson(Json j) => AppNotification(
        id: j['id'] as int,
        title: j['title'] as String,
        body: j['body'] as String,
        createdAt: _time(j['created_at']),
        readAt: _timeOrNull(j['read_at']),
      );
}

class NotificationsData {
  const NotificationsData({required this.items, required this.unread});
  final List<AppNotification> items;
  final int unread;

  factory NotificationsData.fromJson(Json j) => NotificationsData(
        items: [for (final n in j['items'] as List) AppNotification.fromJson(n as Json)],
        unread: j['unread'] as int,
      );
}
