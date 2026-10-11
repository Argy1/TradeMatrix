import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/format.dart';
import '../../core/signal_copy.dart';
import '../../data/models.dart';
import '../../data/providers.dart';
import '../../theme/tokens.dart';
import '../../widgets/direction.dart';
import '../../widgets/glass.dart';
import '../../widgets/meter.dart';
import '../../widgets/orb.dart';

/// The most important component (docs/08): everything a person needs to read a signal in
/// ten seconds, always together: the direction word, the chance, a plain sentence, where
/// and where that chance sits on the Down-to-Up scale. The screen puts the validity line
/// ([ValidityLine]) right under the buttons, so the buttons stay above the fold on a phone.
class SignalCard extends StatefulWidget {
  const SignalCard({super.key, required this.prediction, required this.coinName});

  final Prediction prediction;
  final String coinName;

  /// After a fast candle closes, the next signal needs a few seconds to arrive. Longer than
  /// this and the old direction must not stay on screen as if it were current.
  static const expiredAfter = Duration(seconds: 8);

  @override
  State<SignalCard> createState() => _SignalCardState();
}

class _SignalCardState extends State<SignalCard> {
  Timer? _tick;

  /// Only the fast sizes can expire while someone is looking: check once a second.
  void _startTick() {
    _tick?.cancel();
    _tick = isFast(widget.prediction.timeframe)
        ? Timer.periodic(const Duration(seconds: 1), (_) => setState(() {}))
        : null;
  }

  @override
  void initState() {
    super.initState();
    _startTick();
  }

  @override
  void didUpdateWidget(SignalCard old) {
    super.didUpdateWidget(old);
    // The same card stays on screen when another candle size is picked.
    if (old.prediction.timeframe != widget.prediction.timeframe) _startTick();
  }

  @override
  void dispose() {
    _tick?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final prediction = widget.prediction;
    final coinName = widget.coinName;
    final expired = isFast(prediction.timeframe) &&
        DateTime.now().toUtc().isAfter(prediction.targetCloseTime.add(SignalCard.expiredAfter));
    if (expired) return _Waiting(tf: prediction.timeframe, coinName: coinName);
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

/// Shown in place of an expired fast signal: no direction, no number, only that we wait.
class _Waiting extends StatelessWidget {
  const _Waiting({required this.tf, required this.coinName});
  final String tf, coinName;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      container: true,
      liveRegion: true,
      child: GlassCard(
        padding: const EdgeInsets.fromLTRB(18, 28, 18, 28),
        child: Column(
          children: [
            const Icon(Icons.schedule_rounded, size: 30, color: Tm.neutral),
            const SizedBox(height: 10),
            Text(waitingTitle, textAlign: TextAlign.center, style: TmText.display(20, color: Tm.neutral)),
            const SizedBox(height: 6),
            Text(
              '$waitingForSignal ($tf, $coinName)',
              textAlign: TextAlign.center,
              style: TmText.body(14, color: Tm.fg2, height: 1.5),
            ),
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

  /// Fast candles count down by the second; the slow ones every 20 seconds, as before.
  void _startTick() {
    _tick?.cancel();
    final every = isFast(widget.prediction.timeframe) ? 1 : 20;
    _tick = Timer.periodic(Duration(seconds: every), (_) => setState(() {}));
  }

  @override
  void initState() {
    super.initState();
    _startTick();
  }

  @override
  void didUpdateWidget(ValidityLine old) {
    super.didUpdateWidget(old);
    if (old.prediction.timeframe != widget.prediction.timeframe) _startTick();
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
    final countdown = formatCountdown(closes, DateTime.now().toUtc(), seconds: isFast(p.timeframe));
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
