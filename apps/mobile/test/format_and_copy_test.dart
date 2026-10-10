import 'package:flutter_test/flutter_test.dart';
import 'package:tradematrix/core/format.dart';
import 'package:tradematrix/core/signal_copy.dart';

void main() {
  group('formatting', () {
    test('prices keep every digit that matters and get thousands separators', () {
      expect(formatPrice('67123.45'), r'$67,123.45');
      expect(formatPrice('84536.00000000'), r'$84,536.00'); // exchange padding is dropped
      expect(formatPrice('0.21400000'), r'$0.214');
      expect(formatPrice('0.00001234'), r'$0.00001234'); // small coins are not rounded away
      expect(formatPrice('1234567'), r'$1,234,567.00');
      expect(formatPrice('82819.84', dollar: false), '82,819.84');
    });

    test('probability, change and score', () {
      expect(formatProbability(0.582), '58.2%');
      expect(formatChange(1.236), '+1.24%');
      expect(formatChange(-0.27), '-0.27%');
      expect(formatChange(null), 'n/a');
      expect(formatScore(0.31), '+0.31');
      expect(formatScore(-0.2), '-0.20');
      expect(formatScore(-0.004), '+0.00'); // rounds to zero: never "-0.00"
    });

    test('times are shown in WIB (UTC+7)', () {
      final t = DateTime.utc(2026, 10, 3, 15, 0);
      expect(formatClock(t), '22:00 WIB');
      expect(formatDateTime(t), '3 Oct, 22:00 WIB');
      expect(formatDateTime(DateTime.utc(2026, 10, 3, 20, 30)), '4 Oct, 03:30 WIB'); // next day in WIB
    });

    test('countdown and "ago"', () {
      final now = DateTime.utc(2026, 10, 3, 14, 19);
      expect(formatCountdown(DateTime.utc(2026, 10, 3, 15), now), 'in 41 min');
      expect(formatCountdown(DateTime.utc(2026, 10, 3, 16, 24), now), 'in 2 h 5 min');
      expect(formatCountdown(DateTime.utc(2026, 10, 3, 16, 19), now), 'in 2 h');
      expect(formatCountdown(DateTime.utc(2026, 10, 3, 14), now), 'now');
      expect(formatAgo(DateTime.utc(2026, 10, 3, 14, 7), now), '12 min ago');
      expect(formatAgo(DateTime.utc(2026, 10, 3, 11, 19), now), '3 h ago');
      expect(formatAgo(DateTime.utc(2026, 10, 1, 13), now), '2 d ago');
      expect(formatAgo(DateTime.utc(2026, 10, 3, 14, 22), now), 'just now'); // a clock running ahead
    });
  });

  group('signal wording (docs/08)', () {
    test('the orb shows the Down chance for a Down signal', () {
      expect(shownProbability(Direction.down, 0.3), closeTo(0.7, 1e-9));
      expect(shownProbability(Direction.up, 0.582), 0.582);
      expect(shownProbability(Direction.neutral, 0.508), 0.508);
      expect(directionOf('up'), Direction.up);
      expect(directionOf('anything else'), Direction.neutral);
    });

    test('the plain sentence matches the design example', () {
      expect(
        plainSentence(Direction.up, 0.582, '1h', '67123.45'),
        r'58.2% chance the next 1 hour candle closes higher than $67,123.45. That leaves 41.8% that it does not.',
      );
      expect(
        plainSentence(Direction.down, 0.38, '4h', '100'),
        r'62.0% chance the next 4 hour candle closes lower than $100.00. That leaves 38.0% that it does not.',
      );
      expect(
        plainSentence(Direction.neutral, 0.508, '1h', '1'),
        'Up 50.8% versus down 49.2%. When the odds are this close we make no call and show Neutral.',
      );
    });

    test('a screen reader hears the whole signal as one sentence', () {
      expect(
        screenReaderSummary('Bitcoin', '1h', 'up', 0.582),
        'Bitcoin, next 1 hour candle: up, 58.2 percent chance. Neutral zone is 45 to 55 percent.',
      );
    });

    test('reliability is honest whatever the result', () {
      expect(
        reliabilitySentence(0.541, 0.512, 200, false),
        'The model beat the baseline by 2.9 points. That is a small edge, which is normal for crypto.',
      );
      expect(reliabilitySentence(0.48, 0.5, 300, false), contains('did not beat'));
      expect(reliabilitySentence(null, null, 0, true), contains('Not enough finished signals'));
      expect(reliabilitySentence(0.6, 0.5, 12, true), contains('Only 12 finished signals'));
      // Signals finished, but every one was Neutral: say that, not "not enough signals".
      expect(reliabilitySentence(null, 0.514, 181, false), startsWith('All 181 recent signals were Neutral'));
    });

    test('the disclaimer is the fixed text from docs/06', () {
      expect(disclaimer, startsWith('Signals are probabilistic estimates for information and education only'));
      expect(disclaimer, endsWith('TradeMatrix AI does not execute trades.'));
      expect(disclaimerShort, 'Not financial advice. Estimates only.');
    });
  });

  group('alert wording', () {
    test('each kind of rule is one plain sentence', () {
      expect(ruleSentence(symbol: 'BTC', type: 'signal_change', timeframe: '1h'), 'When the BTC 1h signal changes');
      expect(
        ruleSentence(symbol: 'BTC', type: 'prob_above', timeframe: '1h', threshold: '0.6'),
        'When the BTC 1h chance of Up is 60% or more',
      );
      expect(
        ruleSentence(symbol: 'BTC', type: 'prob_below', timeframe: '4h', threshold: '0.425'),
        'When the BTC 4h chance of Up is 42.5% or less',
      );
      expect(
        ruleSentence(symbol: 'BTC', type: 'price_above', threshold: '85000.5'),
        r'When the BTC price crosses above $85,000.50',
      );
      expect(
        ruleSentence(symbol: 'XLM', type: 'price_below', threshold: '0.2'),
        r'When the XLM price crosses below $0.20',
      );
    });

    test('cooldown in everyday units', () {
      expect(cooldownWords(15), '15 minutes');
      expect(cooldownWords(60), '1 hour');
      expect(cooldownWords(240), '4 hours');
      expect(cooldownWords(1440), '1 day');
    });

    test('typed thresholds become what the API expects, or an explanation', () {
      expect(parseThreshold('prob_above', '60').threshold, '0.6000');
      expect(parseThreshold('prob_below', ' 42.5 ').threshold, '0.4250');
      expect(parseThreshold('price_above', '85,000.50').threshold, '85000.50'); // exact text
      expect(parseThreshold('signal_change', 'anything').threshold, isNull);
      expect(parseThreshold('signal_change', 'anything').error, isNull);
      expect(parseThreshold('prob_above', '100').error, 'Enter a percentage between 1 and 99.');
      expect(parseThreshold('price_above', 'abc').error, 'Enter a number.');
      expect(parseThreshold('price_above', '0').error, 'Enter a price above 0.');
    });
  });
}
