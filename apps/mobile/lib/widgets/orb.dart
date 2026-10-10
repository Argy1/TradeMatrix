import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../core/format.dart';
import '../core/signal_copy.dart';
import '../theme/tokens.dart';

/// Colors of the 3D orb per direction (docs/08): bright body color, deep body color, glow.
const _orbColors = {
  Direction.up: (Color(0xFF34F0B0), Color(0xFF0A6E53), Color(0x8C2EE6A6)),
  Direction.down: (Color(0xFFFF7E96), Color(0xFF8C1B38), Color(0x80FF5C7A)),
  Direction.neutral: (Color(0xFFFFD98A), Color(0xFF8A5F0E), Color(0x73FFC857)),
};

/// The hero of the app: a glowing 3D sphere with the direction word and the probability on
/// it, inside a ring that is filled as far as the probability goes.
///
/// The sphere is painted, not an image: a body gradient lit from the top left, a dark
/// lower-right side, a light rim, a small white highlight, and a glow on the "floor".
/// It bobs 5 px over 5 seconds, and stands still when the phone asks for reduced motion.
class SignalOrb extends StatefulWidget {
  const SignalOrb({super.key, required this.direction, required this.probability, this.size = 176});

  final Direction direction;

  /// The number shown: P(up) for Up and Neutral, P(down) for Down.
  final double probability;
  final double size;

  @override
  State<SignalOrb> createState() => _SignalOrbState();
}

class _SignalOrbState extends State<SignalOrb> with SingleTickerProviderStateMixin {
  late final AnimationController _bob =
      AnimationController(vsync: this, duration: const Duration(milliseconds: 2500));

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // "Remove animations" in the phone's accessibility settings: keep the orb still.
    if (MediaQuery.of(context).disableAnimations) {
      _bob.stop();
    } else if (!_bob.isAnimating) {
      _bob.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _bob.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final (bright, deep, glow) = _orbColors[widget.direction]!;
    final ringColor = switch (widget.direction) {
      Direction.up => Tm.up,
      Direction.down => Tm.down,
      Direction.neutral => Tm.neutral,
    };
    final size = widget.size;
    final scale = size / 176;
    final orb = 124 * scale;
    return ExcludeSemantics(
      // The signal card reads the whole signal as one sentence instead.
      child: RepaintBoundary(
        child: SizedBox(
          width: size,
          height: size,
          child: Stack(
            alignment: Alignment.center,
            children: [
              CustomPaint(
                size: Size.square(size),
                painter: _RingPainter(widget.probability, ringColor, 11 * scale),
              ),
              Positioned(
                bottom: -2,
                child: CustomPaint(size: Size(120 * scale, 16 * scale), painter: _FloorGlowPainter(glow)),
              ),
              AnimatedBuilder(
                animation: _bob,
                builder: (context, child) => Transform.translate(
                  offset: Offset(0, -5 * Curves.easeInOut.transform(_bob.value)),
                  child: child,
                ),
                child: CustomPaint(size: Size.square(orb), painter: _SpherePainter(bright, deep, glow)),
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    orbWord[widget.direction]!,
                    style: TmText.display(
                      (widget.direction == Direction.neutral ? 22 : 32) * scale,
                      weight: FontWeight.w800,
                      color: Colors.white,
                      spacing: 0.6,
                    ).copyWith(shadows: const [Shadow(color: Color(0x8C000000), blurRadius: 10, offset: Offset(0, 2))]),
                  ),
                  Text(
                    formatProbability(widget.probability),
                    style: TmText.mono(19 * scale, color: Colors.white)
                        .copyWith(shadows: const [Shadow(color: Color(0x8C000000), blurRadius: 10, offset: Offset(0, 2))]),
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

/// The probability ring: a faint full circle and a colored arc from 12 o'clock, clockwise.
class _RingPainter extends CustomPainter {
  _RingPainter(this.probability, this.color, this.width);
  final double probability, width;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = (Offset.zero & size).deflate(width / 2);
    final track = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = width
      ..color = const Color(0x17FFFFFF);
    canvas.drawArc(rect, 0, math.pi * 2, false, track);
    final arc = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = width
      ..strokeCap = StrokeCap.round
      ..color = color;
    canvas.drawArc(rect, -math.pi / 2, math.pi * 2 * probability.clamp(0.0, 1.0), false, arc);
  }

  @override
  bool shouldRepaint(_RingPainter old) =>
      old.probability != probability || old.color != color || old.width != width;
}

class _FloorGlowPainter extends CustomPainter {
  _FloorGlowPainter(this.glow);
  final Color glow;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = glow.withValues(alpha: 0.5)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);
    canvas.drawOval(Offset.zero & size, paint);
  }

  @override
  bool shouldRepaint(_FloorGlowPainter old) => old.glow != glow;
}

class _SpherePainter extends CustomPainter {
  _SpherePainter(this.bright, this.deep, this.glow);
  final Color bright, deep, glow;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    final center = rect.center;
    final r = size.width / 2;

    // 1. Glow around the sphere.
    canvas.drawCircle(center, r * 0.96, Paint()
      ..color = glow
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 18));

    // 2. Body: lit from the top left, falling to near-black at the lower right edge.
    canvas.drawCircle(
      center,
      r,
      Paint()
        ..shader = RadialGradient(
          center: const Alignment(-0.28, -0.40),
          radius: 0.95,
          colors: [bright, deep, const Color(0xFF03050B)],
          stops: const [0, 0.68, 1],
        ).createShader(rect),
    );

    // 3. Shade on the lower right (the web version's dark inner shadow).
    canvas.drawCircle(
      center,
      r,
      Paint()
        ..shader = const RadialGradient(
          center: Alignment(-0.30, -0.36),
          radius: 1.05,
          colors: [Color(0x00000000), Color(0x00000000), Color(0x8C000000)],
          stops: [0, 0.60, 1],
        ).createShader(rect),
    );

    // 4. A thin light rim on the upper left edge.
    canvas.drawCircle(
      center,
      r,
      Paint()
        ..shader = const RadialGradient(
          center: Alignment(0.36, 0.44),
          radius: 1.12,
          colors: [Color(0x00FFFFFF), Color(0x00FFFFFF), Color(0x38FFFFFF)],
          stops: [0, 0.80, 1],
        ).createShader(rect),
    );

    // 5. The small white highlight that makes it read as glossy.
    final spot = Offset(center.dx - r * 0.36, center.dy - r * 0.48);
    canvas.drawCircle(
      spot,
      r * 0.30,
      Paint()
        ..shader = const RadialGradient(colors: [Color(0xE6FFFFFF), Color(0x00FFFFFF)])
            .createShader(Rect.fromCircle(center: spot, radius: r * 0.30)),
    );
  }

  @override
  bool shouldRepaint(_SpherePainter old) => old.bright != bright || old.deep != deep || old.glow != glow;
}
