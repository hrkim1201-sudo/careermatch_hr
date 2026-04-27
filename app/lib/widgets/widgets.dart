import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/models.dart';
import '../providers/theme_provider.dart';

// ── AppCard ───────────────────────────────────────────────────────────────────
class AppCard extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry? padding;

  const AppCard({super.key, required this.child, this.onTap, this.padding});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: padding ?? const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isDark ? AppColors.darkSurface : AppColors.lightSurface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isDark ? AppColors.darkBorder : AppColors.lightBorder,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(isDark ? 0.3 : 0.06),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: child,
      ),
    );
  }
}

// ── AppTag ────────────────────────────────────────────────────────────────────
enum TagVariant { def, primary, accent, warn }

class AppTag extends StatelessWidget {
  final String label;
  final TagVariant variant;

  const AppTag(this.label, {super.key, this.variant = TagVariant.def});

  @override
  Widget build(BuildContext context) {
    Color bg, fg, border;
    switch (variant) {
      case TagVariant.primary:
        bg = AppColors.primary.withOpacity(0.12);
        fg = AppColors.primary;
        border = AppColors.primary.withOpacity(0.3);
        break;
      case TagVariant.accent:
        bg = AppColors.accent.withOpacity(0.12);
        fg = AppColors.accent;
        border = AppColors.accent.withOpacity(0.3);
        break;
      case TagVariant.warn:
        bg = AppColors.warn.withOpacity(0.12);
        fg = AppColors.warn;
        border = AppColors.warn.withOpacity(0.3);
        break;
      default:
        final isDark = Theme.of(context).brightness == Brightness.dark;
        bg = isDark ? AppColors.darkSurface2 : AppColors.lightBg;
        fg = isDark ? AppColors.darkMuted : AppColors.lightMuted;
        border = isDark ? AppColors.darkBorder : AppColors.lightBorder;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(99),
        border: Border.all(color: border),
      ),
      child: Text(label, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: fg)),
    );
  }
}

// ── ScoreBadge ────────────────────────────────────────────────────────────────
class ScoreBadge extends StatelessWidget {
  final double score;
  const ScoreBadge(this.score, {super.key});

  Color get _color {
    if (score >= 80) return AppColors.accent;
    if (score >= 60) return AppColors.primary;
    if (score >= 40) return AppColors.warn;
    return AppColors.darkMuted;
  }

  String get _label {
    if (score >= 80) return '매우 높음';
    if (score >= 60) return '높음';
    if (score >= 40) return '보통';
    return '참고';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: _color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(99),
        border: Border.all(color: _color.withOpacity(0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            '${score.round()}점',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: _color),
          ),
          const SizedBox(width: 5),
          Container(width: 5, height: 5, decoration: BoxDecoration(color: _color, shape: BoxShape.circle)),
          const SizedBox(width: 4),
          Text(_label, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: _color)),
        ],
      ),
    );
  }
}

// ── ProgramCard ───────────────────────────────────────────────────────────────
class ProgramCard extends StatelessWidget {
  final Program program;
  final bool compact;
  const ProgramCard({super.key, required this.program, this.compact = false});

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              AppTag(program.typeLabel, variant: _typeVariant(program.programType)),
              const Spacer(),
              if (program.tuition != null)
                Text(program.tuition!, style: const TextStyle(fontSize: 11, color: AppColors.accent, fontWeight: FontWeight.w700)),
            ],
          ),
          const SizedBox(height: 8),
          Text(program.title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700), maxLines: 2, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 6),
          if (program.provider != null) _metaRow('🏫', program.provider!),
          if (program.location != null) _metaRow('📍', program.location!),
          if (program.schedule != null) _metaRow('🕐', program.schedule!),
          if (!compact && program.summary != null) ...[
            const SizedBox(height: 8),
            Text(program.summary!, style: const TextStyle(fontSize: 12), maxLines: 3, overflow: TextOverflow.ellipsis),
          ],
          if (program.skills != null) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 4, runSpacing: 4,
              children: program.skills!.split(' ').take(5)
                  .map((s) => _skillChip(s)).toList(),
            ),
          ],
          const SizedBox(height: 10),
          Row(
            children: [
              Wrap(
                spacing: 4, runSpacing: 4,
                children: program.tags.take(3).map((t) => AppTag(t)).toList(),
              ),
              const Spacer(),
              if (program.url != null && program.url!.isNotEmpty)
                GestureDetector(
                  onTap: () => _openUrl(program.url!),
                  child: const Text('고용24 보기 ↗', style: TextStyle(fontSize: 11, color: AppColors.primary, fontWeight: FontWeight.w600)),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metaRow(String icon, String text) => Padding(
    padding: const EdgeInsets.only(top: 2),
    child: Row(children: [
      Text(icon, style: const TextStyle(fontSize: 11)),
      const SizedBox(width: 4),
      Expanded(child: Text(text, style: const TextStyle(fontSize: 11, color: AppColors.darkMuted), overflow: TextOverflow.ellipsis)),
    ]),
  );

  Widget _skillChip(String s) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
    decoration: BoxDecoration(
      color: AppColors.primary.withOpacity(0.08),
      borderRadius: BorderRadius.circular(99),
      border: Border.all(color: AppColors.primary.withOpacity(0.2)),
    ),
    child: Text(s, style: const TextStyle(fontSize: 10, color: AppColors.primary, fontWeight: FontWeight.w600)),
  );

  TagVariant _typeVariant(String? t) {
    switch (t) {
      case 'kdt': return TagVariant.primary;
      case 'apprenticeship': return TagVariant.accent;
      case 'capability': return TagVariant.warn;
      default: return TagVariant.def;
    }
  }
}

// ── QualificationCard ─────────────────────────────────────────────────────────
class QualificationCard extends StatelessWidget {
  final Qualification qual;
  final ExamSchedule? nextExam;
  final bool compact;
  const QualificationCard({super.key, required this.qual, this.nextExam, this.compact = false});

  TagVariant _typeVariant(String? t) {
    switch (t) {
      case '기술사':
      case '기능장': return TagVariant.accent;
      case '기사': return TagVariant.primary;
      default: return TagVariant.def;
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            if (qual.qualType != null) AppTag(qual.qualType!, variant: _typeVariant(qual.qualType)),
            if (qual.jobFieldName != null) ...[
              const SizedBox(width: 6),
              Text(qual.jobFieldName!, style: const TextStyle(fontSize: 11, color: AppColors.darkMuted)),
            ],
          ]),
          const SizedBox(height: 8),
          Text(qual.qualName, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
          if (qual.midJobField != null)
            Padding(
              padding: const EdgeInsets.only(top: 3),
              child: Text(qual.midJobField!, style: const TextStyle(fontSize: 11, color: AppColors.darkMuted)),
            ),
          if (!compact && qual.relatedJobs != null) ...[
            const SizedBox(height: 6),
            Text(qual.relatedJobs!, style: const TextStyle(fontSize: 11, color: AppColors.darkMuted), maxLines: 2, overflow: TextOverflow.ellipsis),
          ],
          if (!compact && (qual.writtenFee != null || qual.practicalFee != null)) ...[
            const SizedBox(height: 6),
            Row(children: [
              if (qual.writtenFee != null && qual.writtenFee != '0')
                Text('필기 ${_fmtFee(qual.writtenFee!)}원', style: const TextStyle(fontSize: 11, color: AppColors.darkMuted)),
              if (qual.practicalFee != null && qual.practicalFee != '0') ...[
                const SizedBox(width: 12),
                Text('실기 ${_fmtFee(qual.practicalFee!)}원', style: const TextStyle(fontSize: 11, color: AppColors.darkMuted)),
              ],
            ]),
          ],
          if (nextExam != null) ...[
            const SizedBox(height: 8),
            Row(children: [
              Container(width: 5, height: 5, decoration: const BoxDecoration(color: AppColors.accent, shape: BoxShape.circle)),
              const SizedBox(width: 6),
              Text(
                '${nextExam!.year}년 ${nextExam!.roundNo}회차${nextExam!.formattedWrittenDate != null ? ' · ${nextExam!.formattedWrittenDate}' : ''}',
                style: const TextStyle(fontSize: 11, color: AppColors.accent, fontWeight: FontWeight.w600),
              ),
            ]),
          ],
          const SizedBox(height: 10),
          GestureDetector(
            onTap: () => _openUrl(qual.qnetUrl),
            child: Text('Q-Net에서 ${qual.qualName} 보기 ↗',
              style: const TextStyle(fontSize: 11, color: AppColors.primary, fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
  }

  String _fmtFee(String fee) {
    try {
      return int.parse(fee).toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (m) => '${m[1]},');
    } catch (_) { return fee; }
  }
}

// ── JobCard ───────────────────────────────────────────────────────────────────
class JobCard extends StatelessWidget {
  final Job job;
  final bool compact;
  const JobCard({super.key, required this.job, this.compact = false});

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Expanded(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(job.title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700), maxLines: 2, overflow: TextOverflow.ellipsis),
                const SizedBox(height: 3),
                Text(job.company ?? '기업명 비공개', style: const TextStyle(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.w600)),
              ]),
            ),
            if (job.employmentType != null)
              AppTag(job.employmentType!, variant: TagVariant.primary),
          ]),
          const SizedBox(height: 8),
          Wrap(spacing: 12, runSpacing: 2, children: [
            if (job.location != null) _meta('📍', job.location!),
            if (job.salary != null) _meta('💰', job.salary!),
            if (job.deadline != null) _meta('📅', '~${job.deadline!}'),
          ]),
          if (!compact && job.summary != null) ...[
            const SizedBox(height: 8),
            Text(job.summary!, style: const TextStyle(fontSize: 12, color: AppColors.darkMuted), maxLines: 3, overflow: TextOverflow.ellipsis),
          ],
          if (job.skills != null) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 4, runSpacing: 4,
              children: job.skills!.split(RegExp(r'[\s,]+')).where((s) => s.isNotEmpty).take(6)
                  .map((s) => Container(
                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.darkSurface2,
                      borderRadius: BorderRadius.circular(99),
                      border: Border.all(color: AppColors.darkBorder),
                    ),
                    child: Text(s, style: const TextStyle(fontSize: 10, color: AppColors.darkMuted)),
                  )).toList(),
            ),
          ],
          const SizedBox(height: 10),
          GestureDetector(
            onTap: () => _openUrl(job.jobUrl),
            child: const Text('고용24에서 채용공고 확인하기 ↗',
              style: TextStyle(fontSize: 11, color: AppColors.primary, fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
  }

  Widget _meta(String icon, String text) => Row(mainAxisSize: MainAxisSize.min, children: [
    Text(icon, style: const TextStyle(fontSize: 11)),
    const SizedBox(width: 3),
    Flexible(child: Text(text, style: const TextStyle(fontSize: 11, color: AppColors.darkMuted), overflow: TextOverflow.ellipsis)),
  ]);
}

// ── 공통 유틸 ─────────────────────────────────────────────────────────────────
Future<void> _openUrl(String url) async {
  final uri = Uri.parse(url);
  if (await canLaunchUrl(uri)) await launchUrl(uri, mode: LaunchMode.externalApplication);
}

// ── 로딩 shimmer ──────────────────────────────────────────────────────────────
class LoadingCard extends StatelessWidget {
  const LoadingCard({super.key});
  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _shimmerBox(height: 12, width: 60),
        const SizedBox(height: 10),
        _shimmerBox(height: 16, width: double.infinity),
        const SizedBox(height: 6),
        _shimmerBox(height: 12, width: 120),
        const SizedBox(height: 6),
        _shimmerBox(height: 12, width: 90),
      ]),
    );
  }

  Widget _shimmerBox({required double height, required double width}) => Container(
    height: height,
    width: width,
    decoration: BoxDecoration(
      color: AppColors.darkSurface2,
      borderRadius: BorderRadius.circular(4),
    ),
  );
}
