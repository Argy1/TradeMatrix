import 'package:flutter/material.dart';

import '../core/signal_copy.dart';
import '../theme/tokens.dart';

/// Signal color. `text: true` picks the lighter red that stays readable on the dark page.
Color directionColor(Direction direction, {bool text = false}) => switch (direction) {
      Direction.up => Tm.up,
      Direction.down => text ? Tm.downText : Tm.down,
      Direction.neutral => Tm.neutral,
    };

/// Arrow up, arrow down or a dash. Always shown together with a word: color and shape are
/// never the only cue (docs/08).
IconData directionIcon(Direction direction) => switch (direction) {
      Direction.up => Icons.arrow_upward_rounded,
      Direction.down => Icons.arrow_downward_rounded,
      Direction.neutral => Icons.remove_rounded,
    };

class DirectionLabel extends StatelessWidget {
  const DirectionLabel(this.direction, {super.key, this.size = 12, this.word, this.trailing});

  final Direction direction;
  final double size;
  final String? word;
  final String? trailing; // e.g. a probability, shown in the mono font

  @override
  Widget build(BuildContext context) {
    final color = directionColor(direction, text: true);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(directionIcon(direction), size: size + 3, color: color),
        const SizedBox(width: 3),
        Text(word ?? directionWord[direction]!, style: TmText.body(size, weight: FontWeight.w700, color: color)),
        if (trailing != null) ...[
          const SizedBox(width: 5),
          Text(trailing!, style: TmText.mono(size, color: color)),
        ],
      ],
    );
  }
}
