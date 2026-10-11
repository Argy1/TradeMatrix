import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/format.dart';
import '../data/providers.dart';
import '../theme/tokens.dart';
import 'keycap.dart';

/// The candle-size keys (docs/08): the fast sizes, a thin divider, the slow sizes. Eight keys
/// do not fit on a phone, so the row scrolls sideways and brings the picked key into view.
///
/// The picked size is one value for the whole app ([selectedTimeframeProvider]): pick 5m on
/// the markets list and the signal screen opens on 5m too.
class SizeKeys extends ConsumerStatefulWidget {
  const SizeKeys({super.key, this.padding = const EdgeInsets.fromLTRB(20, 0, 20, 12)});
  final EdgeInsetsGeometry padding;

  @override
  ConsumerState<SizeKeys> createState() => _SizeKeysState();
}

class _SizeKeysState extends ConsumerState<SizeKeys> {
  final _picked = GlobalKey();

  /// Scroll the picked key into the middle of the row (after the frame, when it has a size).
  void _reveal() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final target = _picked.currentContext;
      if (target != null && mounted) {
        Scrollable.ensureVisible(target, alignment: 0.5, duration: const Duration(milliseconds: 200));
      }
    });
  }

  @override
  void initState() {
    super.initState();
    _reveal();
  }

  @override
  Widget build(BuildContext context) {
    final tf = ref.watch(selectedTimeframeProvider);
    ref.listen(selectedTimeframeProvider, (previous, next) => _reveal());

    Widget key(String option) => Padding(
          key: option == tf ? _picked : null,
          padding: const EdgeInsets.only(right: 8),
          child: KeyButton(
            onTap: () => ref.read(selectedTimeframeProvider.notifier).state = option,
            selected: option == tf,
            minWidth: 52,
            semanticLabel: 'Candle size ${timeframeWords(option)}',
            child: Text(option, style: TmText.mono(14, weight: FontWeight.w600)),
          ),
        );

    return Padding(
      padding: widget.padding,
      child: Row(
        children: [
          Text('Candle size', style: TmText.body(13, weight: FontWeight.w600, color: Tm.muted)),
          const SizedBox(width: 10),
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              // Room for the keys' shadow, which would be cut off at the scroll edge.
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                children: [
                  for (final option in fastTimeframes) key(option),
                  Container(width: 1, height: 26, color: const Color(0x33FFFFFF)),
                  const SizedBox(width: 8),
                  for (final option in slowTimeframes) key(option),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
