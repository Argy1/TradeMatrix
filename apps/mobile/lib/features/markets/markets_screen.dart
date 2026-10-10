import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/format.dart';
import '../../core/signal_copy.dart';
import '../../data/models.dart';
import '../../data/providers.dart';
import '../../theme/tokens.dart';
import '../../widgets/brand.dart';
import '../../widgets/direction.dart';
import '../../widgets/glass.dart';
import '../../widgets/keycap.dart';
import '../../widgets/page.dart';
import '../../widgets/states.dart';

/// Markets tab: a short hero with the 3D candle scene, every coin with its price and its
/// three signals (1h, 4h, 1d), and the track-record strip.
class MarketsScreen extends ConsumerWidget {
  const MarketsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final markets = ref.watch(marketsProvider);
    return TmPage(
      header: const BrandBar(),
      onRefresh: () async {
        ref.invalidate(marketsProvider);
        ref.invalidate(performanceProvider(30));
      },
      children: [
        const _Hero(),
        const SizedBox(height: 18),
        Semantics(header: true, child: Text("Today's signals", style: TmText.display(22))),
        const SizedBox(height: 4),
        Text('Tap a coin to see its signal and the reasons.', style: TmText.body(13, color: Tm.muted)),
        const SizedBox(height: 12),
        markets.when(
          skipLoadingOnRefresh: true,
          skipLoadingOnReload: true,
          loading: () => const Column(children: [Skeleton(height: 96), SizedBox(height: 12), Skeleton(height: 96)]),
          error: (error, _) => ErrorState(
            message: ErrorState.describe(error, 'Could not load the markets. Please try again.'),
            onRetry: () => ref.invalidate(marketsProvider),
          ),
          data: (rows) => Column(
            children: [
              for (final row in rows) ...[CoinRow(row: row), const SizedBox(height: 12)],
            ],
          ),
        ),
        Text(
          'Each chip is the chance for the next candle of that size. Neutral means the odds are too close, '
          'so we make no call. A warning sign means that model is currently below the simple baseline.',
          style: TmText.body(12.5, color: Tm.muted2, height: 1.5),
        ),
        const SizedBox(height: 20),
        const TrackStrip(),
      ],
    );
  }
}

class _Hero extends StatelessWidget {
  const _Hero();

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('See which way the market leans before you decide.', style: TmText.display(22, height: 1.2)),
          const SizedBox(height: 8),
          Text(
            'The chance the next candle goes up or down, the reasons, and proof of how past signals did.',
            style: TmText.body(14, color: Tm.fg3, height: 1.5),
          ),
          const IsoCandleScene(),
        ],
      ),
    );
  }
}

/// One coin: name, price, 24h change and three chips with direction word + chance.
class CoinRow extends ConsumerWidget {
  const CoinRow({super.key, required this.row, this.trailing});
  final MarketRow row;
  final Widget? trailing;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final change = row.change24hPct;
    return Semantics(
      button: true,
      label: '${row.name}. Open its signal.',
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () {
          ref.read(selectedSymbolProvider.notifier).state = row.symbol;
          context.go('/signals');
        },
        child: GlassCard(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(row.symbol, style: TmText.display(18)),
                        Text(row.name, style: TmText.body(13, color: Tm.muted)),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(row.lastPrice == null ? 'n/a' : formatPrice(row.lastPrice!), style: TmText.mono(15)),
                      Text(
                        '${formatChange(change)} 24h',
                        style: TmText.mono(12,
                            weight: FontWeight.w600,
                            color: change == null ? Tm.muted : (change >= 0 ? Tm.up : Tm.downText)),
                      ),
                    ],
                  ),
                  if (trailing != null) ...[const SizedBox(width: 10), trailing!],
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  for (final tf in timeframes) ...[
                    if (tf != timeframes.first) const SizedBox(width: 8),
                    Expanded(child: _Chip(tf: tf, chip: row.signals[tf])),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.tf, required this.chip});
  final String tf;
  final SignalChip? chip;

  @override
  Widget build(BuildContext context) {
    final c = chip;
    if (c == null) {
      return Tile(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Center(child: Text('$tf · no signal', style: TmText.body(12, color: Tm.muted))),
      );
    }
    final direction = directionOf(c.label);
    final degraded = c.modelStatus == 'degraded';
    return Semantics(
      label: '$tf: ${directionWord[direction]}, ${formatProbability(shownProbability(direction, c.pUp))}'
          '${degraded ? ', model below baseline' : ''}',
      excludeSemantics: true,
      child: Tile(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(tf, style: TmText.mono(11, weight: FontWeight.w600, color: Tm.muted)),
                if (degraded) ...[
                  const SizedBox(width: 4),
                  const Icon(Icons.warning_amber_rounded, size: 12, color: Tm.neutral),
                ],
              ],
            ),
            const SizedBox(height: 3),
            FittedBox(child: DirectionLabel(direction)),
            Text(
              formatProbability(shownProbability(direction, c.pUp)),
              style: TmText.mono(12, color: directionColor(direction, text: true)),
            ),
          ],
        ),
      ),
    );
  }
}

/// "We show our results, even when they are poor": signals recorded, accuracy over 30
/// days, and the simple baseline next to it (docs/06: never accuracy without the baseline).
class TrackStrip extends ConsumerWidget {
  const TrackStrip({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summary = ref.watch(performanceProvider(30));
    final overall = summary.valueOrNull?.overall;
    String pct(double? v) => v == null ? 'n/a' : formatProbability(v);
    return GlassCard(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('We show our results, even when they are poor', style: TmText.display(18, height: 1.25)),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(child: _Stat(label: 'Signals recorded', value: overall == null ? '…' : '${overall.nPredictions}')),
              const SizedBox(width: 8),
              Expanded(child: _Stat(label: 'Accuracy, 30 days', value: overall == null ? '…' : pct(overall.accuracy))),
              const SizedBox(width: 8),
              Expanded(child: _Stat(label: 'Simple baseline', value: overall == null ? '…' : pct(overall.naive))),
            ],
          ),
          const SizedBox(height: 14),
          KeyButton(
            onTap: () => context.go('/more/track-record'),
            child: const Text('See the full track record'),
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.label, required this.value});
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
