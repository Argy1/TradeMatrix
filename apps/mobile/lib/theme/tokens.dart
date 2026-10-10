import 'package:flutter/material.dart';

/// "Matrix Glass" design tokens (docs/08-DESIGN.md), the same values as the web app's CSS.
abstract final class Tm {
  // Surfaces
  static const ink = Color(0xFF060913); // page background
  static const glowViolet = Color(0x527C5CFF); // radial glow, top right
  static const glowCyan = Color(0x2E4DD8FF); // radial glow, top left

  // Text
  static const fg = Color(0xFFEAF0FF);
  static const fg2 = Color(0xFFC9D4EE);
  static const fg3 = Color(0xFFB4C0DC);
  static const muted = Color(0xFF9AA8C7);
  static const muted2 = Color(0xFF8FA0C4);

  // Brand
  static const cyan = Color(0xFF4DD8FF);
  static const cyanLight = Color(0xFF7BE8FF);
  static const cyanDeep = Color(0xFF3FC4EE);
  static const cyanEdge = Color(0xFF1B7FA3); // the extruded edge of the primary button
  static const onCyan = Color(0xFF04121A);
  static const violet = Color(0xFF7C5CFF);
  static const violetLight = Color(0xFFB49BFF);

  // Signal colors. Never the only cue: always with an icon and a word.
  static const up = Color(0xFF2EE6A6);
  static const down = Color(0xFFFF5C7A);
  static const downText = Color(0xFFFF8FA3); // red that passes contrast on the dark page
  static const neutral = Color(0xFFFFC857);

  // Chart lines
  static const ema9 = Color(0xFF4DD8FF);
  static const ema21 = Color(0xFFB49BFF);
  static const ema50 = Color(0xFFFFC857);

  // Shape
  static const rCard = 24.0;
  static const rKey = 14.0;
  static const rButton = 16.0;
  static const rTile = 16.0;

  static const hairline = Color(0x1AFFFFFF); // 10% white
}

/// Text styles. The fonts are variable fonts, so the weight is set twice: `fontWeight` for
/// the layout engine and `fontVariations` for the font's own weight axis.
abstract final class TmText {
  static TextStyle _style(String family, double size, FontWeight weight, Color color,
      {double? height, double? spacing, List<FontFeature>? features}) {
    return TextStyle(
      fontFamily: family,
      fontSize: size,
      fontWeight: weight,
      fontVariations: [FontVariation('wght', weight.value.toDouble())],
      color: color,
      height: height,
      letterSpacing: spacing,
      fontFeatures: features,
    );
  }

  /// Sora: headings and the signal word.
  static TextStyle display(double size,
          {FontWeight weight = FontWeight.w700, Color color = Tm.fg, double? height, double? spacing}) =>
      _style('Sora', size, weight, color, height: height, spacing: spacing);

  /// DM Sans: body and controls.
  static TextStyle body(double size,
          {FontWeight weight = FontWeight.w400, Color color = Tm.fg, double? height, double? spacing}) =>
      _style('DMSans', size, weight, color, height: height, spacing: spacing);

  /// JetBrains Mono with tabular digits: prices and percentages line up.
  static TextStyle mono(double size,
          {FontWeight weight = FontWeight.w700, Color color = Tm.fg, double? spacing}) =>
      _style('JetBrainsMono', size, weight, color,
          spacing: spacing, features: const [FontFeature.tabularFigures()]);
}

ThemeData buildTheme() {
  final scheme = ColorScheme.fromSeed(
    seedColor: Tm.cyan,
    brightness: Brightness.dark,
    surface: Tm.ink,
    primary: Tm.cyan,
    secondary: Tm.violet,
    error: Tm.down,
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: Tm.ink,
    fontFamily: 'DMSans',
    textTheme: Typography.whiteMountainView.apply(
      fontFamily: 'DMSans',
      bodyColor: Tm.fg,
      displayColor: Tm.fg,
    ),
    splashFactory: NoSplash.splashFactory, // keycaps press down instead of rippling
    highlightColor: Colors.transparent,
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: const Color(0x0DFFFFFF),
      hintStyle: TmText.body(15, color: Tm.muted),
      labelStyle: TmText.body(14, weight: FontWeight.w600, color: Tm.fg2),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Tm.rKey),
        borderSide: const BorderSide(color: Color(0x26FFFFFF)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Tm.rKey),
        borderSide: const BorderSide(color: Color(0x26FFFFFF)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Tm.rKey),
        borderSide: const BorderSide(color: Tm.cyan, width: 2),
      ),
    ),
  );
}
