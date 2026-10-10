import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../config.dart';
import '../../core/signal_copy.dart';
import '../../data/providers.dart';
import '../../theme/tokens.dart';
import '../../widgets/glass.dart';
import '../../widgets/keycap.dart';
import '../../widgets/page.dart';
import '../markets/markets_screen.dart';

/// More tab: the account, the track record, and how the app works.
class MoreScreen extends ConsumerWidget {
  const MoreScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionProvider).valueOrNull;
    return TmPage(
      header: const BrandBar(),
      children: [
        Semantics(header: true, child: Text('More', style: TmText.display(26))),
        const SizedBox(height: 14),
        GlassCard(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Account', style: TmText.display(18)),
              const SizedBox(height: 8),
              if (session != null) ...[
                Text('Signed in as', style: TmText.body(13, color: Tm.muted)),
                Text(session.user.email ?? 'your account', style: TmText.body(15, weight: FontWeight.w600)),
                const SizedBox(height: 14),
                KeyButton(
                  onTap: () => Supabase.instance.client.auth.signOut(),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [Icon(Icons.logout_rounded, size: 18), SizedBox(width: 8), Text('Sign out')],
                  ),
                ),
              ] else if (AppConfig.authConfigured) ...[
                Text(
                  'Sign in to keep a watchlist and get alerts. Signals stay public either way.',
                  style: TmText.body(14, color: Tm.fg2, height: 1.5),
                ),
                const SizedBox(height: 14),
                PrimaryButton(label: 'Sign in or create a free account', onTap: () => context.push('/login')),
              ] else
                Text(
                  'Sign-in is not set up in this build. Every signal, the chart and the track record still work.',
                  style: TmText.body(14, color: Tm.fg2, height: 1.5),
                ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        _Link(
          icon: Icons.fact_check_outlined,
          title: 'Track record',
          text: 'How often past signals were right, next to a simple baseline.',
          onTap: () => context.go('/more/track-record'),
        ),
        const SizedBox(height: 12),
        _Link(
          icon: Icons.help_outline_rounded,
          title: 'How it works',
          text: 'What a signal is, how it is made, and what we never do.',
          onTap: () => context.go('/more/about'),
        ),
        const SizedBox(height: 18),
        const TrackStrip(),
        const SizedBox(height: 16),
        Text(disclaimer, style: TmText.body(12.5, color: Tm.muted2, height: 1.5)),
      ],
    );
  }
}

class _Link extends StatelessWidget {
  const _Link({required this.icon, required this.title, required this.text, required this.onTap});
  final IconData icon;
  final String title, text;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: GlassCard(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Tile(padding: const EdgeInsets.all(10), child: Icon(icon, color: Tm.cyanLight, size: 24)),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: TmText.display(16)),
                    const SizedBox(height: 2),
                    Text(text, style: TmText.body(13, color: Tm.muted, height: 1.4)),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded, color: Tm.muted),
            ],
          ),
        ),
      ),
    );
  }
}
