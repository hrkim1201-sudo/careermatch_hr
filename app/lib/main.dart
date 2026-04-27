import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'providers/theme_provider.dart';
import 'screens/home_screen.dart';
import 'screens/other_screens.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));
  runApp(
    ChangeNotifierProvider(
      create: (_) => ThemeProvider(),
      child: const CareerMatchApp(),
    ),
  );
}

class CareerMatchApp extends StatelessWidget {
  const CareerMatchApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = context.watch<ThemeProvider>();
    return MaterialApp(
      title: 'CareerMatch',
      debugShowCheckedModeBanner: false,
      themeMode: themeProvider.mode,
      theme: buildLightTheme(),
      darkTheme: buildDarkTheme(),
      home: const MainShell(),
    );
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _index = 0;

  static const _screens = [
    HomeScreen(),
    ProgramsScreen(),
    QualificationsScreen(),
    JobsScreen(),
  ];

  static const _navItems = [
    BottomNavigationBarItem(icon: Icon(Icons.home_outlined), activeIcon: Icon(Icons.home), label: '추천'),
    BottomNavigationBarItem(icon: Icon(Icons.school_outlined), activeIcon: Icon(Icons.school), label: '훈련과정'),
    BottomNavigationBarItem(icon: Icon(Icons.emoji_events_outlined), activeIcon: Icon(Icons.emoji_events), label: '국가자격'),
    BottomNavigationBarItem(icon: Icon(Icons.work_outline), activeIcon: Icon(Icons.work), label: '채용공고'),
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final themeProvider = context.read<ThemeProvider>();
    return Scaffold(
      appBar: _index == 0 ? AppBar(
        title: RichText(
          text: const TextSpan(
            style: TextStyle(fontSize: 19, fontWeight: FontWeight.w800),
            children: [
              TextSpan(text: 'Career', style: TextStyle(color: Colors.white)),
              TextSpan(text: 'Match', style: TextStyle(color: AppColors.primary)),
            ],
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined, size: 20),
            onPressed: themeProvider.toggle,
            tooltip: '테마 변경',
          ),
        ],
      ) : null,
      body: IndexedStack(index: _index, children: _screens),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          border: Border(top: BorderSide(color: isDark ? AppColors.darkBorder : AppColors.lightBorder)),
        ),
        child: BottomNavigationBar(
          currentIndex: _index,
          onTap: (i) => setState(() => _index = i),
          type: BottomNavigationBarType.fixed,
          backgroundColor: isDark ? AppColors.darkSurface : AppColors.lightSurface,
          selectedItemColor: AppColors.primary,
          unselectedItemColor: isDark ? AppColors.darkMuted : AppColors.lightMuted,
          selectedLabelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
          unselectedLabelStyle: const TextStyle(fontSize: 11),
          elevation: 0,
          items: _navItems,
        ),
      ),
    );
  }
}
