import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/format.dart';
import '../../core/signal_copy.dart';
import '../../data/live.dart';
import '../../data/models.dart';
import '../../data/providers.dart';
import '../../theme/tokens.dart';
import '../../widgets/direction.dart';
import '../../widgets/glass.dart';
import '../../widgets/page.dart';
import '../../widgets/states.dart';
import 'candle_chart.dart';

/// Screen 2 (docs/08, mobile): the proof behind the signal. Chart with the NEXT column,
/// why this signal, how reliable it has been, recent results, news tone, full disclaimer.
class DetailsScreen extends ConsumerWidget {
  const DetailsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final symbol = ref.watch(selectedSymbolProvider);
    final tf = ref.watch(selectedTimeframeProvider);
    final CoinKey key = (symbol: symbol, tf: tf);
    ref.watch(liveProvider(key)); // keeps the live stream open while this screen is shown
    final market = ref.watch(marketsProvider).valueOrNull?.where((m) => m.symbol == symbol).firstOrNull;
    final coinName = market?.name ?? symbol;
    final prediction = ref.watch(predictionProvider(key));
    final p = prediction.valueOrNull;

    return TmPage(
      header: BackBar(
        title: '$coinName · $tf',
        subtitle: 'TradeMatrix AI · Created by Argy',
        trailing: p == null ? null : _SignalChip(prediction: p),
      ),
      onRefresh: () async {
        ref.invalidate(candlesProvider(key));
        ref.invalidate(predictionProvider(key));
        ref.invalidate(historyProvider(key));
        ref.invalidate(newsProvider(symbol));
      },
      children: [
        _ChartCard(coinKey: key, market: market, prediction: p),
        const SizedBox(height: 16),
        if (p != null) ...[
          if (p.degraded) ...[const Notice(child: Text(degradedWarning)), const SizedBox(height: 16)],
          _WhyCard(prediction: p),
          const SizedBox(height: 16),
          _ReliabilityCard(prediction: p),
          const SizedBox(height: 16),
        ] else if (prediction.hasError) ...[
          ErrorState(
            message: ErrorState.describe(prediction.error!, 'Could not load the signal. Please try again.'),
            onRetry: () => ref.invalidate(predictionProvider(key)),
          ),
          const SizedBox(height: 16),
        ] else ...[
          const Skeleton(height: 260),
          const SizedBox(height: 16),
        ],
        _RecentCard(coinKey: key),
        const SizedBox(height: 16),
        _NewsCard(symbol: symbol, coinName: coinName, sentimentUsed: p?.sentimentUsed ?? false),
        const SizedBox(height: 16),
        Notice(
          child: Text.rich(TextSpan(children: [
            TextSpan(
              text: 'Not financial advice. ',
              style: TmText.body(13, weight: FontWeight.w700, color: const Color(0xFFFFE7A8)),
            ),
            TextSpan(text: p?.disclaimer ?? disclaimer),
          ])),
        ),
      ],
    );
  }
}

/// The small "UP 58.2%" chip in the top bar: icon + word + number.
class _SignalChip extends StatelessWidget {
  const _SignalChip({required this.prediction});
  final Prediction prediction;

  @override
  Widget build(BuildContext context) {
    final direction = directionOf(prediction.label);
    final color = directionColor(direction);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.45)),
      ),
      child: DirectionLabel(
        direction,
        size: 13,
        word: orbWord[direction],
        trailing: formatProbability(shownProbability(direction, prediction.pUp)),
      ),
    );
  }
}

class _ChartCard extends ConsumerWidget {
  const _ChartCard({required this.coinKey, required this.market, required this.prediction});
  final CoinKey coinKey;
  final MarketRow? market;
  final Prediction? prediction;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final candles = ref.watch(candlesProvider(coinKey));
    return GlassCard(
      child: candles.when(
        skipLoadingOnRefresh: true,
        skipLoadingOnReload: true,
        loading: () => const SizedBox(height: 330, child: Center(child: CircularProgressIndicator(color: Tm.cyan))),
        error: (error, _) => ErrorState(
          message: ErrorState.describe(error, 'Could not load the chart.'),
          onRetry: () => ref.invalidate(candlesProvider(coinKey)),
        ),
        data: (data) {
          if (data.candles.isEmpty) return Text('No candles yet.', style: TmText.body(14, color: Tm.fg2));
          final change = market?.change24hPct;
          final direction = prediction == null ? null : directionOf(prediction!.label);
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Flexible(
                    child: FittedBox(
                      fit: BoxFit.scaleDown,
                      alignment: Alignment.centerLeft,
                      child: Text(formatPrice(data.candles.last.c), style: TmText.mono(26, spacing: -0.5)),
                    ),
                  ),
                  if (change != null) ...[
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: (change >= 0 ? Tm.up : Tm.down).withValues(alpha: 0.14),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(mainAxisSize: MainAxisSize.min, children: [
                        Icon(change >= 0 ? Icons.arrow_drop_up_rounded : Icons.arrow_drop_down_rounded,
                            size: 18, color: change >= 0 ? Tm.up : Tm.downText),
                        Text('${formatChange(change)} 24h',
                            style: TmText.mono(13, color: change >= 0 ? Tm.up : Tm.downText)),
                      ]),
                    ),
                  ],
                ],
              ),
              if (data.stale) ...[
                const SizedBox(height: 8),
                Text(staleWarning, style: TmText.body(13, color: Tm.neutral)),
              ],
              const SizedBox(height: 10),
              CandleChart(
                candles: data.candles,
                timeframe: coinKey.tf,
                next: direction == null
                    ? null
                    : NextSignal(
                        direction: direction,
                        probability: shownProbability(direction, prediction!.pUp),
                        degraded: prediction!.degraded,
                      ),
              ),
              const SizedBox(height: 6),
              Text('Dashed NEXT column: the signal for the candle that has not started yet.',
                  style: TmText.body(12, color: Tm.muted2)),
            ],
          );
        },
      ),
    );
  }
}

/// Up to three reasons, each with an icon, the reason, one plain sentence that explains
/// the term, and a tag that says which way it pushes.
class _WhyCard extends StatelessWidget {
  const _WhyCard({required this.prediction});
  final Prediction prediction;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.fromLTRB(16, 18, 16, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader('Why this signal', subtitle: 'The three things that mattered most, in plain words.'),
          const SizedBox(height: 6),
          for (final reason in prediction.reasons) _ReasonRow(reason: reason),
        ],
      ),
    );
  }
}

class _ReasonRow extends StatelessWidget {
  const _ReasonRow({required this.reason});
  final Reason reason;

  @override
  Widget build(BuildContext context) {
    final direction = switch (reason.effect) {
      'up' => Direction.up,
      'down' => Direction.down,
      _ => Direction.neutral,
    };
    final color = directionColor(direction);
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 14),
      decoration: const BoxDecoration(border: Border(top: BorderSide(color: Color(0x14FFFFFF)))),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.14),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: color.withValues(alpha: 0.45)),
              boxShadow: const [BoxShadow(color: Color(0x66000000), offset: Offset(0, 3))],
            ),
            child: Icon(directionIcon(direction), size: 18, color: directionColor(direction, text: true)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(reason.text, style: TmText.body(15, weight: FontWeight.w700)),
                const SizedBox(height: 3),
                Text(reasonExplainers[reason.code] ?? '', style: TmText.body(13.5, color: Tm.fg3, height: 1.45)),
                const SizedBox(height: 6),
                Text(
                  effectTag[reason.effect] ?? effectTag['none']!,
                  style: TmText.body(12, weight: FontWeight.w700, color: directionColor(direction, text: true)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Model accuracy next to the simple baseline, on a 40% to 60% scale, with the honest
/// sentence under it (docs/06: never show accuracy without the baseline).
class _ReliabilityCard extends StatelessWidget {
  const _ReliabilityCard({required this.prediction});
  final Prediction prediction;

  @override
  Widget build(BuildContext context) {
    final recent = prediction.recentAccuracy;
    return GlassCard(
      padding: const EdgeInsets.fromLTRB(16, 18, 16, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SectionHeader(
            'How reliable is it?',
            subtitle: 'Real results from the last ${recent.n} finished ${prediction.timeframe} signals '
                'for ${prediction.symbol}.',
          ),
          const SizedBox(height: 14),
          _Bar(
            label: 'TradeMatrix model',
            value: recent.model,
            valueColor: Tm.cyanLight,
            colors: const [Tm.cyanLight, Tm.cyanDeep],
            glow: true,
          ),
          const SizedBox(height: 14),
          _Bar(
            label: 'Baseline: repeat the last move',
            value: recent.naiveBaseline,
            valueColor: Tm.fg3,
            colors: const [Color(0xFF8E9AB8), Color(0xFF5C6784)],
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              for (final tick in ['40%', '50%', '60%']) Text(tick, style: TmText.mono(11, weight: FontWeight.w600, color: Tm.muted2)),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            reliabilitySentence(recent.model, recent.naiveBaseline, recent.n, recent.lowSample),
            style: TmText.body(14, color: Tm.fg2, height: 1.5),
          ),
        ],
      ),
    );
  }
}

class _Bar extends StatelessWidget {
  const _Bar({required this.label, required this.value, required this.valueColor, required this.colors, this.glow = false});
  final String label;
  final double? value;
  final Color valueColor;
  final List<Color> colors;
  final bool glow;

  @override
  Widget build(BuildContext context) {
    // The bar runs from 40% to 60%: crypto accuracy lives close to a coin flip.
    final fill = value == null ? 0.0 : ((value! - 0.40) / 0.20).clamp(0.0, 1.0);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Flexible(child: Text(label, style: TmText.body(14, weight: FontWeight.w600))),
            Text(value == null ? 'n/a' : formatProbability(value!), style: TmText.mono(14, color: valueColor)),
          ],
        ),
        const SizedBox(height: 6),
        Container(
          height: 14,
          decoration: BoxDecoration(color: const Color(0x14FFFFFF), borderRadius: BorderRadius.circular(8)),
          alignment: Alignment.centerLeft,
          child: FractionallySizedBox(
            widthFactor: fill,
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: colors),
                boxShadow: glow ? const [BoxShadow(color: Color(0x803FC4EE), blurRadius: 14)] : null,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

/// Recent results as keycap tiles: Hit, Miss or Skip, with the direction icon.
class _RecentCard extends ConsumerWidget {
  const _RecentCard({required this.coinKey});
  final CoinKey coinKey;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final history = ref.watch(historyProvider(coinKey));
    final resolved = (history.valueOrNull ?? const <HistoryItem>[]).where((h) => h.resolved).toList();
    final calls = resolved.where((h) => h.correct != null).toList();
    final hits = calls.where((h) => h.correct == true).length;
    final skipped = resolved.length - calls.length;
    return GlassCard(
      padding: const EdgeInsets.fromLTRB(16, 18, 16, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SectionHeader(
            'Recent ${coinKey.tf} signals',
            subtitle: 'Newest first. Hit means the candle closed the way we said. '
                'Skip means the odds were too close, so we made no call.',
          ),
          const SizedBox(height: 14),
          if (history.isLoading && resolved.isEmpty)
            const SizedBox(height: 76, child: Center(child: CircularProgressIndicator(color: Tm.cyan)))
          else if (resolved.isEmpty)
            Text('No finished signals yet. They appear after each candle closes.',
                style: TmText.body(14, color: Tm.fg2))
          else ...[
            Wrap(spacing: 12, runSpacing: 12, children: [for (final item in resolved) _ResultTile(item: item)]),
            const SizedBox(height: 12),
            Text(
              '$hits of ${calls.length} calls correct${skipped > 0 ? ', $skipped skipped as Neutral' : ''}.',
              style: TmText.body(14, weight: FontWeight.w600, color: Tm.fg2),
            ),
          ],
        ],
      ),
    );
  }
}

class _ResultTile extends StatelessWidget {
  const _ResultTile({required this.item});
  final HistoryItem item;

  @override
  Widget build(BuildContext context) {
    final direction = directionOf(item.label);
    final (mark, color) = switch (item.correct) {
      null => ('Skip', Tm.neutral),
      true => ('Hit', Tm.up),
      false => ('Miss', Tm.downText),
    };
    return Semantics(
      label: '${formatDateTime(item.targetOpenTime)}: called ${directionWord[direction]}, '
          'went ${item.actualDirection ?? 'unknown'}. $mark.',
      excludeSemantics: true,
      child: SizedBox(
        width: 68,
        height: 76,
        child: Tile(
          padding: EdgeInsets.zero,
          borderColor: color.withValues(alpha: 0.4),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(directionIcon(direction), size: 22, color: directionColor(direction, text: true)),
              const SizedBox(height: 4),
              Text(mark, style: TmText.body(12, weight: FontWeight.w700, color: color)),
            ],
          ),
        ),
      ),
    );
  }
}

/// Recent headlines about the coin with a tone badge. Tapping one opens the publisher's
/// site in the phone's browser; the app never shows the article text itself.
class _NewsCard extends ConsumerWidget {
  const _NewsCard({required this.symbol, required this.coinName, required this.sentimentUsed});
  final String symbol, coinName;
  final bool sentimentUsed;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final news = ref.watch(newsProvider(symbol));
    return GlassCard(
      padding: const EdgeInsets.fromLTRB(16, 18, 16, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SectionHeader(
            'News tone for $coinName',
            subtitle: '$newsScale ${sentimentUsed ? newsBlended : newsContextOnly}',
          ),
          const SizedBox(height: 8),
          news.when(
            skipLoadingOnRefresh: true,
            skipLoadingOnReload: true,
            loading: () => const SizedBox(height: 80, child: Center(child: CircularProgressIndicator(color: Tm.cyan))),
            error: (error, _) => ErrorState(
              message: ErrorState.describe(error, 'Could not load the news.'),
              onRetry: () => ref.invalidate(newsProvider(symbol)),
            ),
            data: (items) => items.isEmpty
                ? Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: Text('No recent headlines mention $coinName.', style: TmText.body(14, color: Tm.fg2)),
                  )
                : Column(children: [for (final item in items) _NewsRow(item: item)]),
          ),
          const SizedBox(height: 8),
          Text(newsFootnote, style: TmText.body(12, color: Tm.muted2, height: 1.45)),
        ],
      ),
    );
  }
}

class _NewsRow extends StatelessWidget {
  const _NewsRow({required this.item});
  final NewsItem item;

  @override
  Widget build(BuildContext context) {
    final uri = Uri.tryParse(item.url);
    final safe = uri != null && (uri.scheme == 'https' || uri.scheme == 'http'); // never anything else
    final sentiment = item.sentiment;
    final direction = switch (sentiment?.label) {
      'bullish' => Direction.up,
      'bearish' => Direction.down,
      _ => Direction.neutral,
    };
    final word = switch (sentiment?.label) { 'bullish' => 'Bullish', 'bearish' => 'Bearish', _ => 'Neutral' };
    return Semantics(
      link: safe,
      child: InkWell(
        onTap: safe ? () => launchUrl(uri, mode: LaunchMode.externalApplication) : null,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: const BoxDecoration(border: Border(top: BorderSide(color: Color(0x14FFFFFF)))),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(item.title, style: TmText.body(14.5, weight: FontWeight.w600, height: 1.35)),
              const SizedBox(height: 6),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      '${item.sourceName} · ${formatAgo(item.publishedAt, DateTime.now().toUtc())}',
                      style: TmText.body(12, color: Tm.muted),
                    ),
                  ),
                  if (sentiment == null)
                    Text('Not rated yet', style: TmText.body(12, color: Tm.muted))
                  else
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: const Color(0x0DFFFFFF),
                        borderRadius: BorderRadius.circular(999),
                        border: Border.all(color: Tm.hairline),
                      ),
                      child: DirectionLabel(direction, word: word, trailing: formatScore(sentiment.score)),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
