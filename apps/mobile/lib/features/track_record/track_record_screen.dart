import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/format.dart';
import '../../core/signal_copy.dart';
import '../../data/models.dart';
import '../../data/providers.dart';
import '../../theme/tokens.dart';
import '../../widgets/glass.dart';
import '../../widgets/keycap.dart';
import '../../widgets/page.dart';
import '../../widgets/states.dart';

final _daysProvider = StateProvider.autoDispose<int>((ref) => 30);

/// Track record: the live results, shown as they are, always next to the simple baseline
/// (CLAUDE.md rule 1). Every number comes from stored signals and their outcomes.
class TrackRecordScreen extends ConsumerWidget {
  const TrackRecordScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final days = ref.watch(_daysProvider);
    final summary = ref.watch(performanceProvider(days));
    String pct(double? v) => v == null ? 'n/a' : formatProbability(v);

    return TmPage(
      header: const BackBar(title: 'Track record', subtitle: 'We show our results, even when they are poor'),
      onRefresh: () async => ref.invalidate(performanceProvider(days)),
      children: [
        Row(
          children: [
            for (final option in const [7, 30, 90]) ...[
              if (option != 7) const SizedBox(width: 10),
              Expanded(
                child: KeyButton(
                  onTap: () => ref.read(_daysProvider.notifier).state = option,
                  selected: option == days,
                  semanticLabel: 'Last $option days',
                  child: Text('$option days', style: TmText.mono(13, weight: FontWeight.w600)),
                ),
              ),
            ],
          ],
        ),
        const SizedBox(height: 16),
        summary.when(
          skipLoadingOnRefresh: true,
          loading: () => const Column(children: [Skeleton(height: 110), SizedBox(height: 12), Skeleton(height: 300)]),
          error: (error, _) => ErrorState(
            message: ErrorState.describe(error, 'Could not load the track record.'),
            onRetry: () => ref.invalidate(performanceProvider(days)),
          ),
          data: (data) {
            final o = data.overall;
            final rows = [...data.rows]..sort((a, b) {
                final tf = timeframes.indexOf(a.timeframe ?? '').compareTo(timeframes.indexOf(b.timeframe ?? ''));
                return tf != 0 ? tf : 0;
              });
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                GlassCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Expanded(child: _Stat('Signals recorded', '${o.nPredictions}')),
                          const SizedBox(width: 8),
                          Expanded(child: _Stat('Model accuracy', pct(o.accuracy))),
                          const SizedBox(width: 8),
                          Expanded(child: _Stat('Simple baseline', pct(o.naive))),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        reliabilitySentence(o.accuracy, o.naive, o.nResolved, o.lowSample),
                        style: TmText.body(14, color: Tm.fg2, height: 1.5),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                GlassCard(
                  padding: const EdgeInsets.fromLTRB(16, 18, 16, 10),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const SectionHeader(
                        'Per coin and candle size',
                        subtitle: 'Accuracy counts only Up and Down calls. '
                            'Baseline = "repeat the last move" on the same candles.',
                      ),
                      const SizedBox(height: 10),
                      for (final row in rows) _Row(row: row),
                    ],
                  ),
                ),
              ],
            );
          },
        ),
        const SizedBox(height: 16),
        const Notice(child: Text(disclaimer)),
      ],
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat(this.label, this.value);
  final String label, value;

  @override
  Widget build(BuildContext context) {
    return Tile(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
      child: Column(
        children: [
          FittedBox(child: Text(value, style: TmText.mono(18))),
          const SizedBox(height: 4),
          Text(label, textAlign: TextAlign.center, style: TmText.body(12, color: Tm.muted, height: 1.25)),
        ],
      ),
    );
  }
}

/// One coin and candle size: finished signals, model accuracy, baseline, and in words
/// whether the model is ahead (never by color alone).
class _Row extends StatelessWidget {
  const _Row({required this.row});
  final Performance row;

  @override
  Widget build(BuildContext context) {
    final a = row.accuracy, b = row.naive;
    final verdict = (a == null || b == null)
        ? 'only Neutral so far'
        : a > b
            ? 'ahead'
            : a < b
                ? 'behind'
                : 'level';
    final color = verdict == 'ahead' ? Tm.up : (verdict == 'behind' ? Tm.downText : Tm.muted);
    String pct(double? v) => v == null ? 'n/a' : formatProbability(v);
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 10),
      decoration: const BoxDecoration(border: Border(top: BorderSide(color: Color(0x14FFFFFF)))),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text.rich(TextSpan(
                  text: '${row.symbol} ',
                  style: TmText.body(14, weight: FontWeight.w700),
                  children: [
                    TextSpan(text: row.timeframe, style: TmText.mono(12, weight: FontWeight.w600, color: Tm.muted)),
                  ],
                )),
              ),
              Text(verdict, style: TmText.body(12, weight: FontWeight.w700, color: color)),
            ],
          ),
          const SizedBox(height: 3),
          Text('Model ${pct(a)} · baseline ${pct(b)}', style: TmText.mono(12, weight: FontWeight.w600, color: Tm.fg2)),
          Text('${row.nResolved} finished${row.lowSample ? ' · small sample' : ''}',
              style: TmText.body(12, color: row.lowSample ? Tm.neutral : Tm.muted)),
        ],
      ),
    );
  }
}
