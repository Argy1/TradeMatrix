import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/tokens.dart';

/// The logo mark (docs/08 block 5): a rounded square with a cyan-to-violet gradient, a
/// faint grid on it (the "matrix") and a hard violet edge below, so it looks extruded.
class Logo3D extends StatelessWidget {
  const Logo3D({super.key, this.size = 36});
  final double size;

  @override
  Widget build(BuildContext context) {
    final radius = BorderRadius.circular(size * 0.30);
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        borderRadius: radius,
        boxShadow: [
          BoxShadow(color: const Color(0xFF3B2FA8), offset: Offset(0, size / 12)),
          BoxShadow(color: const Color(0x807C5CFF), offset: Offset(0, size * 0.28), blurRadius: size / 2),
        ],
      ),
      child: ClipRRect(
        borderRadius: radius,
        child: CustomPaint(painter: _LogoPainter(), size: Size.square(size)),
      ),
    );
  }
}

class _LogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    canvas.drawRect(
      rect,
      Paint()
        ..shader = const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF6AE4FF), Tm.violet],
        ).createShader(rect),
    );
    final grid = Paint()
      ..color = const Color(0x61FFFFFF)
      ..strokeWidth = 1;
    final step = size.width / 4;
    for (var i = 0; i <= 4; i++) {
      canvas.drawLine(Offset(i * step, 0), Offset(i * step, size.height), grid);
      canvas.drawLine(Offset(0, i * step), Offset(size.width, i * step), grid);
    }
    // Light catching the top edge.
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, 2), Paint()..color = const Color(0x8CFFFFFF));
  }

  @override
  bool shouldRepaint(_LogoPainter old) => false;
}

/// Logo + "TradeMatrix AI" + "Created by Argy". This lockup is the brand (CLAUDE.md): it
/// appears in the app bar, on the splash screen and on the About screen.
class BrandLockup extends StatelessWidget {
  const BrandLockup({super.key, this.logoSize = 36, this.nameSize = 17});
  final double logoSize, nameSize;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'TradeMatrix AI, created by Argy',
      excludeSemantics: true,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Logo3D(size: logoSize),
          SizedBox(width: logoSize * 0.28),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text.rich(
                TextSpan(
                  text: 'TradeMatrix ',
                  children: [TextSpan(text: 'AI', style: TextStyle(color: Tm.cyan))],
                ),
                style: TmText.display(nameSize, height: 1.15),
              ),
              Text('Created by Argy', style: TmText.body(12, color: Tm.muted, spacing: 0.5, height: 1.2)),
            ],
          ),
        ],
      ),
    );
  }
}

/// The isometric candle scene (docs/08 block 4), painted: a glowing floor tile, five solid
/// candles drawn as boxes with a light, a mid and a dark face, and one dashed see-through
/// "ghost" candle for the next move. Decoration only, so it is static and cheap to draw.
class IsoCandleScene extends StatelessWidget {
  const IsoCandleScene({super.key, this.height = 170});
  final double height;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      image: true,
      label: 'Decorative 3D chart: five candles and a dashed outline for the next one',
      child: RepaintBoundary(
        child: CustomPaint(size: Size(double.infinity, height), painter: _IsoPainter()),
      ),
    );
  }
}

class _IsoPainter extends CustomPainter {
  // (height, rising?) of the five solid candles, left to right.
  static const _candles = [(46.0, true), (30.0, false), (58.0, true), (40.0, false), (72.0, true)];

  @override
  void paint(Canvas canvas, Size size) {
    const cos30 = 0.8660254, sin30 = 0.5;
    final unit = math.min(size.width / 9.6, size.height / 6.4);
    final origin = Offset(size.width / 2, size.height * 0.58);

    // Isometric projection: x runs down-right, y runs down-left, z goes straight up.
    Offset at(double x, double y, [double z = 0]) =>
        origin + Offset((x - y) * cos30 * unit, (x + y) * sin30 * unit - z);

    Path quad(Offset a, Offset b, Offset c, Offset d) => Path()
      ..moveTo(a.dx, a.dy)
      ..lineTo(b.dx, b.dy)
      ..lineTo(c.dx, c.dy)
      ..lineTo(d.dx, d.dy)
      ..close();

    // Floor tile with a soft cyan glow and a grid.
    final floor = quad(at(-3.6, -1.4), at(3.6, -1.4), at(3.6, 1.4), at(-3.6, 1.4));
    canvas.drawPath(floor, Paint()
      ..color = const Color(0x334DD8FF)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 16));
    canvas.drawPath(floor, Paint()..color = const Color(0x14FFFFFF));
    final grid = Paint()
      ..color = const Color(0x2E4DD8FF)
      ..strokeWidth = 1;
    for (var x = -3.6; x <= 3.61; x += 1.2) {
      canvas.drawLine(at(x, -1.4), at(x, 1.4), grid);
    }
    for (var y = -1.4; y <= 1.41; y += 0.7) {
      canvas.drawLine(at(-3.6, y), at(3.6, y), grid);
    }

    void box(double x, double h, Color color, {bool ghost = false}) {
      const w = 0.34; // half width of a candle
      final top = quad(at(x - w, -w, h), at(x + w, -w, h), at(x + w, w, h), at(x - w, w, h));
      final front = quad(at(x - w, w, h), at(x + w, w, h), at(x + w, w), at(x - w, w));
      final side = quad(at(x + w, -w, h), at(x + w, w, h), at(x + w, w), at(x + w, -w));
      if (ghost) {
        // The predicted candle: a tinted, dashed outline instead of a solid body.
        final tint = Paint()..color = color.withValues(alpha: 0.16);
        final line = Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.6
          ..color = color;
        for (final face in [side, front, top]) {
          canvas.drawPath(face, tint);
          canvas.drawPath(_dashed(face), line);
        }
        return;
      }
      canvas.drawPath(front, Paint()
        ..color = color.withValues(alpha: 0.35)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 10));
      canvas.drawPath(side, Paint()..color = Color.lerp(color, Colors.black, 0.45)!);
      canvas.drawPath(front, Paint()..color = Color.lerp(color, Colors.black, 0.18)!);
      canvas.drawPath(top, Paint()..color = Color.lerp(color, Colors.white, 0.35)!);
    }

    // Drawn left to right, which is also back to front in this projection.
    for (var i = 0; i < _candles.length; i++) {
      final (h, rising) = _candles[i];
      box(-3.0 + i * 1.2, h * unit / 26, rising ? Tm.up : Tm.down);
    }
    box(3.0, 84 * unit / 26, Tm.up, ghost: true);
  }

  /// Cut a path into short dashes (Flutter has no dashed stroke of its own).
  Path _dashed(Path source) {
    final out = Path();
    for (final metric in source.computeMetrics()) {
      for (var d = 0.0; d < metric.length; d += 8) {
        out.addPath(metric.extractPath(d, math.min(d + 5, metric.length)), Offset.zero);
      }
    }
    return out;
  }

  @override
  bool shouldRepaint(_IsoPainter old) => false;
}
