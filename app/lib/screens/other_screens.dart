import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/models.dart';
import '../widgets/widgets.dart';
import '../providers/theme_provider.dart';

// ── 훈련과정 화면 ─────────────────────────────────────────────────────────────
class ProgramsScreen extends StatefulWidget {
  const ProgramsScreen({super.key});
  @override
  State<ProgramsScreen> createState() => _ProgramsScreenState();
}

class _ProgramsScreenState extends State<ProgramsScreen> {
  List<Program> _programs = [];
  bool _loading = true;
  String? _error;
  String _search = '';
  String _filter = '전체';

  static const _filters = ['전체', '내일배움카드', '일학습병행', '취업역량'];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final data = await ApiService().listPrograms();
      setState(() => _programs = (data['programs'] as List? ?? []).map((e) => Program.fromJson(e)).toList());
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  List<Program> get _filtered => _programs.where((p) {
    if (_filter != '전체') {
      if (_filter == '내일배움카드' && p.programType != 'kdt') return false;
      if (_filter == '일학습병행' && p.programType != 'apprenticeship') return false;
      if (_filter == '취업역량' && p.programType != 'capability') return false;
    }
    if (_search.isEmpty) return true;
    final q = _search.toLowerCase();
    return (p.title).toLowerCase().contains(q) ||
        (p.summary ?? '').toLowerCase().contains(q) ||
        (p.skills ?? '').toLowerCase().contains(q);
  }).toList();

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      appBar: AppBar(
        title: const Text('훈련과정', style: TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          IconButton(icon: const Icon(Icons.refresh, size: 20), onPressed: _load),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
            child: Column(children: [
              TextField(
                decoration: InputDecoration(
                  hintText: '제목 / 요약 / 스킬 검색',
                  prefixIcon: const Icon(Icons.search, size: 18, color: AppColors.darkMuted),
                  isDense: true,
                  contentPadding: const EdgeInsets.symmetric(vertical: 10),
                ),
                onChanged: (v) => setState(() => _search = v),
              ),
              const SizedBox(height: 10),
              SizedBox(
                height: 34,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: _filters.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 6),
                  itemBuilder: (_, i) {
                    final f = _filters[i];
                    final selected = f == _filter;
                    return GestureDetector(
                      onTap: () => setState(() => _filter = f),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                        decoration: BoxDecoration(
                          color: selected ? AppColors.primary : (isDark ? AppColors.darkSurface : AppColors.lightSurface),
                          borderRadius: BorderRadius.circular(99),
                          border: Border.all(color: selected ? AppColors.primary : (isDark ? AppColors.darkBorder : AppColors.lightBorder)),
                        ),
                        child: Text(f, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600,
                          color: selected ? Colors.white : (isDark ? AppColors.darkMuted : AppColors.lightMuted))),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 8),
              Row(children: [
                Text('총 ${_filtered.length}개', style: const TextStyle(fontSize: 12, color: AppColors.darkMuted)),
              ]),
            ]),
          ),
          Expanded(child: _loading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: _filtered.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (_, i) => ProgramCard(program: _filtered[i]),
                ),
          ),
        ],
      ),
    );
  }
}

// ── 국가자격 화면 ─────────────────────────────────────────────────────────────
class QualificationsScreen extends StatefulWidget {
  const QualificationsScreen({super.key});
  @override
  State<QualificationsScreen> createState() => _QualificationsScreenState();
}

class _QualificationsScreenState extends State<QualificationsScreen> {
  List<Qualification> _quals = [];
  Map<String, ExamSchedule> _schedules = {};
  bool _loading = true;
  String? _error;
  String _search = '';
  String _type = '전체';

  static const _types = ['전체', '기술사', '기능장', '기사', '산업기사', '기능사'];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final data = await ApiService().listQualifications(
        q: _search.isEmpty ? null : _search,
        qualType: _type == '전체' ? null : _type,
      );
      final quals = (data['qualifications'] as List? ?? [])
          .map((e) => Qualification.fromJson(e)).toList();
      final rawScheds = data['schedules'] as Map<String, dynamic>? ?? {};
      final schedules = rawScheds.map((k, v) => MapEntry(k, ExamSchedule.fromJson(v)));
      setState(() { _quals = quals; _schedules = schedules; });
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      appBar: AppBar(
        title: const Text('국가자격', style: TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          IconButton(icon: const Icon(Icons.refresh, size: 20), onPressed: _load),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
            child: Column(children: [
              Row(children: [
                Expanded(
                  child: TextField(
                    decoration: const InputDecoration(
                      hintText: '자격명 또는 직무분야 검색',
                      prefixIcon: Icon(Icons.search, size: 18, color: AppColors.darkMuted),
                      isDense: true,
                      contentPadding: EdgeInsets.symmetric(vertical: 10),
                    ),
                    onChanged: (v) => setState(() => _search = v),
                    onSubmitted: (_) => _load(),
                  ),
                ),
                const SizedBox(width: 8),
                SizedBox(
                  height: 42,
                  child: ElevatedButton(
                    onPressed: _load,
                    style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 14)),
                    child: const Text('검색', style: TextStyle(fontSize: 13)),
                  ),
                ),
              ]),
              const SizedBox(height: 10),
              SizedBox(
                height: 34,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: _types.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 6),
                  itemBuilder: (_, i) {
                    final t = _types[i];
                    final selected = t == _type;
                    return GestureDetector(
                      onTap: () { setState(() => _type = t); _load(); },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                        decoration: BoxDecoration(
                          color: selected ? AppColors.primary : (isDark ? AppColors.darkSurface : AppColors.lightSurface),
                          borderRadius: BorderRadius.circular(99),
                          border: Border.all(color: selected ? AppColors.primary : (isDark ? AppColors.darkBorder : AppColors.lightBorder)),
                        ),
                        child: Text(t, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600,
                          color: selected ? Colors.white : (isDark ? AppColors.darkMuted : AppColors.lightMuted))),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 8),
              Row(children: [
                Text('총 ${_quals.length}개', style: const TextStyle(fontSize: 12, color: AppColors.darkMuted)),
              ]),
            ]),
          ),
          Expanded(child: _loading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: _quals.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (_, i) {
                    final q = _quals[i];
                    return QualificationCard(
                      qual: q,
                      nextExam: _schedules[q.qualCode],
                    );
                  },
                ),
          ),
        ],
      ),
    );
  }
}

// ── 채용공고 화면 ─────────────────────────────────────────────────────────────
class JobsScreen extends StatefulWidget {
  const JobsScreen({super.key});
  @override
  State<JobsScreen> createState() => _JobsScreenState();
}

class _JobsScreenState extends State<JobsScreen> {
  List<Job> _jobs = [];
  bool _loading = true;
  String? _error;
  final _searchCtrl = TextEditingController();
  final _locationCtrl = TextEditingController();

  @override
  void initState() { super.initState(); _load(); }
  @override
  void dispose() { _searchCtrl.dispose(); _locationCtrl.dispose(); super.dispose(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final data = await ApiService().listJobs(
        q: _searchCtrl.text.trim().isEmpty ? null : _searchCtrl.text.trim(),
        location: _locationCtrl.text.trim().isEmpty ? null : _locationCtrl.text.trim(),
      );
      setState(() => _jobs = (data['jobs'] as List? ?? []).map((e) => Job.fromJson(e)).toList());
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('채용공고', style: TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          IconButton(icon: const Icon(Icons.refresh, size: 20), onPressed: _load),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: Column(children: [
              TextField(
                controller: _searchCtrl,
                decoration: const InputDecoration(
                  hintText: '직무명, 회사명, 스킬 검색',
                  prefixIcon: Icon(Icons.work_outline, size: 18, color: AppColors.darkMuted),
                  isDense: true,
                  contentPadding: EdgeInsets.symmetric(vertical: 10),
                ),
                onSubmitted: (_) => _load(),
              ),
              const SizedBox(height: 8),
              Row(children: [
                Expanded(
                  child: TextField(
                    controller: _locationCtrl,
                    decoration: const InputDecoration(
                      hintText: '지역 (서울, 경기...)',
                      prefixIcon: Icon(Icons.location_on_outlined, size: 18, color: AppColors.darkMuted),
                      isDense: true,
                      contentPadding: EdgeInsets.symmetric(vertical: 10),
                    ),
                    onSubmitted: (_) => _load(),
                  ),
                ),
                const SizedBox(width: 8),
                SizedBox(
                  height: 42,
                  child: ElevatedButton(
                    onPressed: _load,
                    style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 14)),
                    child: const Text('검색', style: TextStyle(fontSize: 13)),
                  ),
                ),
              ]),
              const SizedBox(height: 6),
              Row(children: [
                Text('총 ${_jobs.length}개 채용공고', style: const TextStyle(fontSize: 12, color: AppColors.darkMuted)),
              ]),
            ]),
          ),
          Expanded(child: _loading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
              : _jobs.isEmpty
                ? const Center(child: Text('채용공고가 없습니다.', style: TextStyle(color: AppColors.darkMuted)))
                : ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                    itemCount: _jobs.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 12),
                    itemBuilder: (_, i) => JobCard(job: _jobs[i]),
                  ),
          ),
        ],
      ),
    );
  }
}
