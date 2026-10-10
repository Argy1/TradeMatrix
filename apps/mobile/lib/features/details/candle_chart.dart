import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../core/format.dart';
import '../../core/signal_copy.dart';
import '../../data/models.dart';
import '../../theme/tokens.dart';
import '../../widgets/direction.dart';
import '../../widgets/keycap.dart';

/// Width kept free on the right of the candles for the last-price tag, so the tag never
/// covers the newest candles (the ones a person looks at most).
const kPriceAxis = 58.0;

/// What the NEXT column shows: the signal for the candle that has not started yet.
class NextSignal {
  const NextSignal({required this.direction, required this.probability, this.degraded = false});
  final Direction direction;
  final double probability; // the number on the orb
  final bool degraded;
}

/// The price chart (docs/08 "Chart"), painted by hand so it matches the design exactly:
/// glowing candles with a lit left edge, volume bars, the EMA 9 / 21 / 50 lines sent by
/// the API, a dashed last-price line with a white price tag, relative time labels and the
/// dashed NEXT column on the right.
///
/// Drag sideways to look back in time, use - / + to see more or fewer candles, and press
/// and hold a candle to read its open, high, low and close.
class CandleChart extends StatefulWidget {
  const CandleChart({super.key, required this.candles, required this.timeframe, this.next, this.height = 230});

  final List<Candle> candles;
  final String timeframe;
  final NextSignal? next;
  final double height;

  @override
  State<CandleChart> createState() => _CandleChartState();
}

class _CandleChartState extends State<CandleChart> {
  static const _zoomLevels = [24, 36, 60, 96, 160];
  int _zoom = 1; // 36 candles, as in the design
  double _offset = 0; // candles hidden on the right (0 = the newest candle is visible)
  int? _focus; // index of the candle under the finger

  int get _visible => math.min(_zoomLevels[_zoom], widget.candles.length);
  double get _maxOffset => math.max(0, widget.candles.length - _visible).toDouble();

  void _setZoom(int next) => setState(() {
        _zoom = next.clamp(0, _zoomLevels.length - 1);
        _offset = _offset.clamp(0, _maxOffset);
        _focus = null;
      });

  @override
  void didUpdateWidget(CandleChart old) {
    super.didUpdateWidget(old);
    _offset = _offset.clamp(0, _maxOffset);
  }

  @override
  Widget build(BuildContext context) {
    final all = widget.candles;
    if (all.isEmpty) return SizedBox(height: widget.height);
    final end = all.length - _offset.round();
    final start = math.max(0, end - _visible);
    final window = all.sublist(start, end);
    final atNewest = _offset.round() == 0;
    final focused = _focus != null && _focus! < window.length ? window[_focus!] : null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SizedBox(
          height: 18,
          child: focused == null
              ? Text('Drag to look back · hold a candle for its prices',
                  style: TmText.body(12, color: Tm.muted2))
              : Text(
                  '${formatDateTime(focused.t)}  O ${formatPrice(focused.o, dollar: false)}  '
                  'H ${formatPrice(focused.h, dollar: false)}  L ${formatPrice(focused.l, dollar: false)}  '
                  'C ${formatPrice(focused.c, dollar: false)}',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TmText.mono(11, weight: FontWeight.w600, color: Tm.fg2),
                ),
        ),
        const SizedBox(height: 6),
        LayoutBuilder(
          builder: (context, box) {
            // The plot keeps 84% of the width; the NEXT column takes the rest (design canvas).
            final nextWidth = atNewest && widget.next != null ? box.maxWidth * 0.14 : 0.0;
            final plotWidth = box.maxWidth - nextWidth - (nextWidth > 0 ? 6 : 0);
            final slot = (plotWidth - kPriceAxis) / window.length;

            int indexAt(double x) => (x / slot).floor().clamp(0, window.length - 1);

            return Semantics(
              image: true,
              label: 'Price chart, ${window.length} ${widget.timeframe} candles. '
                  'Last price ${formatPrice(all.last.c)}.',
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onHorizontalDragUpdate: (d) => setState(() {
                  _focus = null;
                  // Dragging right moves back in time: one candle per candle-width of travel.
                  _offset = (_offset + d.delta.dx / slot).clamp(0, _maxOffset);
                }),
                onLongPressStart: (d) => setState(() => _focus = indexAt(d.localPosition.dx)),
                onLongPressMoveUpdate: (d) => setState(() => _focus = indexAt(d.localPosition.dx)),
                onLongPressEnd: (_) => setState(() => _focus = null),
                child: SizedBox(
                  height: widget.height,
                  child: Stack(
                    children: [
                      Positioned(
                        left: 0,
                        top: 0,
                        bottom: 0,
                        width: plotWidth,
                        child: RepaintBoundary(
                          child: CustomPaint(
                            painter: _ChartPainter(window, focus: _focus, showLastPrice: atNewest),
                          ),
                        ),
                      ),
                      if (nextWidth > 0)
                        Positioned(
                          right: 0,
                          top: 0,
                          bottom: 22, // lines up with the candle area, above the time labels
                          width: nextWidth,
                          child: _NextColumn(next: widget.next!),
                        ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            Expanded(child: _TimeLabels(window: window, atNewest: atNewest)),
            const SizedBox(width: 10),
            KeyButton(
              onTap: _zoom < _zoomLevels.length - 1 ? () => _setZoom(_zoom + 1) : null,
              minHeight: 44,
              padding: EdgeInsets.zero,
              semanticLabel: 'Show more candles',
              child: const Icon(Icons.remove_rounded, size: 20),
            ),
            const SizedBox(width: 8),
            KeyButton(
              onTap: _zoom > 0 ? () => _setZoom(_zoom - 1) : null,
              minHeight: 44,
              padding: EdgeInsets.zero,
              semanticLabel: 'Show fewer candles',
              child: const Icon(Icons.add_rounded, size: 20),
            ),
          ],
        ),
        const SizedBox(height: 12),
        const _Legend(),
      ],
    );
  }
}

/// The dashed NEXT column: the signal's color, icon and chance for the coming candle.
class _NextColumn extends StatelessWidget {
  const _NextColumn({required this.next});
  final NextSignal next;

  @override
  Widget build(BuildContext context) {
    final color = directionColor(next.direction, text: true);
    return CustomPaint(
      painter: _DashedBorderPainter(directionColor(next.direction)),
      child: Padding(
        padding: const EdgeInsets.only(top: 8),
        child: Column(
          children: [
            Text('NEXT', style: TmText.body(11, weight: FontWeight.w800, color: color, spacing: 1.1)),
            const SizedBox(height: 4),
            Icon(directionIcon(next.direction), size: 24, color: color),
            const SizedBox(height: 2),
            FittedBox(
              child: Text('${(next.probability * 100).round()}%', style: TmText.mono(13, color: color)),
            ),
            if (next.degraded) ...[
              const SizedBox(height: 4),
              const Icon(Icons.warning_amber_rounded, size: 16, color: Tm.neutral),
            ],
          ],
        ),
      ),
    );
  }
}

class _DashedBorderPainter extends CustomPainter {
  _DashedBorderPainter(this.color);
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final rrect = RRect.fromRectAndRadius((Offset.zero & size).deflate(1), const Radius.circular(14));
    canvas.drawRRect(
      rrect,
      Paint()
        ..shader = LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [color.withValues(alpha: 0.16), color.withValues(alpha: 0)],
        ).createShader(Offset.zero & size),
    );
    final line = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..color = color;
    for (final metric in (Path()..addRRect(rrect)).computeMetrics()) {
      for (var d = 0.0; d < metric.length; d += 10) {
        canvas.drawPath(metric.extractPath(d, math.min(d + 6, metric.length)), line);
      }
    }
  }

  @override
  bool shouldRepaint(_DashedBorderPainter old) => old.color != color;
}

/// "48h ago ... Now": relative labels, because "how long ago" is what a beginner asks.
class _TimeLabels extends StatelessWidget {
  const _TimeLabels({required this.window, required this.atNewest});
  final List<Candle> window;
  final bool atNewest;

  String _ago(DateTime time) {
    final hours = DateTime.now().toUtc().difference(time).inHours;
    return hours >= 48 ? '${hours ~/ 24}d ago' : '${hours}h ago';
  }

  @override
  Widget build(BuildContext context) {
    final style = TmText.body(12, color: Tm.muted2);
    Widget part(String text, Alignment alignment) => Expanded(
          child: FittedBox(fit: BoxFit.scaleDown, alignment: alignment, child: Text(text, style: style)),
        );
    return Row(
      children: [
        part(_ago(window.first.t), Alignment.centerLeft),
        part(_ago(window[window.length ~/ 2].t), Alignment.center),
        part(atNewest ? 'Now' : _ago(window.last.t), Alignment.centerRight),
      ],
    );
  }
}

/// Names every line and candle color, with a shape next to each color.
class _Legend extends StatelessWidget {
  const _Legend();

  @override
  Widget build(BuildContext context) {
    Widget line(Color color, String label) => Row(mainAxisSize: MainAxisSize.min, children: [
          Container(width: 16, height: 3, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(2))),
          const SizedBox(width: 6),
          Text(label, style: TmText.body(12, color: Tm.fg3)),
        ]);
    Widget candle(Color color, IconData icon, String label) => Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(icon, size: 20, color: color),
          const SizedBox(width: 4),
          Text(label, style: TmText.body(12, color: Tm.fg3)),
        ]);
    return Wrap(
      spacing: 14,
      runSpacing: 6,
      children: [
        line(Tm.ema9, 'EMA 9'),
        line(Tm.ema21, 'EMA 21'),
        line(Tm.ema50, 'EMA 50'),
        candle(Tm.up, Icons.arrow_drop_up_rounded, 'closed higher'),
        candle(Tm.down, Icons.arrow_drop_down_rounded, 'closed lower'),
        Text('EMA = average price of the last 9, 21 or 50 candles', style: TmText.body(12, color: Tm.muted2)),
      ],
    );
  }
}

class _ChartPainter extends CustomPainter {
  _ChartPainter(this.candles, {this.focus, required this.showLastPrice});

  final List<Candle> candles;
  final int? focus;
  final bool showLastPrice;

  static const _volumeShare = 0.16; // bottom part of the plot, for volume bars
  static const _labelSpace = 22.0; // room under the plot (kept empty; labels are widgets)

  @override
  void paint(Canvas canvas, Size size) {
    final plotHeight = size.height - _labelSpace;
    final priceHeight = plotHeight * (1 - _volumeShare) - 6;
    final slot = (size.width - kPriceAxis) / candles.length;

    // Price range of what is on screen, with a little air above and below.
    var lo = double.infinity, hi = -double.infinity, maxVolume = 0.0;
    for (final c in candles) {
      lo = math.min(lo, c.low);
      hi = math.max(hi, c.high);
      maxVolume = math.max(maxVolume, c.volume);
      for (final e in [c.ema9, c.ema21, c.ema50]) {
        if (e != null) {
          lo = math.min(lo, e);
          hi = math.max(hi, e);
        }
      }
    }
    final pad = (hi - lo) * 0.06;
    lo -= pad;
    hi += pad;
    if (hi <= lo) hi = lo + 1;
    double y(double price) => (hi - price) / (hi - lo) * priceHeight;
    double x(int i) => (i + 0.5) * slot;

    // Faint dashed guide lines.
    final guide = Paint()
      ..color = const Color(0x14FFFFFF)
      ..strokeWidth = 1;
    for (final fraction in [0.25, 0.5, 0.75]) {
      _dashedLine(canvas, Offset(0, priceHeight * fraction), Offset(size.width, priceHeight * fraction), guide);
    }

    // Volume bars along the bottom.
    for (var i = 0; i < candles.length; i++) {
      final c = candles[i];
      if (maxVolume <= 0) break;
      final h = c.volume / maxVolume * plotHeight * _volumeShare;
      canvas.drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTWH(x(i) - slot * 0.32, plotHeight - h, slot * 0.64, h),
          const Radius.circular(1.5),
        ),
        Paint()..color = (c.rising ? Tm.up : Tm.down).withValues(alpha: 0.28),
      );
    }

    // Candles: a thin wick, then a body with a soft glow and light on its left edge.
    for (var i = 0; i < candles.length; i++) {
      final c = candles[i];
      final color = c.rising ? Tm.up : Tm.down;
      final cx = x(i);
      canvas.drawLine(
        Offset(cx, y(c.high)),
        Offset(cx, y(c.low)),
        Paint()
          ..color = color
          ..strokeWidth = math.max(1, slot * 0.12)
          ..strokeCap = StrokeCap.round,
      );
      final top = y(math.max(c.open, c.close));
      final bodyHeight = math.max(2.5, y(math.min(c.open, c.close)) - top);
      final body = Rect.fromLTWH(cx - slot * 0.38, top, slot * 0.76, bodyHeight);
      final rounded = RRect.fromRectAndRadius(body, const Radius.circular(2));
      canvas.drawRRect(rounded, Paint()
        ..color = color.withValues(alpha: 0.28)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 5));
      canvas.drawRRect(rounded, Paint()..color = color);
      canvas.drawRRect(
        rounded,
        Paint()
          ..shader = const LinearGradient(
            colors: [Color(0x59FFFFFF), Color(0x00FFFFFF)],
            stops: [0, 0.5],
          ).createShader(body),
      );
    }

    // EMA lines. A candle that is still forming has no value yet, so the line just stops.
    void ema(double? Function(Candle) value, Color color) {
      final path = Path();
      var started = false;
      for (var i = 0; i < candles.length; i++) {
        final v = value(candles[i]);
        if (v == null) continue;
        started ? path.lineTo(x(i), y(v)) : path.moveTo(x(i), y(v));
        started = true;
      }
      canvas.drawPath(
        path,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.8
          ..strokeJoin = StrokeJoin.round
          ..color = color,
      );
    }

    ema((c) => c.ema50, Tm.ema50);
    ema((c) => c.ema21, Tm.ema21);
    ema((c) => c.ema9, Tm.ema9);

    // Dashed last-price line with a white price tag on the right.
    if (showLastPrice) {
      final last = candles.last;
      final ly = y(last.close).clamp(8.0, priceHeight - 8);
      _dashedLine(canvas, Offset(0, ly), Offset(size.width, ly), Paint()
        ..color = const Color(0x99FFFFFF)
        ..strokeWidth = 1);
      final tag = TextPainter(
        text: TextSpan(text: formatPrice(last.c, dollar: false), style: TmText.mono(10.5, color: Tm.ink)),
        textDirection: TextDirection.ltr,
      )..layout();
      final box = Rect.fromLTWH(size.width - tag.width - 10, ly - 9, tag.width + 10, 18); // inside the axis strip
      canvas.drawRRect(RRect.fromRectAndRadius(box, const Radius.circular(5)), Paint()..color = Colors.white);
      tag.paint(canvas, Offset(box.left + 5, ly - tag.height / 2));
    }

    // The candle under the finger: a vertical guide line.
    if (focus != null && focus! < candles.length) {
      final fx = x(focus!);
      canvas.drawLine(Offset(fx, 0), Offset(fx, plotHeight), Paint()
        ..color = const Color(0x66FFFFFF)
        ..strokeWidth = 1);
    }
  }

  void _dashedLine(Canvas canvas, Offset from, Offset to, Paint paint) {
    for (var dx = from.dx; dx < to.dx; dx += 8) {
      canvas.drawLine(Offset(dx, from.dy), Offset(math.min(dx + 4, to.dx), from.dy), paint);
    }
  }

  @override
  bool shouldRepaint(_ChartPainter old) =>
      old.candles != candles || old.focus != focus || old.showLastPrice != showLastPrice;
}
