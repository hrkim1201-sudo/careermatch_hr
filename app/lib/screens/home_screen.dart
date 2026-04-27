import 'package:flutter/material.dart';
import '../providers/theme_provider.dart';
import '../services/api_service.dart';
import '../models/models.dart';
import '../widgets/widgets.dart';
import 'match_result_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  bool _loading = false;

  static const _examples = [
    '서울에서 전기기사 자격증 따고 싶어요',
    'Python 백엔드 개발자로 취업하고 싶어요',
    '온라인으로 데이터 분석을 배우고 싶어요',
    '부산에서 용접 기술 배우고 싶어요',
    '취업 공백이 길어서 면접 준비도 필요해요',
  ];

  static const _features = [
    ('✦', '자연어 이해', '지역·직무·자격을 자유롭게 입력'),
    ('◈', '훈련과정 매칭', '고용24 내일배움카드 과정'),
    ('◉', '국가자격 연계', 'Q-Net 215개 자격 + 시험일정'),
    ('◆', '채용공고 연결', '관련 실제 채용공고 추천'),
  ];

  Future<void> _search() async {
    final prompt = _controller.text.trim();
    if (prompt.isEmpty) return;
    setState(() => _loading = true);
    try {
      final data = await ApiService().directMatch(prompt);
      final results = (data['results'] as List? ?? [])
          .map((e) => MatchResult.fromJson(e)).toList();
      if (mounted) {
        Navigator.push(context, MaterialPageRoute(
          builder: (_) => MatchResultScreen(prompt: prompt, results: results),
        ));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString()), backgroundColor: AppColors.danger),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: RadialGradient(
            center: const Alignment(0, -0.6),
            radius: 1.2,
            colors: [
              AppColors.primary.withOpacity(isDark ? 0.15 : 0.08),
              isDark ? AppColors.darkBg : AppColors.lightBg,
            ],
          ),
        ),
        child: SafeArea(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 32, 20, 24),
            children: [
              Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(99),
                    border: Border.all(color: AppColors.primary.withOpacity(0.25)),
                  ),
                  child: Row(mainAxisSize: MainAxisSize.min, children: [
                    Container(width: 6, height: 6,
                      decoration: const BoxDecoration(color: AppColors.accent, shape: BoxShape.circle)),
                    const SizedBox(width: 7),
                    const Text('NCS 기반 취업 경로 추천',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                        color: AppColors.primary, letterSpacing: 0.5)),
                  ]),
                ),
              ),
              const SizedBox(height: 24),

              // 헤드라인 — ShaderMask로 그라디언트 (const 오류 수정)
              Center(
                child: Column(children: [
                  Text('원하는 것을 말하면',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800,
                      color: isDark ? AppColors.darkText : AppColors.lightText, height: 1.25)),
                  ShaderMask(
                    shaderCallback: (bounds) => const LinearGradient(
                      colors: [AppColors.primary, AppColors.accent],
                    ).createShader(bounds),
                    child: const Text('맞는 경로를 찾아드려요',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800,
                        color: Colors.white, height: 1.25)),
                  ),
                ]),
              ),
              const SizedBox(height: 12),

              Text(
                '직무·지역·자격증·온라인 여부를 자유롭게 입력하세요.\nAI가 훈련과정·국가자격·채용공고를 함께 추천합니다.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13,
                  color: isDark ? AppColors.darkMuted : AppColors.lightMuted, height: 1.65),
              ),
              const SizedBox(height: 28),

              // 입력창
              Container(
                decoration: BoxDecoration(
                  color: isDark ? AppColors.darkSurface : AppColors.lightSurface,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(
                    color: isDark ? AppColors.darkBorder : AppColors.lightBorder),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(isDark ? 0.3 : 0.06),
                      blurRadius: 16, offset: const Offset(0, 4)),
                  ],
                ),
                child: Column(children: [
                  TextField(
                    controller: _controller,
                    focusNode: _focusNode,
                    maxLines: 3, minLines: 2,
                    style: TextStyle(fontSize: 15,
                      color: isDark ? AppColors.darkText : AppColors.lightText),
                    decoration: InputDecoration(
                      hintText: 'IT 개발자로 취업하고 싶어요. Python이나 백엔드 쪽이요',
                      hintStyle: TextStyle(
                        color: isDark ? AppColors.darkMuted : AppColors.lightMuted, fontSize: 14),
                      filled: false, border: InputBorder.none,
                      contentPadding: const EdgeInsets.all(16),
                    ),
                    onChanged: (_) => setState(() {}),
                    onSubmitted: (_) => _search(),
                  ),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(8, 0, 8, 8),
                    child: Row(mainAxisAlignment: MainAxisAlignment.end, children: [
                      SizedBox(
                        height: 38,
                        child: ElevatedButton.icon(
                          onPressed: _controller.text.trim().isEmpty || _loading ? null : _search,
                          icon: _loading
                              ? const SizedBox(width: 14, height: 14,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                              : const Icon(Icons.arrow_forward, size: 16),
                          label: Text(_loading ? '분석 중...' : '추천 받기',
                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
                          style: ElevatedButton.styleFrom(
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(99)),
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                          ),
                        ),
                      ),
                    ]),
                  ),
                ]),
              ),
              const SizedBox(height: 12),

              Wrap(
                spacing: 6, runSpacing: 6, alignment: WrapAlignment.center,
                children: _examples.map((ex) => GestureDetector(
                  onTap: () { _controller.text = ex; setState(() {}); },
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: isDark ? AppColors.darkSurface2 : AppColors.lightBg,
                      borderRadius: BorderRadius.circular(99),
                      border: Border.all(color: isDark ? AppColors.darkBorder : AppColors.lightBorder),
                    ),
                    child: Text(ex, style: TextStyle(fontSize: 11,
                      color: isDark ? AppColors.darkMuted : AppColors.lightMuted)),
                  ),
                )).toList(),
              ),
              const SizedBox(height: 32),

              GridView.count(
                crossAxisCount: 2, shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisSpacing: 10, mainAxisSpacing: 10,
                childAspectRatio: 1.8,
                children: _features.map((f) => AppCard(
                  child: Row(children: [
                    Container(
                      width: 32, height: 32,
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Center(child: Text(f.$1,
                        style: const TextStyle(fontSize: 14, color: AppColors.primary))),
                    ),
                    const SizedBox(width: 10),
                    Expanded(child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(f.$2, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700,
                          color: isDark ? AppColors.darkText : AppColors.lightText)),
                        const SizedBox(height: 2),
                        Text(f.$3, style: const TextStyle(fontSize: 10, color: AppColors.darkMuted),
                          maxLines: 2, overflow: TextOverflow.ellipsis),
                      ],
                    )),
                  ]),
                )).toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
