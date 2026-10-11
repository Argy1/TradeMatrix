/// Display formatting only. The app never computes a price, indicator or probability
/// (CLAUDE.md rule 5): it shows what the API sends, in a readable form.
library;

const _months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/// Data is UTC everywhere; the app shows WIB (UTC+7, no daylight saving).
const displayZone = 'WIB';

DateTime toWib(DateTime time) => time.toUtc().add(const Duration(hours: 7));

const _unitWords = {'m': 'minute', 'h': 'hour', 'd': 'day'};

/// "15 minute" / "1 hour" / "1 day", as used in "the next 1 hour candle".
String timeframeWords(String tf) {
  final unit = tf.isEmpty ? null : _unitWords[tf[tf.length - 1]];
  return unit == null ? tf : '${tf.substring(0, tf.length - 1)} $unit';
}

/// Prices arrive as exact strings. Add thousands separators without going through a
/// floating-point number, drop trailing zeros and keep at least two decimals.
String formatPrice(String value, {bool dollar = true}) {
  final parts = value.split('.');
  final whole = parts[0].replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (_) => ',');
  final fraction = (parts.length > 1 ? parts[1] : '').replaceFirst(RegExp(r'0+$'), '').padRight(2, '0');
  return '${dollar ? r'$' : ''}$whole.$fraction';
}

/// 0.582 -> "58.2%" (one decimal, docs/01).
String formatProbability(double p) => '${(p * 100).toStringAsFixed(1)}%';

String formatChange(double? pct) {
  if (pct == null) return 'n/a';
  return '${pct > 0 ? '+' : ''}${pct.toStringAsFixed(2)}%';
}

String _two(int n) => n.toString().padLeft(2, '0');

/// "22:00 WIB"
String formatClock(DateTime time) {
  final wib = toWib(time);
  return '${_two(wib.hour)}:${_two(wib.minute)} $displayZone';
}

/// "3 Oct, 22:00 WIB"
String formatDateTime(DateTime time) {
  final wib = toWib(time);
  return '${wib.day} ${_months[wib.month - 1]}, ${formatClock(time)}';
}

/// "in 41 min" / "in 2 h 5 min" / "now". With [seconds] (the fast candle sizes) the last
/// ten minutes are exact: "in 3 min 20 s", and under two minutes "in 42 s".
String formatCountdown(DateTime target, DateTime now, {bool seconds = false}) {
  final left = target.difference(now).inSeconds;
  if (seconds && left > 0 && left < 600) {
    if (left < 120) return 'in $left s';
    final rest = left % 60;
    return rest > 0 ? 'in ${left ~/ 60} min $rest s' : 'in ${left ~/ 60} min';
  }
  final minutes = (left / 60).round();
  if (minutes <= 0) return 'now';
  if (minutes < 60) return 'in $minutes min';
  final hours = minutes ~/ 60, rest = minutes % 60;
  return rest > 0 ? 'in $hours h $rest min' : 'in $hours h';
}

/// "just now" / "12 min ago" / "3 h ago" / "2 d ago"
String formatAgo(DateTime time, DateTime now) {
  final minutes = now.difference(time).inMinutes;
  if (minutes < 1) return 'just now';
  if (minutes < 60) return '$minutes min ago';
  final hours = minutes ~/ 60;
  if (hours < 24) return '$hours h ago';
  return '${hours ~/ 24} d ago';
}

/// A sentiment score always shows its sign: 0.31 -> "+0.31", -0.2 -> "-0.20".
String formatScore(double score) {
  final rounded = double.parse(score.toStringAsFixed(2)); // -0.004 becomes 0: never "-0.00"
  return '${rounded >= 0 ? '+' : '-'}${rounded.abs().toStringAsFixed(2)}';
}
