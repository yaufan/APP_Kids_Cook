import 'package:flutter/material.dart';

/// 動物小餐廳's clay colours: chunky, soft and warm, shaded like plasticine
/// and never outlined (docs/design.md "畫風").
abstract final class Clay {
  static const cream = Color(0xFFFFF4E6);
  static const creamDeep = Color(0xFFF6E3CB);
  static const ink = Color(0xFF6B4A3A);
  static const inkSoft = Color(0xFF9A7B6A);

  static const tomato = Color(0xFFF2665A);
  static const peach = Color(0xFFFFB38A);
  static const butter = Color(0xFFFFD36E);
  static const mint = Color(0xFF8FD3B6);
  static const sky = Color(0xFF9DCBF0);
  static const lilac = Color(0xFFC9B3E8);
  static const wood = Color(0xFFD9A066);

  /// The green of "done" and the dashed guides.
  static const go = Color(0xFF5DBB7A);

  static const parentBg = Color(0xFFF6F2EA);
}

abstract final class ClayTheme {
  /// jf open 粉圓 (OFL): a rounded typeface made in Taiwan.
  static const font = 'Huninn';

  static ThemeData light() {
    final base = ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: Clay.tomato, surface: Clay.cream),
      scaffoldBackgroundColor: Clay.cream,
      fontFamily: font,
      materialTapTargetSize: MaterialTapTargetSize.padded,
    );
    return base.copyWith(textTheme: base.textTheme.apply(bodyColor: Clay.ink, displayColor: Clay.ink, fontFamily: font));
  }
}
