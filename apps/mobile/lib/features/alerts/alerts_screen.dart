import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/format.dart';
import '../../core/signal_copy.dart';
import '../../data/api.dart';
import '../../data/models.dart';
import '../../data/providers.dart';
import '../../theme/tokens.dart';
import '../../widgets/glass.dart';
import '../../widgets/keycap.dart';
import '../../widgets/page.dart';
import '../../widgets/states.dart';

/// Alerts tab: the notifications that arrived, the person's rules, and a sheet to make a
/// new rule. The API decides what is valid and when a rule fires; this screen only shows it.
class AlertsScreen extends ConsumerWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionProvider);
    final signedIn = session.valueOrNull != null;

    return TmPage(
      header: const BrandBar(),
      onRefresh: () async {
        ref.invalidate(alertsProvider);
        ref.invalidate(notificationsProvider);
      },
      children: [
        Semantics(header: true, child: Text('Alerts', style: TmText.display(26))),
        const SizedBox(height: 4),
        Text('Get told when a signal changes or a price crosses a level.',
            style: TmText.body(14, color: Tm.fg3, height: 1.45)),
        const SizedBox(height: 14),
        if (session.isLoading)
          const Skeleton(height: 140)
        else if (!signedIn)
          EmptyState(
            title: 'Alerts need an account',
            text: 'Sign in to get a notification when a signal changes or a price crosses a level you choose. '
                'Signals stay public either way.',
            action: PrimaryButton(label: 'Sign in', onTap: () => context.push('/login')),
          )
        else ...[
          const _Notifications(),
          const SizedBox(height: 18),
          const _Rules(),
          const SizedBox(height: 16),
          Text(
            'Signal alerts are checked each time a candle closes. Price alerts are checked once a minute. '
            'Notifications appear here; phone push notifications come in a later update. $disclaimerShort',
            style: TmText.body(12.5, color: Tm.muted2, height: 1.5),
          ),
        ],
      ],
    );
  }
}

class _Notifications extends ConsumerWidget {
  const _Notifications();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifications = ref.watch(notificationsProvider);
    final unread = notifications.valueOrNull?.unread ?? 0;
    return GlassCard(
      padding: const EdgeInsets.fromLTRB(16, 18, 16, 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SectionHeader('Notifications', subtitle: unread > 0 ? '$unread new' : null),
          const SizedBox(height: 8),
          notifications.when(
            skipLoadingOnRefresh: true,
            skipLoadingOnReload: true,
            loading: () => const SizedBox(height: 70, child: Center(child: CircularProgressIndicator(color: Tm.cyan))),
            error: (error, _) => ErrorState(
              message: ErrorState.describe(error, 'Could not load your notifications.'),
              onRetry: () => ref.invalidate(notificationsProvider),
            ),
            data: (data) => data.items.isEmpty
                ? Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text('Nothing yet. When one of your alerts fires, it shows up here.',
                        style: TmText.body(14, color: Tm.fg2, height: 1.45)),
                  )
                : Column(children: [for (final item in data.items) _NotificationRow(item: item)]),
          ),
        ],
      ),
    );
  }
}

class _NotificationRow extends ConsumerWidget {
  const _NotificationRow({required this.item});
  final AppNotification item;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final unread = item.readAt == null;
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: const BoxDecoration(border: Border(top: BorderSide(color: Color(0x14FFFFFF)))),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (unread) ...[
                Container(
                  margin: const EdgeInsets.only(top: 2, right: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(color: const Color(0x264DD8FF), borderRadius: BorderRadius.circular(999)),
                  child: Text('New', style: TmText.body(12, weight: FontWeight.w700, color: Tm.cyan)),
                ),
              ],
              Expanded(child: Text(item.title, style: TmText.body(15, weight: FontWeight.w700, height: 1.3))),
            ],
          ),
          const SizedBox(height: 4),
          Text(item.body, style: TmText.body(13.5, color: Tm.fg2, height: 1.45)),
          const SizedBox(height: 6),
          Row(
            children: [
              Expanded(
                child: Text(formatAgo(item.createdAt, DateTime.now().toUtc()), style: TmText.body(12, color: Tm.muted)),
              ),
              if (unread)
                KeyButton(
                  onTap: () => ref.read(notificationsProvider.notifier).markRead(item.id),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [Icon(Icons.check_rounded, size: 18), SizedBox(width: 6), Text('Mark as read')],
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Rules extends ConsumerWidget {
  const _Rules();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alerts = ref.watch(alertsProvider);
    final data = alerts.valueOrNull;
    final full = data != null && data.items.length >= data.maxAlerts;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            const Expanded(child: SectionHeader('Your alerts')),
            if (data != null)
              Text('${data.items.length} of ${data.maxAlerts} used', style: TmText.body(13, color: Tm.muted)),
          ],
        ),
        const SizedBox(height: 12),
        alerts.when(
          skipLoadingOnRefresh: true,
          skipLoadingOnReload: true,
          loading: () => const Skeleton(height: 90),
          error: (error, _) => ErrorState(
            message: ErrorState.describe(error, 'Could not load your alerts.'),
            onRetry: () => ref.invalidate(alertsProvider),
          ),
          data: (d) => d.items.isEmpty
              ? const EmptyState(
                  title: 'No alerts yet',
                  text: 'Create your first alert with the button below.',
                )
              : Column(children: [
                  for (final rule in d.items) ...[_RuleCard(rule: rule), const SizedBox(height: 12)],
                ]),
        ),
        const SizedBox(height: 14),
        PrimaryButton(
          label: full ? 'Alert limit reached' : 'New alert',
          icon: Icons.add_rounded,
          onTap: full
              ? null
              : () => showModalBottomSheet<void>(
                    context: context,
                    isScrollControlled: true,
                    backgroundColor: const Color(0xFF0B1124),
                    shape: const RoundedRectangleBorder(
                      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                    ),
                    builder: (_) => const NewAlertSheet(),
                  ),
        ),
        if (full) ...[
          const SizedBox(height: 8),
          Text('Delete one to add another.', textAlign: TextAlign.center, style: TmText.body(13, color: Tm.neutral)),
        ],
      ],
    );
  }
}

class _RuleCard extends ConsumerStatefulWidget {
  const _RuleCard({required this.rule});
  final AlertRule rule;

  @override
  ConsumerState<_RuleCard> createState() => _RuleCardState();
}

class _RuleCardState extends ConsumerState<_RuleCard> {
  bool _busy = false;

  Future<void> _run(Future<void> Function() action) async {
    setState(() => _busy = true);
    final messenger = ScaffoldMessenger.of(context);
    try {
      await action();
    } on ApiException catch (e) {
      messenger.showSnackBar(SnackBar(content: Text(e.message)));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final rule = widget.rule;
    final sentence = ruleSentence(
        symbol: rule.symbol, type: rule.type, timeframe: rule.timeframe, threshold: rule.threshold);
    final fired = rule.lastTriggeredAt == null
        ? 'has not fired yet'
        : 'last fired ${formatDateTime(rule.lastTriggeredAt!)}';
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(sentence, style: TmText.body(15, weight: FontWeight.w700, height: 1.35)),
          const SizedBox(height: 4),
          Text(
            '${rule.active ? 'Active' : 'Paused'} · at most once every ${cooldownWords(rule.cooldownMinutes)} · $fired',
            style: TmText.body(13, color: Tm.muted, height: 1.4),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: KeyButton(
                  onTap: _busy
                      ? null
                      : () => _run(() => ref.read(alertsProvider.notifier).setActive(rule.id, active: !rule.active)),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(rule.active ? Icons.notifications_off_outlined : Icons.notifications_none_rounded, size: 18),
                      const SizedBox(width: 6),
                      Text(rule.active ? 'Pause' : 'Resume'),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: KeyButton(
                  onTap: _busy ? null : () => _run(() => ref.read(alertsProvider.notifier).delete(rule.id)),
                  semanticLabel: 'Delete alert: $sentence',
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [Icon(Icons.delete_outline_rounded, size: 18), SizedBox(width: 6), Text('Delete')],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// Bottom sheet: coin, what to watch for, candle size or level, and how often at most.
class NewAlertSheet extends ConsumerStatefulWidget {
  const NewAlertSheet({super.key});

  @override
  ConsumerState<NewAlertSheet> createState() => _NewAlertSheetState();
}

class _NewAlertSheetState extends ConsumerState<NewAlertSheet> {
  late String _symbol = ref.read(selectedSymbolProvider);
  String _type = 'signal_change';
  late String _tf = ref.read(selectedTimeframeProvider);
  int _cooldown = 60;
  final _level = TextEditingController();
  String? _problem;
  bool _busy = false;

  @override
  void dispose() {
    _level.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final parsed = parseThreshold(_type, _level.text);
    if (parsed.error != null) return setState(() => _problem = parsed.error);
    setState(() {
      _problem = null;
      _busy = true;
    });
    final navigator = Navigator.of(context);
    final messenger = ScaffoldMessenger.of(context);
    try {
      await ref.read(alertsProvider.notifier).create(
            symbol: _symbol,
            type: _type,
            timeframe: isSignalAlert(_type) ? _tf : null,
            threshold: parsed.threshold,
            cooldownMinutes: _cooldown,
          );
      navigator.pop();
      messenger.showSnackBar(const SnackBar(content: Text('Alert saved.')));
    } on ApiException catch (e) {
      // The API explains what it refused (for example the limit of alerts).
      if (mounted) setState(() => _problem = e.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final coins = ref.watch(marketsProvider).valueOrNull ?? const <MarketRow>[];
    final signal = isSignalAlert(_type);
    final needsLevel = _type != 'signal_change';
    DropdownMenuItem<T> item<T>(T value, String label) =>
        DropdownMenuItem(value: value, child: Text(label, overflow: TextOverflow.ellipsis));

    return Padding(
      // Lifts the sheet above the keyboard.
      padding: EdgeInsets.fromLTRB(20, 20, 20, 20 + MediaQuery.of(context).viewInsets.bottom),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('New alert', style: TmText.display(20)),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              initialValue: coins.any((c) => c.symbol == _symbol) ? _symbol : null,
              isExpanded: true,
              dropdownColor: const Color(0xFF111A33),
              decoration: const InputDecoration(labelText: 'Coin'),
              items: [for (final c in coins) item(c.symbol, '${c.name} (${c.symbol})')],
              onChanged: (v) => setState(() => _symbol = v ?? _symbol),
            ),
            const SizedBox(height: 14),
            DropdownButtonFormField<String>(
              initialValue: _type,
              isExpanded: true,
              dropdownColor: const Color(0xFF111A33),
              decoration: const InputDecoration(labelText: 'Tell me when'),
              items: [for (final e in alertTypeLabels.entries) item(e.key, e.value)],
              onChanged: (v) => setState(() {
                _type = v ?? _type;
                _level.clear();
                _problem = null;
              }),
            ),
            if (signal) ...[
              const SizedBox(height: 14),
              DropdownButtonFormField<String>(
                initialValue: _tf,
                dropdownColor: const Color(0xFF111A33),
                decoration: const InputDecoration(labelText: 'Candle size'),
                items: [for (final tf in timeframes) item(tf, tf)],
                onChanged: (v) => setState(() => _tf = v ?? _tf),
              ),
            ],
            if (needsLevel) ...[
              const SizedBox(height: 14),
              TextField(
                controller: _level,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                style: TmText.mono(16, weight: FontWeight.w600),
                decoration: InputDecoration(
                  labelText: signal ? 'Chance of Up (%)' : 'Price in USDT',
                  hintText: signal ? '60' : '85000',
                  helperMaxLines: 3,
                  helperText: signal
                      ? 'A number from 1 to 99. The chance of Down is 100 minus this.'
                      : 'You are notified when the price moves across this level, not while it stays beyond it.',
                ),
              ),
            ],
            const SizedBox(height: 14),
            DropdownButtonFormField<int>(
              initialValue: _cooldown,
              dropdownColor: const Color(0xFF111A33),
              decoration: const InputDecoration(labelText: 'At most once every'),
              items: [for (final m in const [15, 60, 240, 1440]) item(m, cooldownWords(m))],
              onChanged: (v) => setState(() => _cooldown = v ?? _cooldown),
            ),
            if (_problem != null) ...[
              const SizedBox(height: 12),
              Semantics(
                liveRegion: true,
                child: Text(_problem!, style: TmText.body(14, color: Tm.downText)),
              ),
            ],
            const SizedBox(height: 18),
            PrimaryButton(label: 'Save alert', busy: _busy, onTap: _save),
          ],
        ),
      ),
    );
  }
}
