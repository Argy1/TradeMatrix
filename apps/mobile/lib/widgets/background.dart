import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/tokens.dart';

/// The page background (docs/08): deep navy with a violet glow at the top right and a cyan
/// glow at the top left. Painted once and cached, because it never changes.
class SpaceBackground extends StatelessWidget {
  const SpaceBackground({super.key, required this.child, this.grid = false});

  final Widget child;

  /// Adds the perspective floor grid along the bottom of the page (sign-in).
  final bool grid;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: Tm.ink,
      child: Stack(
        children: [
          const Positioned.fill(child: RepaintBoundary(child: CustomPaint(painter: _GlowPainter()))),
          if (grid) const Positioned(left: 0, right: 0, bottom: 0, height: 320, child: FloorGrid()),
          child,
        ],
      ),
    );
  }
}

class _GlowPainter extends CustomPainter {
  const _GlowPainter();

  @override
  void paint(Canvas canvas, Size size) {
    void glow(Offset center, Size radii, Color color) {
      final rect = Rect.fromCenter(center: center, width: radii.width * 2, height: radii.height * 2);
      canvas.drawOval(
        rect,
        Paint()
          ..shader = RadialGradient(
            colors: [color, color.withValues(alpha: 0)],
            stops: const [0, 0.62],
          ).createShader(rect),
      );
    }

    glow(Offset(size.width * 0.9, -34), const Size(420, 300), Tm.glowViolet);
    glow(Offset(0, 68), const Size(360, 260), Tm.glowCyan);
  }

  @override
  bool shouldRepaint(_GlowPainter old) => false;
}

/// The perspective floor grid (docs/08 block 3): cyan lines on a floor that runs away from
/// the viewer. The lines "into the distance" all meet at one vanishing point, and the lines
/// across get closer together toward the horizon. That is all perspective is, so it is
/// simply painted that way; no 3D transform is needed.
class FloorGrid extends StatelessWidget {
  const FloorGrid({super.key});

  @override
  Widget build(BuildContext context) {
    return const IgnorePointer(
      child: ExcludeSemantics(
        child: RepaintBoundary(child: CustomPaint(painter: _FloorPainter(), size: Size.infinite)),
      ),
    );
  }
}

class _FloorPainter extends CustomPainter {
  const _FloorPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final horizon = size.height * 0.12;
    final floor = Rect.fromLTRB(0, horizon, size.width, size.height);
    final line = Paint()
      ..strokeWidth = 1
      // Bright near the viewer, fading to nothing at the horizon.
      ..shader = const LinearGradient(
        begin: Alignment.bottomCenter,
        end: Alignment.topCenter,
        colors: [Color(0x524DD8FF), Color(0x004DD8FF)],
      ).createShader(floor);
    final vanish = Offset(size.width / 2, horizon);
    for (var i = -12; i <= 12; i++) {
      canvas.drawLine(Offset(size.width / 2 + i * 72.0, size.height), vanish, line);
    }
    for (var k = 0; k < 11; k++) {
      final y = horizon + floor.height * math.pow(0.74, k);
      canvas.drawLine(Offset(0, y), Offset(size.width, y), line);
    }
  }

  @override
  bool shouldRepaint(_FloorPainter old) => false;
}
