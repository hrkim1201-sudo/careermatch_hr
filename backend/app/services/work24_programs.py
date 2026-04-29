"""Work24 훈련과정 API 클라이언트 (모든 유형 지원).

API 키별 서비스:
  국민내일배움카드   : 608d3aed-...  → callOpenApiSvcInfo150L01.do
  사업주훈련         : 15f629cc-...  → callOpenApiSvcInfo160L01.do
  컨소시엄훈련       : e4d1b3dc-...  → callOpenApiSvcInfo170L01.do
  일학습병행         : ff14ab69-...  → callOpenApiSvcInfo180L01.do
  구직자취업역량강화  : 99ae5f84-...  → callOpenApiSvcInfo190L01.do
"""
from __future__ import annotations
import logging
import urllib.parse
from typing import Any
import httpx
import xmltodict
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.repositories import program_repo
from app.services.program_catalog import SAMPLE_PROGRAMS, seed_sample_programs

logger = logging.getLogger(__name__)

_BASE = "https://www.work24.go.kr/cm/openApi/call/wk"

_ENDPOINTS = [
    ("kdt",           "callOpenApiSvcInfo150L01.do", "work24_kdt_api_key",         "국민내일배움카드 훈련과정"),
    ("bizowner",      "callOpenApiSvcInfo160L01.do", "work24_bizowner_api_key",     "사업주훈련과정"),
    ("consortium",    "callOpenApiSvcInfo170L01.do", "work24_consortium_api_key",   "국가인적자원개발 컨소시엄"),
    ("apprenticeship","callOpenApiSvcInfo180L01.do", "work24_apprentice_api_key",   "일학습병행훈련과정"),
    ("capability",    "callOpenApiSvcInfo190L01.do", "work24_capability_api_key",   "구직자취업역량 강화프로그램"),
]

_CATEGORY_MAP = {
    "kdt":            "국민내일배움카드 훈련과정",
    "bizowner":       "사업주훈련과정",
    "consortium":     "국가인적자원개발 컨소시엄",
    "apprenticeship": "일학습병행훈련과정",
    "capability":     "구직자취업역량 강화프로그램",
}


def fetch_and_store(db: Session) -> tuple[int, str]:
    settings = get_settings()
    all_programs: list[dict] = []
    any_success = False

    for prog_type, endpoint, key_attr, category in _ENDPOINTS:
        api_key = getattr(settings, key_attr, "") or settings.work24_api_key
        if not api_key:
            continue
        programs = _fetch_pages(prog_type, endpoint, api_key, category, settings.work24_request_timeout)
        if programs:
            all_programs.extend(programs)
            any_success = True
            logger.info("work24 [%s]: %d programs", prog_type, len(programs))

    if not any_success or not all_programs:
        logger.warning("work24 programs: all failed, fallback to sample")
        n = program_repo.upsert_many(db, SAMPLE_PROGRAMS)
        return n, "sample"

    n = program_repo.upsert_many(db, all_programs)
    return n, "work24"


def _fetch_pages(prog_type: str, endpoint: str, api_key: str, category: str, timeout: float) -> list[dict]:
    results: list[dict] = []
    url = f"{_BASE}/{endpoint}"
    page = 1
    try:
        with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
            while True:
                resp = client.get(url, params={
                    "authKey": api_key, "returnType": "XML",
                    "startPage": page, "display": 100,
                })
                resp.raise_for_status()
                items = _parse_xml(resp.text)
                if not items:
                    break
                for item in items:
                    p = _normalize(item, prog_type, category)
                    if p.get("external_id"):
                        results.append(p)
                if len(items) < 100:
                    break
                page += 1
    except Exception as e:
        logger.warning("work24 [%s] error: %s", prog_type, e)
    return results


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


def _normalize(raw: dict, prog_type: str, category: str) -> dict:
    eid = str(raw.get("trprId") or raw.get("id") or "").strip()
    if not eid:
        return {}
    title = str(raw.get("trprNm") or raw.get("title") or "").strip()
    encoded = urllib.parse.quote(title)
    url = f"https://www.work24.go.kr/wk/a/b/1300/retriveSrchTraPbancInfoList.do?schText={encoded}"
    return {
        "title": title,
        "provider": str(raw.get("instNm") or "").strip() or None,
        "program_type": prog_type,
        "category": category,
        "location": str(raw.get("workPlcNm") or raw.get("sido") or "").strip() or None,
        "summary": str(raw.get("contents") or raw.get("trprDc") or "").strip() or None,
        "target_audience": str(raw.get("trainTarget") or "").strip() or None,
        "skills": str(raw.get("ncsCd") or "").strip() or None,
        "benefits": None,
        "schedule": _parse_schedule(raw),
        "tuition": str(raw.get("courseMan") or "").strip() or None,
        "url": url,
        "source": "work24",
        "external_id": f"{prog_type}-{eid}",
        "ncs_code": str(raw.get("ncsCd") or "").strip() or None,
        "ncs_name": str(raw.get("ncsNm") or "").strip() or None,
        "tags": [category[:6]],
    }


def _parse_schedule(raw: dict) -> str | None:
    s = str(raw.get("traStartDate") or "").strip()
    e = str(raw.get("traEndDate") or "").strip()
    if s and e:
        return f"{s} ~ {e}"
    return s or None
