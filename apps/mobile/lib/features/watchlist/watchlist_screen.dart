import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api.dart';
import '../../data/providers.dart';
import '../../theme/tokens.dart';
import '../../widgets/keycap.dart';
import '../../widgets/page.dart';
import '../../widgets/states.dart';
import '../markets/markets_screen.dart';

/// Watchlist tab: the coins the person follows, with their three signals, and keys to add
/// the others. Signed out, it explains what the list is for and offers sign-in.
class WatchlistScreen extends ConsumerWidget {
  const WatchlistScreen({super.key});

  Future<void> _toggle(BuildContext context, WidgetRef ref, String symbol) async {
    final messenger = ScaffoldMessenger.of(context);
    try {
      await ref.read(watchlistProvider.notifier).toggle(symbol);
    } on ApiException catch (e) {
      messenger.showSnackBar(SnackBar(content: Text(e.message)));
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionProvider);
    final signedIn = session.valueOrNull != null;
    final watchlist = ref.watch(watchlistProvider);
    final markets = ref.watch(marketsProvider);

    final List<Widget> body;
    if (session.isLoading) {
      body = const [Skeleton(height: 140)];
    } else if (!signedIn) {
      body = [
        EmptyState(
          title: 'Keep the coins you follow in one place',
          text: 'Sign in to build a watchlist. Signals stay public either way.',
          action: PrimaryButton(label: 'Sign in', onTap: () => context.push('/login')),
        ),
      ];
    } else if (watchlist.hasError || markets.hasError) {
      body = [
        ErrorState(
          message: ErrorState.describe(watchlist.error ?? markets.error!, 'Could not load your watchlist.'),
          onRetry: () {
            ref.invalidate(watchlistProvider);
            ref.invalidate(marketsProvider);
          },
        ),
      ];
    } else if (!watchlist.hasValue || !markets.hasValue) {
      body = const [Skeleton(height: 96), SizedBox(height: 12), Skeleton(height: 96)];
    } else {
      final watched = watchlist.value!.toSet();
      final mine = markets.value!.where((m) => watched.contains(m.symbol)).toList();
      final others = markets.value!.where((m) => !watched.contains(m.symbol)).toList();
      body = [
        if (mine.isEmpty)
          const EmptyState(
            title: 'Your watchlist is empty',
            text: 'Add a coin below to see its signals here at a glance.',
          )
        else
          for (final row in mine) ...[
            CoinRow(
              row: row,
              trailing: KeyButton(
                onTap: () => _toggle(context, ref, row.symbol),
                padding: EdgeInsets.zero,
                semanticLabel: 'Remove ${row.name} from watchlist',
                child: const Icon(Icons.star_rounded, color: Tm.neutral),
              ),
            ),
            const SizedBox(height: 12),
          ],
        if (others.isNotEmpty) ...[
          const SizedBox(height: 8),
          const SectionHeader('Add a coin'),
          const SizedBox(height: 12),
          Wrap(
            spacing: 10,
            runSpacing: 12,
            children: [
              for (final row in others)
                KeyButton(
                  onTap: () => _toggle(context, ref, row.symbol),
                  semanticLabel: 'Add ${row.name} to watchlist',
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.star_border_rounded, size: 18),
                      const SizedBox(width: 6),
                      Text(row.symbol),
                    ],
                  ),
                ),
            ],
          ),
        ],
      ];
    }

    return TmPage(
      header: const BrandBar(),
      onRefresh: () async {
        ref.invalidate(watchlistProvider);
        ref.invalidate(marketsProvider);
      },
      children: [
        Semantics(header: true, child: Text('Watchlist', style: TmText.display(26))),
        const SizedBox(height: 14),
        ...body,
      ],
    );
  }
}
