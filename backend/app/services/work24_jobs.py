"""Work24 채용정보(구인공고) API 클라이언트.

Endpoint : https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do
Params   : authKey, callTp=L, returnType=XML, startPage, display(max 100)
Response : XML
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
import xmltodict
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories import job_repo

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"

# 샘플 채용공고 (API 실패 시 fallback)
SAMPLE_JOBS: list[dict] = [
    {
        "external_id": "sample-job-001",
        "title": "Python 백엔드 개발자",
        "company": "(주)테크스타트업",
        "location": "서울 강남구",
        "salary": "3,500~5,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-31",
        "summary": "FastAPI 기반 백엔드 서비스 개발 및 운영. AI 서비스 API 설계 경험 우대.",
        "skills": "Python FastAPI PostgreSQL Docker REST API",
        "url": "",
        "ncs_code": "20",
        "ncs_name": "정보통신",
        "tags": ["백엔드", "Python", "FastAPI", "정규직"],
    },
    {
        "external_id": "sample-job-002",
        "title": "데이터 분석가",
        "company": "(주)데이터인사이트",
        "location": "서울 여의도",
        "salary": "3,000~4,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-15",
        "summary": "SQL, Python을 활용한 비즈니스 데이터 분석 및 대시보드 구축.",
        "skills": "SQL Python Pandas Power BI Tableau",
        "url": "",
        "ncs_code": "20",
        "ncs_name": "정보통신",
        "tags": ["데이터분석", "SQL", "Python", "정규직"],
    },
    {
        "external_id": "sample-job-003",
        "title": "전기 설비 기사",
        "company": "(주)한국전력기술",
        "location": "경기 수원",
        "salary": "3,200~4,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-20",
        "summary": "산업 현장 전기 설비 설계 및 유지보수. 전기기사 자격증 소지자 우대.",
        "skills": "전기설비 AutoCAD 전력공학 PLC",
        "url": "",
        "ncs_code": "19",
        "ncs_name": "전기전자",
        "tags": ["전기", "설비", "전기기사", "정규직"],
    },
    {
        "external_id": "sample-job-004",
        "title": "CNC 기계 가공 기술자",
        "company": "(주)정밀기계",
        "location": "인천 남동구",
        "salary": "2,800~3,800만원",
        "employment_type": "정규직",
        "deadline": "2026-05-10",
        "summary": "CNC 선반·밀링 프로그래밍 및 조작. 기계가공기능사 이상 소지자 우대.",
        "skills": "CNC선반 CNC밀링 G-code 도면해독",
        "url": "",
        "ncs_code": "15",
        "ncs_name": "기계",
        "tags": ["CNC", "기계가공", "제조", "정규직"],
    },
    {
        "external_id": "sample-job-005",
        "title": "사회복지사",
        "company": "○○복지관",
        "location": "서울 노원구",
        "salary": "2,600~3,200만원",
        "employment_type": "정규직",
        "deadline": "2026-05-25",
        "summary": "지역사회 복지 서비스 기획 및 사례관리. 사회복지사 2급 이상 필수.",
        "skills": "사례관리 지역사회조직 상담 복지서비스",
        "url": "",
        "ncs_code": "07",
        "ncs_name": "사회복지종교",
        "tags": ["사회복지사", "복지", "상담", "정규직"],
    },
    {
        "external_id": "sample-job-006",
        "title": "건축 설계 BIM 담당자",
        "company": "(주)종합건축사무소",
        "location": "서울 서초구",
        "salary": "3,000~4,200만원",
        "employment_type": "정규직",
        "deadline": "2026-05-18",
        "summary": "Revit 기반 BIM 설계 및 도면 작성. 건축기사 또는 건축산업기사 소지자 우대.",
        "skills": "Revit BIM AutoCAD ArchiCAD 건축설계",
        "url": "",
        "ncs_code": "14",
        "ncs_name": "건설",
        "tags": ["건축", "BIM", "Revit", "정규직"],
    },
    {
        "external_id": "sample-job-007",
        "title": "AI 서비스 기획자 (PM)",
        "company": "(주)AI솔루션",
        "location": "경기 판교",
        "salary": "4,000~6,000만원",
        "employment_type": "정규직",
        "deadline": "2026-05-30",
        "summary": "생성형 AI 기반 B2B 서비스 기획 및 로드맵 수립. 개발 협업 경험 우대.",
        "skills": "서비스기획 PM AI UX 데이터분석 애자일",
        "url": "",
        "ncs_code": "20",
        "ncs_name": "정보통신",
        "tags": ["PM", "AI", "서비스기획", "정규직"],
    },
    {
        "external_id": "sample-job-008",
        "title": "산업안전관리사",
        "company": "(주)대형제조",
        "location": "울산 북구",
        "salary": "3,500~4,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-12",
        "summary": "제조 현장 안전 관리 계획 수립 및 지도·감독. 산업안전기사 필수.",
        "skills": "안전관리 위험성평가 재해예방 법규",
        "url": "",
        "ncs_code": "23",
        "ncs_name": "환경에너지안전",
        "tags": ["산업안전", "안전관리", "제조", "정규직"],
    },
    {
        "external_id": "sample-job-009",
        "title": "전산회계 담당자",
        "company": "(주)중견기업",
        "location": "서울 영등포",
        "salary": "2,800~3,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-08",
        "summary": "ERP 활용 회계 전표 처리, 결산, 세무 신고 보조. 전산회계 1급 우대.",
        "skills": "전산회계 ERP 세무 재무제표 엑셀",
        "url": "",
        "ncs_code": "02",
        "ncs_name": "경영회계사무",
        "tags": ["회계", "ERP", "세무", "정규직"],
    },
    {
        "external_id": "sample-job-010",
        "title": "식품 QC 담당자",
        "company": "(주)식품회사",
        "location": "경기 오산",
        "salary": "2,800~3,500만원",
        "employment_type": "정규직",
        "deadline": "2026-05-22",
        "summary": "식품 제조 공정 품질 관리 및 미생물 검사. 식품기사 또는 산업기사 우대.",
        "skills": "품질관리 GMP 미생물검사 HACCP 식품법규",
        "url": "",
        "ncs_code": "21",
        "ncs_name": "식품가공",
        "tags": ["식품", "QC", "품질관리", "정규직"],
    },
]


def fetch_and_store(db: Session) -> tuple[int, str]:
    """Work24 채용정보를 가져와 DB에 저장."""
    settings = get_settings()
    api_key = settings.work24_api_key or settings.work24_kdt_api_key

    if not api_key:
        logger.warning("work24 jobs: no api key, using sample data")
        n = job_repo.upsert_many(db, SAMPLE_JOBS)
        return n, "sample"

    jobs = _fetch_all_pages(api_key, settings.work24_request_timeout)
    if not jobs:
        logger.warning("work24 jobs: 0 results, using sample data")
        n = job_repo.upsert_many(db, SAMPLE_JOBS)
        return n, "sample"

    n = job_repo.upsert_many(db, jobs)
    logger.info("work24 jobs: %d postings stored", n)
    return n, "work24"


def seed_sample(db: Session) -> int:
    return job_repo.upsert_many(db, SAMPLE_JOBS)


def _fetch_all_pages(api_key: str, timeout: float) -> list[dict]:
    all_items: list[dict] = []
    page = 1
    display = 100

    try:
        with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
            while True:
                params = {
                    "authKey": api_key,
                    "callTp": "L",
                    "returnType": "XML",
                    "startPage": page,
                    "display": display,
                }
                logger.info("work24 jobs page %d", page)
                resp = client.get(_BASE_URL, params=params)
                resp.raise_for_status()

                items = _parse_xml(resp.text)
                if not items:
                    break

                normalized = [_normalize(item) for item in items if isinstance(item, dict)]
                normalized = [j for j in normalized if j.get("external_id")]
                all_items.extend(normalized)
                logger.info("work24 jobs page %d: %d items (total %d)", page, len(normalized), len(all_items))

                if len(items) < display:
                    break
                page += 1

    except Exception as e:
        logger.warning("work24 jobs fetch error: %s", e)

    return all_items


def _parse_xml(xml_text: str) -> list[dict]:
    try:
        data = xmltodict.parse(xml_text)
        root = data.get("result") or data.get("response") or data.get("resultInfo") or data
        if not isinstance(root, dict):
            return []
        for key in ["srchList", "list", "items", "item", "contents"]:
            val = root.get(key)
            if val is None:
                for subroot in root.values():
                    if isinstance(subroot, dict):
                        val = subroot.get(key)
                        if val:
                            break
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                return [val]
        return []
    except Exception as e:
        logger.warning("xml parse error: %s", e)
        return []


def _normalize(raw: dict) -> dict:
    external_id = str(
        raw.get("recrutPblntSn") or raw.get("jobId") or raw.get("id") or ""
    ).strip()
    if not external_id:
        return {}

    return {
        "external_id": f"work24-{external_id}",
        "title": str(raw.get("recrutPbancTtl") or raw.get("jobNm") or "").strip(),
        "company": str(raw.get("cmpnyNm") or raw.get("companyNm") or "").strip() or None,
        "location": str(raw.get("workPlcNm") or raw.get("sido") or "").strip() or None,
        "salary": str(raw.get("srwgPay") or raw.get("salary") or "").strip() or None,
        "employment_type": str(raw.get("emplymShp") or raw.get("empType") or "").strip() or None,
        "deadline": str(raw.get("recrutPbancEndYmd") or raw.get("deadline") or "").strip() or None,
        "summary": str(raw.get("detailContents") or raw.get("jobDc") or "").strip() or None,
        "skills": str(raw.get("preferentialConditions") or raw.get("skills") or "").strip() or None,
        "url": str(raw.get("detailUrl") or raw.get("url") or "").strip() or None,
        "ncs_code": str(raw.get("ncsCd") or "").strip() or None,
        "ncs_name": str(raw.get("ncsNm") or "").strip() or None,
        "tags": _extract_tags(raw),
    }


def _extract_tags(raw: dict) -> list[str]:
    tags = []
    emp = str(raw.get("emplymShp") or "").strip()
    if emp:
        tags.append(emp)
    ncs = str(raw.get("ncsNm") or "").strip()
    if ncs:
        tags.append(ncs)
    return tags[:4]
