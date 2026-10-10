import 'package:flutter/material.dart';

import '../core/signal_copy.dart';
import '../theme/tokens.dart';
import 'direction.dart';

/// The probability meter (docs/08 item 5): a bar from "Down more likely" (red) to
/// "Up more likely" (green), the neutral zone outlined in amber from 45% to 55%, and a 3D
/// knob at P(up). The numbers under it say what the positions mean.
class ProbabilityMeter extends StatelessWidget {
  const ProbabilityMeter({super.key, required this.pUp, required this.direction});

  final double pUp;
  final Direction direction;

  @override
  Widget build(BuildContext context) {
    final label = TmText.body(12, weight: FontWeight.w700);
    final tick = TmText.mono(11, weight: FontWeight.w600, color: Tm.muted2);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(
              child: FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerLeft,
                child: Text('Down more likely', style: label.copyWith(color: Tm.downText)),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerRight,
                child: Text('Up more likely', style: label.copyWith(color: Tm.up)),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        LayoutBuilder(
          builder: (context, box) {
            final width = box.maxWidth;
            const knob = 24.0, bar = 14.0;
            final x = (pUp.clamp(0.0, 1.0) * width).clamp(knob / 2, width - knob / 2);
            return SizedBox(
              height: knob,
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  // The bar itself.
                  Positioned(
                    left: 0,
                    right: 0,
                    top: (knob - bar) / 2,
                    height: bar,
                    child: const DecoratedBox(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.all(Radius.circular(9)),
                        gradient: LinearGradient(
                          colors: [Tm.down, Color(0xFF7A2B3C), Color(0xFF3A3F52), Color(0xFF0F6B52), Tm.up],
                          stops: [0, 0.44, 0.50, 0.56, 1],
                        ),
                        boxShadow: [BoxShadow(color: Color(0x1FFFFFFF), offset: Offset(0, 1))],
                      ),
                    ),
                  ),
                  // Neutral zone, 45% to 55%: an amber outline a little taller than the bar.
                  Positioned(
                    left: width * neutralLow,
                    width: width * (neutralHigh - neutralLow),
                    top: (knob - bar) / 2 - 3,
                    height: bar + 6,
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(7),
                        border: Border.all(color: Tm.neutral, width: 2),
                      ),
                    ),
                  ),
                  // The knob at P(up): a small glossy ball with a ring in the signal color.
                  Positioned(
                    left: x - knob / 2,
                    top: 0,
                    child: Container(
                      width: knob,
                      height: knob,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: const RadialGradient(
                          center: Alignment(-0.3, -0.4),
                          colors: [Colors.white, Tm.fg2],
                          stops: [0, 0.7],
                        ),
                        border: Border.all(color: directionColor(direction), width: 3),
                        boxShadow: const [
                          BoxShadow(color: Color(0x73000000), offset: Offset(0, 3)),
                          BoxShadow(color: Color(0x80000000), offset: Offset(0, 6), blurRadius: 12),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 6),
        // What the positions mean. 45% and 55% sit under the edges of the neutral zone.
        LayoutBuilder(
          builder: (context, box) => SizedBox(
            height: 14,
            child: Stack(
              children: [
                Positioned(left: 0, child: Text('0%', style: tick)),
                Positioned(left: box.maxWidth * neutralLow - 26, child: Text('45%', style: tick)),
                Positioned(left: box.maxWidth * neutralHigh + 4, child: Text('55%', style: tick)),
                Positioned(right: 0, child: Text('100%', style: tick)),
              ],
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          'Neutral zone 45% to 55%: too close to call',
          textAlign: TextAlign.center,
          style: TmText.body(12, weight: FontWeight.w600, color: Tm.neutral),
        ),
      ],
    );
  }
}
