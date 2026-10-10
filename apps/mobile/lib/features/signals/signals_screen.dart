import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/signal_copy.dart';
import '../../data/api.dart';
import '../../data/live.dart';
import '../../data/models.dart';
import '../../data/providers.dart';
import '../../theme/tokens.dart';
import '../../widgets/direction.dart';
import '../../widgets/keycap.dart';
import '../../widgets/page.dart';
import '../../widgets/states.dart';
import 'signal_card.dart';

/// Screen 1 (docs/08, mobile): pick a coin and a candle size, read the signal, and either
/// set an alert or tap "Why?" for the details.
class SignalsScreen extends ConsumerWidget {
  const SignalsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final symbol = ref.watch(selectedSymbolProvider);
    final tf = ref.watch(selectedTimeframeProvider);
    final CoinKey key = (symbol: symbol, tf: tf);
    final markets = ref.watch(marketsProvider);
    final prediction = ref.watch(predictionProvider(key));
    final live = ref.watch(liveProvider(key));
    final coinName = markets.valueOrNull?.where((m) => m.symbol == symbol).firstOrNull?.name ?? symbol;

    return TmPage(
      header: const BrandBar(),
      padding: const EdgeInsets.only(bottom: 28),
      onRefresh: () async {
        ref.invalidate(marketsProvider);
        ref.invalidate(predictionProvider(key));
        try {
          await ref.read(predictionProvider(key).future);
        } catch (_) {
          // The error state on the page already says what went wrong.
        }
      },
      children: [
        _CoinChips(markets: markets.valueOrNull ?? const [], symbol: symbol, tf: tf),
        _TimeframeRow(tf: tf),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (live.updating)
                const Padding(
                  padding: EdgeInsets.only(bottom: 10),
                  child: Notice(
                    icon: Icons.sync_rounded,
                    child: Text('Updating signal… the candle just closed.'),
                  ),
                ),
              prediction.when(
                skipLoadingOnRefresh: true,
                skipLoadingOnReload: true,
                loading: () => const Skeleton(height: 470),
                error: (error, _) => ErrorState(
                  message: error is ApiException && error.notFound
                      ? 'No signal yet for this coin and candle size. '
                          'The first one appears after the next candle closes.'
                      : ErrorState.describe(error, 'Could not load the signal. Please try again.'),
                  onRetry: () => ref.invalidate(predictionProvider(key)),
                ),
                data: (p) => Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (p.stale)
                      const Padding(
                        padding: EdgeInsets.only(bottom: 10),
                        child: Notice(child: Text(staleWarning)),
                      ),
                    if (p.degraded)
                      const Padding(
                        padding: EdgeInsets.only(bottom: 10),
                        child: Notice(child: Text(degradedWarning)),
                      ),
                    SignalCard(prediction: p, coinName: coinName),
                    const SizedBox(height: 14),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(child: AlertOnChangeButton(symbol: symbol, tf: tf)),
                        const SizedBox(width: 10),
                        KeyButton(
                          onTap: () => context.go('/signals/details'),
                          minHeight: 52,
                          radius: Tm.rButton,
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          semanticLabel: 'Why this signal? Open the details',
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [Text('Why?'), SizedBox(width: 6), Icon(Icons.arrow_downward_rounded, size: 18)],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    ValidityLine(prediction: p),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                alignment: WrapAlignment.center,
                crossAxisAlignment: WrapCrossAlignment.center,
                spacing: 10,
                runSpacing: 4,
                children: [
                  _LiveLine(live: live),
                  Text(disclaimerShort, style: TmText.body(12, color: Tm.muted2)),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Horizontally scrolling coin keys; each shows the coin's current direction as a word.
class _CoinChips extends ConsumerWidget {
  const _CoinChips({required this.markets, required this.symbol, required this.tf});
  final List<MarketRow> markets;
  final String symbol, tf;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (markets.isEmpty) {
      return const Padding(padding: EdgeInsets.fromLTRB(16, 6, 16, 10), child: Skeleton(height: 56));
    }
    // Tall enough for two lines of text at the phone's text size (56 px at the normal size).
    final chipHeight = MediaQuery.textScalerOf(context).scale(40) + 18;
    return SizedBox(
      height: chipHeight + 20,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.fromLTRB(20, 6, 20, 14),
        itemCount: markets.length,
        separatorBuilder: (_, _) => const SizedBox(width: 10),
        itemBuilder: (context, index) {
          final row = markets[index];
          final chip = row.signals[tf];
          final direction = directionOf(chip?.label ?? 'neutral');
          final word = chip == null ? 'no signal' : directionWord[direction]!;
          return KeyButton(
            onTap: () => ref.read(selectedSymbolProvider.notifier).state = row.symbol,
            selected: row.symbol == symbol,
            minWidth: 78,
            minHeight: 56,
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            semanticLabel: '${row.name}, $word',
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(row.symbol, style: TmText.display(16)),
                Text(
                  word,
                  style: TmText.body(12,
                      weight: FontWeight.w700,
                      color: chip == null ? Tm.muted : directionColor(direction, text: true)),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _TimeframeRow extends ConsumerWidget {
  const _TimeframeRow({required this.tf});
  final String tf;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
      child: Row(
        children: [
          Flexible(
            child: Text('Candle size',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TmText.body(13, weight: FontWeight.w600, color: Tm.muted)),
          ),
          for (final option in timeframes) ...[
            const SizedBox(width: 10),
            Expanded(
              child: KeyButton(
                onTap: () => ref.read(selectedTimeframeProvider.notifier).state = option,
                selected: option == tf,
                semanticLabel: 'Candle size $option',
                child: Text(option, style: TmText.mono(14, weight: FontWeight.w600)),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

/// "Live" / "Connecting" / "Offline, retrying": a dot and always a word (never color alone).
class _LiveLine extends StatelessWidget {
  const _LiveLine({required this.live});
  final LiveState live;

  @override
  Widget build(BuildContext context) {
    final (color, text) = switch (live.status) {
      LiveStatus.live => (Tm.up, 'Live'),
      LiveStatus.connecting => (Tm.neutral, 'Connecting…'),
      LiveStatus.offline => (Tm.down, 'Offline, retrying'),
    };
    return Semantics(
      liveRegion: true,
      child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
            const SizedBox(width: 8),
            Text(text, style: TmText.body(12, color: Tm.muted)),
          ],
      ),
    );
  }
}

/// "Alert me on change": one tap makes a "the signal changes" rule for this coin and
/// candle size. Signed out, it leads to sign-in; with the rule already there, it says so.
class AlertOnChangeButton extends ConsumerStatefulWidget {
  const AlertOnChangeButton({super.key, required this.symbol, required this.tf});
  final String symbol, tf;

  @override
  ConsumerState<AlertOnChangeButton> createState() => _AlertOnChangeButtonState();
}

class _AlertOnChangeButtonState extends ConsumerState<AlertOnChangeButton> {
  bool _busy = false;

  Future<void> _create() async {
    setState(() => _busy = true);
    final messenger = ScaffoldMessenger.of(context);
    try {
      await ref.read(alertsProvider.notifier).create(
            symbol: widget.symbol,
            type: 'signal_change',
            timeframe: widget.tf,
          );
      messenger.showSnackBar(SnackBar(
        content: Text('Alert set: you are told when the ${widget.symbol} ${widget.tf} signal changes.'),
      ));
    } on ApiException catch (e) {
      messenger.showSnackBar(SnackBar(content: Text(e.message)));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final signedIn = ref.watch(sessionProvider).valueOrNull != null;
    if (!signedIn) {
      return PrimaryButton(
        label: 'Sign in to get alerts',
        icon: Icons.notifications_none_rounded,
        onTap: () => context.push('/login'),
      );
    }
    final rules = ref.watch(alertsProvider).valueOrNull?.items ?? const <AlertRule>[];
    final exists = rules.any(
      (r) => r.type == 'signal_change' && r.symbol == widget.symbol && r.timeframe == widget.tf,
    );
    if (exists) {
      return KeyButton(
        onTap: () => context.go('/alerts'),
        minHeight: 52,
        radius: Tm.rButton,
        semanticLabel: 'Alert is set. Manage alerts',
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [Icon(Icons.check_rounded, size: 20, color: Tm.up), SizedBox(width: 8), Text('Alert is set')],
        ),
      );
    }
    return PrimaryButton(
      label: 'Alert me on change',
      icon: Icons.notifications_none_rounded,
      busy: _busy,
      onTap: _create,
    );
  }
}
