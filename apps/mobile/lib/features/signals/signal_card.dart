import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/format.dart';
import '../../core/signal_copy.dart';
import '../../data/models.dart';
import '../../theme/tokens.dart';
import '../../widgets/direction.dart';
import '../../widgets/glass.dart';
import '../../widgets/meter.dart';
import '../../widgets/orb.dart';

/// The most important component (docs/08): everything a person needs to read a signal in
/// ten seconds, always together: the direction word, the chance, a plain sentence, where
/// and where that chance sits on the Down-to-Up scale. The screen puts the validity line
/// ([ValidityLine]) right under the buttons, so the buttons stay above the fold on a phone.
class SignalCard extends StatelessWidget {
  const SignalCard({super.key, required this.prediction, required this.coinName});

  final Prediction prediction;
  final String coinName;

  @override
  Widget build(BuildContext context) {
    final direction = directionOf(prediction.label);
    final color = directionColor(direction, text: true);
    final tf = prediction.timeframe;
    return Semantics(
      container: true,
      // A screen reader gets the whole signal as one sentence first.
      label: screenReaderSummary(coinName, tf, prediction.label, prediction.pUp),
      child: GlassCard(
        tint: directionColor(direction),
        padding: const EdgeInsets.fromLTRB(18, 16, 18, 18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // A Wrap, not a Row: with large text the second part moves to its own line.
            Wrap(
              alignment: WrapAlignment.spaceBetween,
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 12,
              runSpacing: 2,
              children: [
                Text('TRADEMATRIX SIGNAL',
                    style: TmText.body(12, weight: FontWeight.w700, color: Tm.muted, spacing: 1.1)),
                Text('next $tf candle · $coinName', style: TmText.body(13, color: Tm.muted)),
              ],
            ),
            const SizedBox(height: 10),
            Center(
              child: SignalOrb(direction: direction, probability: shownProbability(direction, prediction.pUp)),
            ),
            const SizedBox(height: 8),
            Text(headline[direction]!, textAlign: TextAlign.center, style: TmText.display(21, color: color)),
            const SizedBox(height: 6),
            Text(
              plainSentence(direction, prediction.pUp, tf, prediction.baseClose),
              textAlign: TextAlign.center,
              style: TmText.body(14.5, color: Tm.fg2, height: 1.5),
            ),
            const SizedBox(height: 16),
            ProbabilityMeter(pUp: prediction.pUp, direction: direction),
          ],
        ),
      ),
    );
  }
}

/// "Valid for the 1h candle that closes at 22:00 WIB, in 41 min." The countdown ticks by
/// itself, so the screen does not need a refresh to stay true.
class ValidityLine extends StatefulWidget {
  const ValidityLine({super.key, required this.prediction});
  final Prediction prediction;

  @override
  State<ValidityLine> createState() => _ValidityLineState();
}

class _ValidityLineState extends State<ValidityLine> {
  Timer? _tick;

  @override
  void initState() {
    super.initState();
    _tick = Timer.periodic(const Duration(seconds: 20), (_) => setState(() {}));
  }

  @override
  void dispose() {
    _tick?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.prediction;
    final closes = p.targetCloseTime;
    final countdown = formatCountdown(closes, DateTime.now().toUtc());
    final text = countdown == 'now'
        ? 'The ${p.timeframe} candle has just closed. A new signal appears in a moment.'
        : 'Valid for the ${p.timeframe} candle that closes at ${formatClock(closes)}, $countdown. '
            'A new signal appears right after it closes.';
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(top: 1),
          child: Icon(Icons.schedule_rounded, size: 16, color: Tm.muted),
        ),
        const SizedBox(width: 8),
        Expanded(child: Text(text, style: TmText.body(12.5, color: Tm.fg3, height: 1.45))),
      ],
    );
  }
}
