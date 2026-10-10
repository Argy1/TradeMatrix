import 'package:flutter/material.dart';

import '../../core/signal_copy.dart';
import '../../theme/tokens.dart';
import '../../widgets/brand.dart';
import '../../widgets/glass.dart';
import '../../widgets/page.dart';
import '../../widgets/states.dart';

// The same explanations as the web app's "How it works" page.
const _sections = [
  (
    'What a signal is',
    'For each coin and candle size (1 hour, 4 hours, 1 day) we estimate the chance that the next candle '
        'closes higher than the last one. Above 55% we say Up, below 45% Down, and in between Neutral: '
        'too close to call.',
  ),
  (
    'How it is made',
    'When a candle closes, we compute indicators such as RSI, moving averages, MACD, Bollinger Bands and '
        'volume from closed candles only. A machine-learning model (XGBoost) turns them into a probability, '
        'calibrated so that 60% means Up about 60% of the time. The three reasons you see come from fixed '
        'templates, never from free AI text.',
  ),
  (
    'The baseline',
    'A model is only useful if it beats simple rules. Our baseline is "repeat the last move": if the last '
        'candle went up, say up. We show the model\'s live accuracy next to that baseline on every signal '
        'and on the track-record page.',
  ),
  (
    'What we found when testing',
    'In walk-forward tests on data the models had never seen, most 1-hour models beat the baselines by a '
        'small margin, while the 4-hour and daily models did not. Any model that is below the baseline '
        'shows a warning on its signal. Even the small edge is smaller than trading fees if you traded '
        'every signal. Treat signals as one input to your own decision.',
  ),
  (
    'What we never do',
    'TradeMatrix AI never places trades, never asks for exchange keys, and never promises profit.',
  ),
];

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return TmPage(
      header: const BackBar(title: 'How it works'),
      children: [
        const Center(child: Padding(padding: EdgeInsets.symmetric(vertical: 10), child: BrandLockup(logoSize: 48, nameSize: 22))),
        const SizedBox(height: 10),
        for (final (title, text) in _sections) ...[
          GlassCard(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Semantics(header: true, child: Text(title, style: TmText.display(18))),
                const SizedBox(height: 8),
                Text(text, style: TmText.body(14.5, color: Tm.fg2, height: 1.55)),
              ],
            ),
          ),
          const SizedBox(height: 12),
        ],
        const Notice(child: Text(disclaimer)),
      ],
    );
  }
}
