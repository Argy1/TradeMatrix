import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../theme/tokens.dart';

const _tabs = [
  (Icons.bar_chart_rounded, 'Markets'),
  (Icons.arrow_circle_up_rounded, 'Signals'),
  (Icons.star_border_rounded, 'Watchlist'),
  (Icons.notifications_none_rounded, 'Alerts'),
  (Icons.more_horiz_rounded, 'More'),
];

/// The frame around the five tabs. Each tab keeps its own place (scroll position, the page
/// it was on) while the person visits another one.
class AppShell extends StatelessWidget {
  const AppShell({super.key, required this.shell});
  final StatefulNavigationShell shell;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Tm.ink,
      body: shell,
      bottomNavigationBar: _TabBar(
        index: shell.currentIndex,
        // Tapping the tab you are on takes it back to its first page.
        onTap: (i) =>
            shell.goBranch(i, initialLocation: i == shell.currentIndex),
      ),
    );
  }
}

/// Bottom tab bar (docs/08): icon plus a visible 12 px label, 56 px touch targets, and the
/// current tab shown by a cyan pill behind it as well as by its color.
class _TabBar extends StatelessWidget {
  const _TabBar({required this.index, required this.onTap});
  final int index;
  final ValueChanged<int> onTap;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xD90A1020), Color(0xFA060913)],
        ),
        border: Border(top: BorderSide(color: Tm.hairline)),
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(8, 8, 8, 8),
          child: Row(
            children: [
              for (var i = 0; i < _tabs.length; i++)
                Expanded(
                  child: Semantics(
                    button: true,
                    selected: i == index,
                    label: '${_tabs[i].$2} tab',
                    excludeSemantics: true,
                    child: GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: () => onTap(i),
                      child: Container(
                        // A fixed height: a bottom bar is offered the whole screen, and a
                        // Column would happily take all of it.
                        height: 56,
                        margin: const EdgeInsets.symmetric(horizontal: 2),
                        decoration: BoxDecoration(
                          color: i == index ? const Color(0x1F4DD8FF) : null,
                          borderRadius: BorderRadius.circular(14),
                        ),
                        // Scales the icon and label down together if large text is switched on,
                        // so the label is never cut off.
                        child: FittedBox(
                          fit: BoxFit.scaleDown,
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                _tabs[i].$1,
                                size: 24,
                                color: i == index ? Tm.cyanLight : Tm.muted,
                              ),
                              const SizedBox(height: 3),
                              Text(
                                _tabs[i].$2,
                                maxLines: 1,
                                overflow: TextOverflow.fade,
                                softWrap: false,
                                style: TmText.body(
                                  12,
                                  weight: i == index
                                      ? FontWeight.w700
                                      : FontWeight.w600,
                                  color: i == index ? Tm.cyanLight : Tm.muted,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
