import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/providers.dart';
import '../theme/tokens.dart';
import 'background.dart';
import 'brand.dart';
import 'keycap.dart';

/// The frame of every screen: space background, safe area and one scrolling column.
/// `onRefresh` adds pull-to-refresh.
class TmPage extends StatelessWidget {
  const TmPage({
    super.key,
    required this.children,
    this.header,
    this.onRefresh,
    this.padding = const EdgeInsets.fromLTRB(16, 4, 16, 28),
    this.grid = false,
  });

  final List<Widget> children;
  final Widget? header;
  final Future<void> Function()? onRefresh;
  final EdgeInsets padding;
  final bool grid;

  @override
  Widget build(BuildContext context) {
    Widget list = ListView(padding: padding, children: children);
    if (onRefresh != null) {
      list = RefreshIndicator(onRefresh: onRefresh!, color: Tm.cyan, backgroundColor: const Color(0xFF101830), child: list);
    }
    return Scaffold(
      backgroundColor: Tm.ink,
      body: SpaceBackground(
        grid: grid,
        child: SafeArea(
          bottom: false,
          child: Column(children: [?header, Expanded(child: list)]),
        ),
      ),
    );
  }
}

/// App bar of the tab screens: the brand lockup on the left, the bell on the right with a
/// dot when there are unread notifications.
class BrandBar extends ConsumerWidget {
  const BrandBar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final unread = ref.watch(notificationsProvider).valueOrNull?.unread ?? 0;
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 14, 20, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Shrinks as one piece when the phone's text size is turned up, so the bell stays.
          const Flexible(
            child: FittedBox(fit: BoxFit.scaleDown, alignment: Alignment.centerLeft, child: BrandLockup()),
          ),
          const SizedBox(width: 12),
          KeyButton(
            onTap: () => context.go('/alerts'),
            padding: EdgeInsets.zero,
            semanticLabel: unread > 0 ? 'Notifications, $unread unread' : 'Notifications',
            child: Stack(
              clipBehavior: Clip.none,
              children: [
                const Icon(Icons.notifications_none_rounded),
                if (unread > 0)
                  Positioned(
                    right: -2,
                    top: -2,
                    child: Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                        color: Tm.cyan,
                        shape: BoxShape.circle,
                        border: Border.all(color: Tm.ink, width: 1.5),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// App bar of a pushed screen: a back key, a title and an optional line under it.
class BackBar extends StatelessWidget {
  const BackBar({super.key, required this.title, this.subtitle, this.trailing});
  final String title;
  final String? subtitle;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 10),
      child: Row(
        children: [
          KeyButton(
            onTap: () => context.canPop() ? context.pop() : context.go('/signals'),
            padding: EdgeInsets.zero,
            semanticLabel: 'Back',
            child: const Icon(Icons.chevron_left_rounded, size: 26),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Semantics(
                  header: true,
                  child: Text(title, overflow: TextOverflow.ellipsis, style: TmText.display(18, height: 1.2)),
                ),
                if (subtitle != null)
                  FittedBox(
                    fit: BoxFit.scaleDown,
                    alignment: Alignment.centerLeft,
                    child: Text(subtitle!, maxLines: 1, style: TmText.body(12, color: Tm.muted, height: 1.2)),
                  ),
              ],
            ),
          ),
          if (trailing != null) ...[const SizedBox(width: 10), trailing!],
        ],
      ),
    );
  }
}
