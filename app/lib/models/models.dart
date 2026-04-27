// ── Program ──────────────────────────────────────────────────────────────────
class Program {
  final int id;
  final String title;
  final String? provider;
  final String? location;
  final String? schedule;
  final String? tuition;
  final String? summary;
  final String? skills;
  final String? url;
  final String? programType;
  final String? category;
  final String? ncsName;
  final List<String> tags;

  Program({
    required this.id,
    required this.title,
    this.provider,
    this.location,
    this.schedule,
    this.tuition,
    this.summary,
    this.skills,
    this.url,
    this.programType,
    this.category,
    this.ncsName,
    this.tags = const [],
  });

  factory Program.fromJson(Map<String, dynamic> j) => Program(
    id: j['id'] ?? 0,
    title: j['title'] ?? '',
    provider: j['provider'],
    location: j['location'],
    schedule: j['schedule'],
    tuition: j['tuition'],
    summary: j['summary'],
    skills: j['skills'],
    url: j['url'],
    programType: j['program_type'],
    category: j['category'],
    ncsName: j['ncs_name'],
    tags: List<String>.from(j['tags'] ?? []),
  );

  String get typeLabel {
    switch (programType) {
      case 'kdt': return '내일배움카드';
      case 'apprenticeship': return '일학습병행';
      case 'capability': return '취업역량';
      default: return '훈련과정';
    }
  }
}

// ── Qualification ─────────────────────────────────────────────────────────────
class Qualification {
  final String qualCode;
  final String qualName;
  final String? qualType;
  final String? jobFieldName;
  final String? midJobField;
  final String? relatedJobs;
  final String? writtenFee;
  final String? practicalFee;
  final String? detailUrl;

  Qualification({
    required this.qualCode,
    required this.qualName,
    this.qualType,
    this.jobFieldName,
    this.midJobField,
    this.relatedJobs,
    this.writtenFee,
    this.practicalFee,
    this.detailUrl,
  });

  factory Qualification.fromJson(Map<String, dynamic> j) => Qualification(
    qualCode: j['qual_code'] ?? '',
    qualName: j['qual_name'] ?? '',
    qualType: j['qual_type'],
    jobFieldName: j['job_field_name'],
    midJobField: j['mid_job_field'],
    relatedJobs: j['related_jobs'],
    writtenFee: j['written_fee'],
    practicalFee: j['practical_fee'],
    detailUrl: j['detail_url'],
  );

  String get qnetUrl =>
      'https://www.q-net.or.kr/crf005.do?id=crf00505&kw=${Uri.encodeComponent(qualName)}';
}

// ── ExamSchedule ──────────────────────────────────────────────────────────────
class ExamSchedule {
  final String? year;
  final String? roundNo;
  final String? writtenExamStart;
  final String? writtenResultDate;
  final String? practicalExamStart;
  final String? practicalResultDate;

  ExamSchedule({
    this.year,
    this.roundNo,
    this.writtenExamStart,
    this.writtenResultDate,
    this.practicalExamStart,
    this.practicalResultDate,
  });

  factory ExamSchedule.fromJson(Map<String, dynamic> j) => ExamSchedule(
    year: j['year'],
    roundNo: j['round_no'],
    writtenExamStart: j['written_exam_start'],
    writtenResultDate: j['written_result_date'],
    practicalExamStart: j['practical_exam_start'],
    practicalResultDate: j['practical_result_date'],
  );

  String? get formattedWrittenDate {
    final d = writtenExamStart;
    if (d == null || d.length < 8) return null;
    return '${d.substring(0, 4)}-${d.substring(4, 6)}-${d.substring(6, 8)}';
  }
}

// ── Job ───────────────────────────────────────────────────────────────────────
class Job {
  final int id;
  final String title;
  final String? company;
  final String? location;
  final String? salary;
  final String? employmentType;
  final String? deadline;
  final String? summary;
  final String? skills;
  final String? url;
  final String? ncsName;
  final List<String> tags;

  Job({
    required this.id,
    required this.title,
    this.company,
    this.location,
    this.salary,
    this.employmentType,
    this.deadline,
    this.summary,
    this.skills,
    this.url,
    this.ncsName,
    this.tags = const [],
  });

  factory Job.fromJson(Map<String, dynamic> j) => Job(
    id: j['id'] ?? 0,
    title: j['title'] ?? '',
    company: j['company'],
    location: j['location'],
    salary: j['salary'],
    employmentType: j['employment_type'],
    deadline: j['deadline'],
    summary: j['summary'],
    skills: j['skills'],
    url: j['url'],
    ncsName: j['ncs_name'],
    tags: List<String>.from(j['tags'] ?? []),
  );

  String get jobUrl {
    if (url != null && url!.isNotEmpty && url != 'https://www.work24.go.kr') {
      return url!;
    }
    return 'https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=${Uri.encodeComponent(title)}';
  }
}

// ── MatchResult ───────────────────────────────────────────────────────────────
class MatchResult {
  final int id;
  final Program program;
  final double score;
  final List<String> reasonKeywords;
  final List<RelatedQual> relatedQualifications;
  final List<Job> relatedJobs;

  MatchResult({
    required this.id,
    required this.program,
    required this.score,
    this.reasonKeywords = const [],
    this.relatedQualifications = const [],
    this.relatedJobs = const [],
  });

  factory MatchResult.fromJson(Map<String, dynamic> j) => MatchResult(
    id: j['id'] ?? 0,
    program: Program.fromJson(j['program'] ?? {}),
    score: (j['score'] ?? 0).toDouble(),
    reasonKeywords: List<String>.from(j['reason_keywords'] ?? []),
    relatedQualifications: (j['related_qualifications'] as List? ?? [])
        .map((e) => RelatedQual.fromJson(e))
        .toList(),
    relatedJobs: (j['related_jobs'] as List? ?? [])
        .map((e) => Job.fromJson(e))
        .toList(),
  );

  String get scoreLabel {
    if (score >= 80) return '매우 높음';
    if (score >= 60) return '높음';
    if (score >= 40) return '보통';
    return '참고';
  }
}

class RelatedQual {
  final Qualification qualification;
  final ExamSchedule? nextExam;

  RelatedQual({required this.qualification, this.nextExam});

  factory RelatedQual.fromJson(Map<String, dynamic> j) => RelatedQual(
    qualification: Qualification.fromJson(j['qualification'] ?? {}),
    nextExam: j['next_exam'] != null ? ExamSchedule.fromJson(j['next_exam']) : null,
  );
}
