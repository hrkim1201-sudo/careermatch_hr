import 'dart:convert';
import 'package:http/http.dart' as http;

const String kBaseUrl = 'https://careermatchhr-production.up.railway.app';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final _client = http.Client();
  final _headers = {'Content-Type': 'application/json'};

  Future<Map<String, dynamic>> _get(String path) async {
    final uri = Uri.parse('$kBaseUrl$path');
    final res = await _client.get(uri, headers: _headers).timeout(
      const Duration(seconds: 20),
    );
    if (res.statusCode != 200) {
      throw ApiException('서버 오류 (${res.statusCode})');
    }
    return json.decode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> _post(String path, [Map<String, dynamic>? body]) async {
    final uri = Uri.parse('$kBaseUrl$path');
    final res = await _client.post(
      uri,
      headers: _headers,
      body: body != null ? json.encode(body) : null,
    ).timeout(const Duration(seconds: 30));
    if (res.statusCode != 200) {
      throw ApiException('서버 오류 (${res.statusCode})');
    }
    return json.decode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
  }

  // ── 추천 ──────────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> directMatch(String prompt) =>
      _post('/api/match/direct', {'prompt': prompt});

  // ── 훈련과정 ──────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> listPrograms() => _get('/api/programs');

  // ── 국가자격 ──────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> listQualifications({
    String? q,
    String? qualType,
  }) {
    final params = <String, String>{};
    if (q != null && q.isNotEmpty) params['q'] = q;
    if (qualType != null && qualType != '전체') params['qual_type'] = qualType;
    final query = params.entries.map((e) => '${e.key}=${Uri.encodeComponent(e.value)}').join('&');
    return _get('/api/qualifications${query.isEmpty ? '' : '?$query'}');
  }

  // ── 채용공고 ──────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> listJobs({String? q, String? location}) {
    final params = <String, String>{};
    if (q != null && q.isNotEmpty) params['q'] = q;
    if (location != null && location.isNotEmpty) params['location'] = location;
    final query = params.entries.map((e) => '${e.key}=${Uri.encodeComponent(e.value)}').join('&');
    return _get('/api/jobs${query.isEmpty ? '' : '?$query'}');
  }

  // ── 헬스체크 ──────────────────────────────────────────────────────────────
  Future<bool> healthCheck() async {
    try {
      final res = await _get('/health');
      return res['status'] == 'healthy';
    } catch (_) {
      return false;
    }
  }
}
