import 'package:flutter/material.dart';

import '../theme/tokens.dart';

/// The frosted-glass panel (docs/08): a faint top-to-bottom gradient, a hairline border, a
/// lit top edge, and two shadows under it (a soft deep one and a hard 3 px one that makes
/// the card look like a slab with thickness).
///
/// No blur behind it: `BackdropFilter` is expensive on phones and these cards sit in
/// scrolling lists (docs/08, Flutter equivalents).
class GlassCard extends StatelessWidget {
  const GlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.margin = EdgeInsets.zero,
    this.tint,
    this.radius = Tm.rCard,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry margin;

  /// Signal color for the border and a soft glow at the top (the signal card).
  final Color? tint;
  final double radius;

  @override
  Widget build(BuildContext context) {
    final shape = BorderRadius.circular(radius);
    return Container(
      margin: margin,
      decoration: BoxDecoration(
        borderRadius: shape,
        boxShadow: const [
          BoxShadow(color: Color(0xBF000000), offset: Offset(0, 24), blurRadius: 40, spreadRadius: -20),
          BoxShadow(color: Color(0x59000000), offset: Offset(0, 3)),
        ],
      ),
      child: ClipRRect(
        borderRadius: shape,
        child: DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: shape,
            gradient: const LinearGradient(
              begin: Alignment(-0.4, -1),
              end: Alignment(0.4, 1),
              colors: [Color(0x13FFFFFF), Color(0x06FFFFFF)],
            ),
            border: Border.all(color: tint?.withValues(alpha: 0.45) ?? Tm.hairline),
          ),
          child: Stack(
            children: [
              if (tint != null)
                Positioned(
                  left: -40,
                  right: -40,
                  top: -90,
                  height: 260,
                  child: IgnorePointer(
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        gradient: RadialGradient(
                          colors: [tint!.withValues(alpha: 0.18), tint!.withValues(alpha: 0)],
                        ),
                      ),
                    ),
                  ),
                ),
              // The lit top edge: a thin line of light, brightest in the middle.
              const Positioned(
                left: 0,
                right: 0,
                top: 0,
                height: 1.2,
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Color(0x00FFFFFF), Color(0x3DFFFFFF), Color(0x00FFFFFF)],
                    ),
                  ),
                ),
              ),
              Padding(padding: padding, child: child),
            ],
          ),
        ),
      ),
    );
  }
}

/// A small raised tile (reason rows, stat tiles): same family as the glass card, flatter.
class Tile extends StatelessWidget {
  const Tile({super.key, required this.child, this.padding = const EdgeInsets.all(12), this.borderColor});

  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? borderColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(Tm.rTile),
        gradient: const LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0x1AFFFFFF), Color(0x08FFFFFF)],
        ),
        border: Border.all(color: borderColor ?? const Color(0x1FFFFFFF)),
        boxShadow: const [BoxShadow(color: Color(0x73000000), offset: Offset(0, 3))],
      ),
      child: child,
    );
  }
}
