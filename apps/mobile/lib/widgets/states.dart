import 'package:flutter/material.dart';

import '../data/api.dart';
import '../theme/tokens.dart';
import 'glass.dart';
import 'keycap.dart';

/// Loading placeholder: a glass block that pulses gently (docs/08 "Loading"). It stays
/// still when the phone asks for reduced motion.
class Skeleton extends StatefulWidget {
  const Skeleton({super.key, this.height = 120});
  final double height;

  @override
  State<Skeleton> createState() => _SkeletonState();
}

class _SkeletonState extends State<Skeleton> with SingleTickerProviderStateMixin {
  late final AnimationController _pulse =
      AnimationController(vsync: this, duration: const Duration(milliseconds: 1100));

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.of(context).disableAnimations) {
      _pulse.value = 0.5;
    } else if (!_pulse.isAnimating) {
      _pulse.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Loading',
      child: FadeTransition(
        opacity: Tween(begin: 0.45, end: 1.0).animate(_pulse),
        child: GlassCard(padding: EdgeInsets.zero, child: SizedBox(height: widget.height, width: double.infinity)),
      ),
    );
  }
}

/// A plain message and a retry button (docs/08 "Error / offline").
class ErrorState extends StatelessWidget {
  const ErrorState({super.key, required this.message, this.onRetry});
  final String message;
  final VoidCallback? onRetry;

  /// The words for an error from a provider: the API's own message when there is one.
  static String describe(Object error, String fallback) {
    if (error is ApiException) {
      return error.status == null ? 'No connection. Check your internet and try again.' : fallback;
    }
    return fallback;
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      liveRegion: true,
      child: GlassCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(message, style: TmText.body(15, color: Tm.fg2, height: 1.45)),
            if (onRetry != null) ...[
              const SizedBox(height: 12),
              KeyButton(
                onTap: onRetry,
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [Icon(Icons.refresh_rounded, size: 18), SizedBox(width: 8), Text('Try again')],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// A short explanation and one clear button (docs/08 "Empty").
class EmptyState extends StatelessWidget {
  const EmptyState({super.key, required this.title, required this.text, this.action});
  final String title, text;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TmText.display(17)),
          const SizedBox(height: 6),
          Text(text, style: TmText.body(14.5, color: Tm.fg2, height: 1.5)),
          if (action != null) ...[const SizedBox(height: 16), action!],
        ],
      ),
    );
  }
}

/// Amber notice: stale data, a model below its baseline, or the disclaimer box.
class Notice extends StatelessWidget {
  const Notice({super.key, required this.child, this.icon = Icons.warning_amber_rounded});
  final Widget child;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0x14FFC857),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0x47FFC857)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: Tm.neutral),
          const SizedBox(width: 10),
          Expanded(
            child: DefaultTextStyle.merge(
              style: TmText.body(13, color: const Color(0xFFE7D9B5), height: 1.5),
              child: child,
            ),
          ),
        ],
      ),
    );
  }
}

/// Card heading with an optional one-line explanation under it.
class SectionHeader extends StatelessWidget {
  const SectionHeader(this.title, {super.key, this.subtitle});
  final String title;
  final String? subtitle;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Semantics(header: true, child: Text(title, style: TmText.display(19))),
        if (subtitle != null) ...[
          const SizedBox(height: 4),
          Text(subtitle!, style: TmText.body(13, color: Tm.muted, height: 1.45)),
        ],
      ],
    );
  }
}
