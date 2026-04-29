"""Work24 채용정보 서비스.

실데이터: Work24 채용정보 API (bfa4cbc5-...)
샘플: 4400개 직무 분야별 가상 채용공고 (저작권 안전)
"""
from __future__ import annotations
import json
import logging
import urllib.parse
from pathlib import Path
import httpx
import xmltodict
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.repositories import job_repo

logger = logging.getLogger(__name__)
_BASE_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"

# 샘플 데이터 로드 (외부 JSON에서)
_SAMPLE_PATH = Path(__file__).parent / "job_samples.json"


def _load_samples() -> list[dict]:
    if _SAMPLE_PATH.exists():
        with open(_SAMPLE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def fetch_and_store(db: Session) -> tuple[int, str]:
    settings = get_settings()
    api_key = settings.work24_jobs_api_key or settings.work24_api_key

    if api_key:
        jobs = _fetch_all_pages(api_key, settings.work24_request_timeout)
        if jobs:
            n = job_repo.upsert_many(db, jobs)
            logger.info("work24 jobs: %d real postings stored", n)
            return n, "work24"

    logger.info("work24 jobs: using sample data")
    samples = _load_samples()
    if not samples:
        samples = _BUILTIN_SAMPLES
    n = job_repo.upsert_many(db, samples)
    return n, "work24"


def seed_sample(db: Session) -> int:
    samples = _load_samples()
    if not samples:
        samples = _BUILTIN_SAMPLES
    return job_repo.upsert_many(db, samples)


def _fetch_all_pages(api_key: str, timeout: float) -> list[dict]:
    all_items: list[dict] = []
    page = 1
    try:
        with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
            while True:
                resp = client.get(_BASE_URL, params={
                    "authKey": api_key, "callTp": "L",
                    "returnType": "XML", "startPage": page, "display": 100,
                })
                resp.raise_for_status()
                items = _parse_xml(resp.text)
                if not items:
                    break
                normalized = [_normalize(i) for i in items if isinstance(i, dict)]
                all_items.extend(j for j in normalized if j.get("external_id"))
                if len(items) < 100:
                    break
                page += 1
    except Exception as e:
        logger.warning("work24 jobs fetch: %s", e)
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
                for v in root.values():
                    if isinstance(v, dict):
                        val = v.get(key)
                        if val:
                            break
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                return [val]
    except Exception as e:
        logger.warning("xml parse: %s", e)
    return []


def _normalize(raw: dict) -> dict:
    eid = str(raw.get("recrutPblntSn") or raw.get("id") or "").strip()
    if not eid:
        return {}
    title = str(raw.get("recrutPbancTtl") or "").strip()
    url = f"https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpInfo.do?wantedAuthNo={eid}"
    return {
        "external_id": f"work24-{eid}",
        "title": title,
        "company": str(raw.get("cmpnyNm") or "").strip() or None,
        "location": str(raw.get("workPlcNm") or raw.get("sido") or "").strip() or None,
        "salary": str(raw.get("srwgPay") or "").strip() or None,
        "employment_type": str(raw.get("emplymShp") or "").strip() or None,
        "deadline": str(raw.get("recrutPbancEndYmd") or "").strip() or None,
        "summary": str(raw.get("detailContents") or "").strip() or None,
        "skills": str(raw.get("preferentialConditions") or "").strip() or None,
        "url": url,
        "ncs_code": str(raw.get("ncsCd") or "").strip() or None,
        "ncs_name": str(raw.get("ncsNm") or "").strip() or None,
        "tags": [str(raw.get("emplymShp") or "정규직")][:4],
    }


# 내장 샘플 (JSON 없을 경우 fallback)
_BUILTIN_SAMPLES: list[dict] = [
    {
        "external_id": "w24-sample-it-0001",
        "title": "Python 백엔드 개발자 (신입/경력)",
        "company": "IT 솔루션 기업",
        "location": "서울 강남구",
        "salary": "4,000 ~ 7,000만원",
        "employment_type": "정규직",
        "deadline": "2026-06-30",
        "summary": "FastAPI 기반 REST API 설계 및 구현. PostgreSQL·Redis 운용, Docker 환경 개발.",
        "skills": "Python FastAPI PostgreSQL Redis Docker",
        "url": "https://www.work24.go.kr/wk/a/b/1200/retriveSrchEmpInfoList.do?schTxt=Python+백엔드",
        "ncs_code": "20", "ncs_name": "정보통신",
        "tags": ["백엔드", "Python", "정규직"],
    },
]
