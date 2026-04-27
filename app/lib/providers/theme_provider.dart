import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeProvider extends ChangeNotifier {
  ThemeMode _mode = ThemeMode.dark;
  ThemeMode get mode => _mode;
  bool get isDark => _mode == ThemeMode.dark;

  ThemeProvider() {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final isDark = prefs.getBool('dark_mode') ?? true;
    _mode = isDark ? ThemeMode.dark : ThemeMode.light;
    notifyListeners();
  }

  Future<void> toggle() async {
    _mode = isDark ? ThemeMode.light : ThemeMode.dark;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('dark_mode', isDark);
    notifyListeners();
  }
}

// ── 색상 팔레트 ───────────────────────────────────────────────────────────────
class AppColors {
  // 다크
  static const darkBg       = Color(0xFF080B14);
  static const darkSurface  = Color(0xFF111827);
  static const darkSurface2 = Color(0xFF1A2236);
  static const darkBorder   = Color(0x14FFFFFF);
  static const darkText     = Color(0xFFF0F4FF);
  static const darkMuted    = Color(0xFF8B97B8);

  // 라이트
  static const lightBg      = Color(0xFFF5F7FF);
  static const lightSurface = Color(0xFFFFFFFF);
  static const lightBorder  = Color(0x14000000);
  static const lightText    = Color(0xFF0F1629);
  static const lightMuted   = Color(0xFF5A6585);

  // 공통
  static const primary = Color(0xFF4F7CFF);
  static const accent  = Color(0xFF00E5B0);
  static const danger  = Color(0xFFF87171);
  static const warn    = Color(0xFFFBBF24);
}

ThemeData buildDarkTheme() => ThemeData(
  brightness: Brightness.dark,
  scaffoldBackgroundColor: AppColors.darkBg,
  colorScheme: const ColorScheme.dark(
    primary: AppColors.primary,
    secondary: AppColors.accent,
    surface: AppColors.darkSurface,
    error: AppColors.danger,
  ),
  cardColor: AppColors.darkSurface,
  dividerColor: AppColors.darkBorder,
  fontFamily: 'Pretendard',
  useMaterial3: true,
  appBarTheme: const AppBarTheme(
    backgroundColor: Color(0xD4080B14),
    foregroundColor: AppColors.darkText,
    elevation: 0,
    centerTitle: true,
  ),
  textTheme: const TextTheme(
    headlineLarge: TextStyle(color: AppColors.darkText, fontWeight: FontWeight.w800),
    headlineMedium: TextStyle(color: AppColors.darkText, fontWeight: FontWeight.w700),
    bodyLarge: TextStyle(color: AppColors.darkText),
    bodyMedium: TextStyle(color: AppColors.darkMuted),
    bodySmall: TextStyle(color: AppColors.darkMuted),
  ),
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: AppColors.darkSurface,
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: const BorderSide(color: AppColors.darkBorder),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: const BorderSide(color: AppColors.darkBorder),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
    ),
    hintStyle: const TextStyle(color: AppColors.darkMuted),
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: AppColors.primary,
      foregroundColor: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
    ),
  ),
);

ThemeData buildLightTheme() => ThemeData(
  brightness: Brightness.light,
  scaffoldBackgroundColor: AppColors.lightBg,
  colorScheme: const ColorScheme.light(
    primary: AppColors.primary,
    secondary: AppColors.accent,
    surface: AppColors.lightSurface,
    error: AppColors.danger,
  ),
  cardColor: AppColors.lightSurface,
  fontFamily: 'Pretendard',
  useMaterial3: true,
  appBarTheme: const AppBarTheme(
    backgroundColor: Color(0xE8F5F7FF),
    foregroundColor: AppColors.lightText,
    elevation: 0,
    centerTitle: true,
  ),
  textTheme: const TextTheme(
    headlineLarge: TextStyle(color: AppColors.lightText, fontWeight: FontWeight.w800),
    headlineMedium: TextStyle(color: AppColors.lightText, fontWeight: FontWeight.w700),
    bodyLarge: TextStyle(color: AppColors.lightText),
    bodyMedium: TextStyle(color: AppColors.lightMuted),
    bodySmall: TextStyle(color: AppColors.lightMuted),
  ),
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: AppColors.lightSurface,
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: const BorderSide(color: AppColors.lightBorder),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: const BorderSide(color: AppColors.lightBorder),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
    ),
    hintStyle: const TextStyle(color: AppColors.lightMuted),
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: AppColors.primary,
      foregroundColor: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
    ),
  ),
);
