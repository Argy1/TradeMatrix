import 'package:flutter/material.dart';

import '../theme/tokens.dart';

/// Shared press behavior of the 3D buttons: while a finger is down the face moves 3 px
/// toward its hard shadow, like a key being pushed (docs/08: press = 80 ms, translate 3 px).
class _Pressable extends StatefulWidget {
  const _Pressable({required this.onTap, required this.builder, this.semanticLabel, this.selected});

  final VoidCallback? onTap;
  final Widget Function(BuildContext context, bool pressed) builder;
  final String? semanticLabel;
  final bool? selected;

  @override
  State<_Pressable> createState() => _PressableState();
}

class _PressableState extends State<_Pressable> {
  bool _down = false;

  void _set(bool value) {
    if (widget.onTap != null && _down != value) setState(() => _down = value);
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      enabled: widget.onTap != null,
      selected: widget.selected,
      label: widget.semanticLabel,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTapDown: (_) => _set(true),
        onTapUp: (_) => _set(false),
        onTapCancel: () => _set(false),
        onTap: widget.onTap,
        child: widget.builder(context, _down),
      ),
    );
  }
}

const _press = Duration(milliseconds: 80);

/// Secondary "keycap" button: glass face, hard 4 px shadow below. `selected` turns it
/// violet (the chosen coin, the chosen candle size).
class KeyButton extends StatelessWidget {
  const KeyButton({
    super.key,
    required this.child,
    required this.onTap,
    this.selected = false,
    this.minHeight = 44,
    this.minWidth = 44,
    this.padding = const EdgeInsets.symmetric(horizontal: 14),
    this.radius = Tm.rKey,
    this.semanticLabel,
    this.borderColor,
  });

  final Widget child;
  final VoidCallback? onTap;
  final bool selected;
  final double minHeight, minWidth, radius;
  final EdgeInsetsGeometry padding;
  final String? semanticLabel;
  final Color? borderColor;

  @override
  Widget build(BuildContext context) {
    return _Pressable(
      onTap: onTap,
      semanticLabel: semanticLabel,
      selected: selected ? true : null,
      builder: (context, pressed) => AnimatedContainer(
        duration: _press,
        // 3 px of travel on press; the shadow shrinks by the same amount so the base stays put.
        transform: Matrix4.translationValues(0, pressed ? 3 : 0, 0),
        constraints: BoxConstraints(minHeight: minHeight, minWidth: minWidth),
        padding: padding,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(radius),
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: selected
                ? const [Color(0x737C5CFF), Color(0x2E7C5CFF)]
                : const [Color(0x1FFFFFFF), Color(0x0AFFFFFF)],
          ),
          border: Border.all(
            color: borderColor ?? (selected ? const Color(0xCCB49BFF) : const Color(0x1FFFFFFF)),
          ),
          boxShadow: [BoxShadow(color: const Color(0x80000000), offset: Offset(0, pressed ? 1 : 4))],
        ),
        child: DefaultTextStyle.merge(
          style: TmText.body(15, weight: FontWeight.w600),
          child: IconTheme.merge(data: const IconThemeData(color: Tm.fg, size: 22), child: child),
        ),
      ),
    );
  }
}

/// Primary button: cyan face, darker cyan edge below, soft glow. Dark text for contrast.
class PrimaryButton extends StatelessWidget {
  const PrimaryButton({super.key, required this.label, required this.onTap, this.icon, this.busy = false});

  final String label;
  final VoidCallback? onTap;
  final IconData? icon;
  final bool busy;

  @override
  Widget build(BuildContext context) {
    final enabled = onTap != null && !busy;
    return Opacity(
      opacity: enabled ? 1 : 0.6,
      child: _Pressable(
        onTap: enabled ? onTap : null,
        builder: (context, pressed) => AnimatedContainer(
          duration: _press,
          transform: Matrix4.translationValues(0, pressed ? 3 : 0, 0),
          constraints: const BoxConstraints(minHeight: 52),
          padding: const EdgeInsets.symmetric(horizontal: 18),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(Tm.rButton),
            gradient: const LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Tm.cyanLight, Tm.cyanDeep],
            ),
            boxShadow: [
              BoxShadow(color: Tm.cyanEdge, offset: Offset(0, pressed ? 1 : 4)),
              BoxShadow(
                color: const Color(0x523FC4EE),
                offset: Offset(0, pressed ? 6 : 12),
                blurRadius: pressed ? 14 : 26,
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[Icon(icon, size: 20, color: Tm.onCyan), const SizedBox(width: 8)],
              Flexible(
                child: Text(
                  busy ? 'Please wait…' : label,
                  textAlign: TextAlign.center,
                  style: TmText.body(16, weight: FontWeight.w700, color: Tm.onCyan),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
