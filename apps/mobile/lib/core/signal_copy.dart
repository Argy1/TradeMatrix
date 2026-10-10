/// The words around a signal (docs/08 and docs/06). Same sentences as the web app, so a
/// person reads the same thing on both.
library;

import 'format.dart';

enum Direction { up, down, neutral }

/// The API decides the label; anything that is not "up" or "down" is shown as Neutral.
Direction directionOf(String label) => switch (label) {
      'up' => Direction.up,
      'down' => Direction.down,
      _ => Direction.neutral,
    };

// Display only: the neutral zone drawn on the meter. The backend applies the real rule.
const neutralLow = 0.45;
const neutralHigh = 0.55;

/// The number on the orb: P(up) for Up and Neutral, P(down) for Down (docs/08).
double shownProbability(Direction direction, double pUp) => direction == Direction.down ? 1 - pUp : pUp;

const orbWord = {Direction.up: 'UP', Direction.down: 'DOWN', Direction.neutral: 'NEUTRAL'};
const directionWord = {Direction.up: 'Up', Direction.down: 'Down', Direction.neutral: 'Neutral'};
const headline = {
  Direction.up: 'Buyers have the edge',
  Direction.down: 'Sellers have the edge',
  Direction.neutral: 'Too close to call',
};

/// The one plain-language sentence under the headline (docs/08 item 4).
String plainSentence(Direction direction, double pUp, String tf, String baseClose) {
  final up = formatProbability(pUp), down = formatProbability(1 - pUp);
  final price = formatPrice(baseClose);
  final candle = 'the next ${timeframeWords(tf)} candle';
  return switch (direction) {
    Direction.up => '$up chance $candle closes higher than $price. That leaves $down that it does not.',
    Direction.down => '$down chance $candle closes lower than $price. That leaves $up that it does not.',
    Direction.neutral =>
      'Up $up versus down $down. When the odds are this close we make no call and show Neutral.',
  };
}

/// One sentence a screen reader can read for the whole signal (docs/08 accessibility).
String screenReaderSummary(String coin, String tf, String label, double pUp) {
  final direction = directionOf(label);
  final percent = (shownProbability(direction, pUp) * 100).toStringAsFixed(1);
  return '$coin, next ${timeframeWords(tf)} candle: ${directionWord[direction]!.toLowerCase()}, '
      '$percent percent chance. Neutral zone is 45 to 55 percent.';
}

/// The "How reliable is it?" sentence. Honest whatever the result (docs/06).
String reliabilitySentence(double? model, double? naive, int n, bool lowSample) {
  if (n == 0 || naive == null) {
    return 'Not enough finished signals yet to measure reliability. Check back after more candles close.';
  }
  if (model == null) {
    // Signals finished, but none of them was an Up or Down call.
    return 'All $n recent signals were Neutral (too close to call), so there are no Up or Down calls '
        'to score yet. Staying Neutral is the honest answer when the odds are close.';
  }
  final points = (model - naive) * 100;
  final sample = lowSample ? ' Only $n finished signals so far, so this can still change a lot.' : '';
  if (points > 0) {
    return 'The model beat the baseline by ${points.toStringAsFixed(1)} points. '
        'That is a small edge, which is normal for crypto.$sample';
  }
  return 'The model did not beat the simple baseline (${points.abs().toStringAsFixed(1)} points behind). '
      'Treat its signals with caution.$sample';
}

const degradedWarning =
    'This model is performing below the baseline right now. Treat the signal with extra caution.';
const staleWarning = 'Data is delayed. Signals may be out of date.';

/// Fixed text from docs/06. It may only change with Argy's approval.
const disclaimer =
    'Signals are probabilistic estimates for information and education only, not financial advice. '
    'Crypto is volatile and you can lose all the money you invest. Past performance does not '
    'guarantee future results. TradeMatrix AI does not execute trades.';
const disclaimerShort = 'Not financial advice. Estimates only.';

/// One plain sentence per reason code, so jargon is explained the first time (docs/08).
const reasonExplainers = {
  'rsi': 'RSI measures recent momentum on a 0 to 100 scale; above 70 or below 30 is stretched.',
  'ema_trend': 'EMA 50 is the average price of the last 50 candles, a simple view of the trend.',
  'ema_cross': 'When the fast average (EMA 9) crosses the slower one (EMA 21), momentum is turning.',
  'macd': 'MACD compares a fast and a slow trend; a positive histogram means momentum is rising.',
  'volume': 'Unusual volume means more traders than normal are active right now.',
  'bollinger': 'Bollinger Bands mark the usual price range; outside them, moves are stretched.',
  'momentum': 'How far the price moved over the last 24 candles.',
  'sentiment': 'The average tone of recent news headlines about this coin.',
};

const effectTag = {'up': 'Pushes up', 'down': 'Pushes down', 'none': 'No clear push'};

// News section. Which sentence is shown comes from the API (`sentiment_used`), so the app
// never claims news is part of the signal while it is only being recorded.
const newsScale = 'Each badge is an automated reading of the headline, from -1 (bearish) to +1 (bullish).';
const newsContextOnly = "For now news is context only: it does not change the signal's probability.";
const newsBlended = 'News tone is one of the inputs of the signal, with a small weight.';
const newsFootnote =
    'Headlines open on the publisher\'s site. The tone rating is made by an AI model and can be wrong.';

// ---- Alerts (display only; the API decides what is valid and what fires) ----

const alertTypeLabels = {
  'signal_change': 'The signal changes (Up, Down or Neutral)',
  'prob_above': 'The chance of Up is at or above a level',
  'prob_below': 'The chance of Up is at or below a level',
  'price_above': 'The price crosses above a level',
  'price_below': 'The price crosses below a level',
};

bool isSignalAlert(String type) => const {'signal_change', 'prob_above', 'prob_below'}.contains(type);

/// 60 -> "1 hour", 240 -> "4 hours", 1440 -> "1 day", 15 -> "15 minutes"
String cooldownWords(int minutes) {
  String plural(int n, String word) => '$n $word${n == 1 ? '' : 's'}';
  if (minutes % 1440 == 0) return plural(minutes ~/ 1440, 'day');
  if (minutes % 60 == 0) return plural(minutes ~/ 60, 'hour');
  return plural(minutes, 'minute');
}

String _percent(String? threshold) {
  final value = ((double.tryParse(threshold ?? '') ?? 0) * 1000).round() / 10;
  return '${value == value.roundToDouble() ? value.toInt() : value}%';
}

/// One plain sentence for a rule, e.g. "When the BTC 1h signal changes".
String ruleSentence({required String symbol, required String type, String? timeframe, String? threshold}) {
  return switch (type) {
    'signal_change' => 'When the $symbol $timeframe signal changes',
    'prob_above' => 'When the $symbol $timeframe chance of Up is ${_percent(threshold)} or more',
    'prob_below' => 'When the $symbol $timeframe chance of Up is ${_percent(threshold)} or less',
    'price_above' => 'When the $symbol price crosses above ${formatPrice(threshold ?? '0')}',
    'price_below' => 'When the $symbol price crosses below ${formatPrice(threshold ?? '0')}',
    _ => '$symbol alert',
  };
}

/// Turn what was typed into the threshold the API expects, or say what is wrong.
({String? threshold, String? error}) parseThreshold(String type, String typed) {
  if (type == 'signal_change') return (threshold: null, error: null);
  final text = typed.trim().replaceAll(',', '');
  if (!RegExp(r'^\d+(\.\d+)?$').hasMatch(text)) return (threshold: null, error: 'Enter a number.');
  final value = double.parse(text);
  if (isSignalAlert(type)) {
    if (value <= 0 || value >= 100) {
      return (threshold: null, error: 'Enter a percentage between 1 and 99.');
    }
    return (threshold: (value / 100).toStringAsFixed(4), error: null); // 60 (%) -> "0.6000"
  }
  if (value <= 0) return (threshold: null, error: 'Enter a price above 0.');
  return (threshold: text, error: null); // prices stay exact strings
}
