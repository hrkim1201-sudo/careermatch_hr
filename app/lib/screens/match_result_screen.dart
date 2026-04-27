import 'package:flutter/material.dart';
import '../models/models.dart';
import '../widgets/widgets.dart';
import '../providers/theme_provider.dart';

class MatchResultScreen extends StatefulWidget {
  final String prompt;
  final List<MatchResult> results;
  const MatchResultScreen({super.key, required this.prompt, required this.results});

  @override
  State<MatchResultScreen> createState() => _MatchResultScreenState();
}

class _MatchResultScreenState extends State<MatchResultScreen> {
  final Set<int> _expandedQuals = {};
  final Set<int> _expandedJobs = {};

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      appBar: AppBar(
        title: const Text('추천 결과', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 17)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 검색어 표시
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: isDark ? AppColors.darkSurface : AppColors.lightSurface,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: isDark ? AppColors.darkBorder : AppColors.lightBorder),
            ),
            child: Row(children: [
              const Text('검색', style: TextStyle(fontSize: 11, color: AppColors.primary, fontWeight: FontWeight.w700)),
              const SizedBox(width: 10),
              Expanded(child: Text(widget.prompt,
                style: TextStyle(fontSize: 13, color: isDark ? AppColors.darkMuted : AppColors.lightMuted))),
            ]),
          ),
          const SizedBox(height: 12),
          Text('${widget.results.length}개 훈련과정 추천',
            style: TextStyle(fontSize: 13, color: isDark ? AppColors.darkMuted : AppColors.lightMuted)),
          const SizedBox(height: 12),

          // 결과 카드들
          ...widget.results.map((item) => Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: AppCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 점수 + 키워드
                  Row(children: [
                    ScoreBadge(item.score),
                    const SizedBox(width: 8),
                    if (item.reasonKeywords.isNotEmpty)
                      Expanded(child: Text(
                        item.reasonKeywords.join(', '),
                        style: const TextStyle(fontSize: 11, color: AppColors.darkMuted),
                        overflow: TextOverflow.ellipsis,
                      )),
                  ]),
                  const SizedBox(height: 12),

                  // 훈련과정 카드
                  ProgramCard(program: item.program, compact: true),
                  const SizedBox(height: 8),

                  // 관련 국가자격
                  if (item.relatedQualifications.isNotEmpty) ...[
                    _divider(),
                    _expandToggle(
                      icon: '🏆',
                      label: '관련 국가자격 ${item.relatedQualifications.length}개',
                      color: AppColors.accent,
                      expanded: _expandedQuals.contains(item.id),
                      onTap: () => setState(() {
                        _expandedQuals.contains(item.id)
                            ? _expandedQuals.remove(item.id)
                            : _expandedQuals.add(item.id);
                      }),
                    ),
                    if (_expandedQuals.contains(item.id))
                      ...item.relatedQualifications.map((rq) => Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: QualificationCard(
                          qual: rq.qualification,
                          nextExam: rq.nextExam,
                          compact: true,
                        ),
                      )),
                  ],

                  // 관련 채용공고
                  if (item.relatedJobs.isNotEmpty) ...[
                    _divider(),
                    _expandToggle(
                      icon: '💼',
                      label: '관련 채용공고 ${item.relatedJobs.length}개',
                      color: AppColors.primary,
                      expanded: _expandedJobs.contains(item.id),
                      onTap: () => setState(() {
                        _expandedJobs.contains(item.id)
                            ? _expandedJobs.remove(item.id)
                            : _expandedJobs.add(item.id);
                      }),
                    ),
                    if (_expandedJobs.contains(item.id))
                      ...item.relatedJobs.map((job) => Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: JobCard(job: job, compact: true),
                      )),
                  ],
                ],
              ),
            ),
          )),
        ],
      ),
    );
  }

  Widget _divider() => const Padding(
    padding: EdgeInsets.symmetric(vertical: 10),
    child: Divider(height: 1, color: AppColors.darkBorder),
  );

  Widget _expandToggle({
    required String icon,
    required String label,
    required Color color,
    required bool expanded,
    required VoidCallback onTap,
  }) => GestureDetector(
    onTap: onTap,
    child: Row(children: [
      Text(icon, style: const TextStyle(fontSize: 13)),
      const SizedBox(width: 6),
      Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: color)),
      const Spacer(),
      Icon(expanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down, color: color, size: 18),
    ]),
  );
}
