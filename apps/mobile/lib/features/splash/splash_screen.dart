import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../theme/tokens.dart';
import '../../widgets/background.dart';
import '../../widgets/brand.dart';

/// Splash: the brand lockup over the perspective floor grid, then on to the signals.
/// "TradeMatrix AI" and "Created by Argy" are shown here by the brand rule in CLAUDE.md.
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _rise =
      AnimationController(vsync: this, duration: const Duration(milliseconds: 700));
  Timer? _leave;

  @override
  void initState() {
    super.initState();
    _rise.forward();
    _leave = Timer(const Duration(milliseconds: 1500), () {
      if (mounted) context.go('/signals');
    });
  }

  @override
  void dispose() {
    _leave?.cancel();
    _rise.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final still = MediaQuery.of(context).disableAnimations;
    final lockup = Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Logo3D(size: 84),
        const SizedBox(height: 26),
        Text.rich(
          const TextSpan(text: 'TradeMatrix ', children: [TextSpan(text: 'AI', style: TextStyle(color: Tm.cyan))]),
          style: TmText.display(30, weight: FontWeight.w800),
        ),
        const SizedBox(height: 6),
        Text('Created by Argy', style: TmText.body(14, color: Tm.muted, spacing: 0.6)),
        const SizedBox(height: 22),
        Text('Crypto signals in plain language', style: TmText.body(14, color: Tm.fg3)),
      ],
    );
    return Scaffold(
      backgroundColor: Tm.ink,
      body: SpaceBackground(
        child: Stack(
          children: [
            // The floor the logo stands on: the grid runs away from the viewer.
            const Positioned(left: 0, right: 0, bottom: 0, height: 360, child: FloorGrid()),
            Center(
              child: Semantics(
                label: 'TradeMatrix AI, created by Argy',
                excludeSemantics: true,
                child: still
                    ? lockup
                    : FadeTransition(
                        opacity: _rise,
                        child: SlideTransition(
                          position: Tween(begin: const Offset(0, 0.06), end: Offset.zero)
                              .animate(CurvedAnimation(parent: _rise, curve: Curves.easeOut)),
                          child: lockup,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
