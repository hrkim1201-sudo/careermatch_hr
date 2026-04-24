"""Work24 고용24 Open API 클라이언트.

프로그램 유형별로 별도 API 키와 엔드포인트를 사용합니다.
페이지네이션으로 전체 데이터를 모두 수집합니다.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories import program_repo
from app.services.program_catalog import SAMPLE_PROGRAMS

logger = logging.getLogger(__name__)

_ENDPOINTS = {
    "kdt": "https://www.work24.go.kr/cm/openApi/call/wk/workApiWkKdt.do",
    "apprenticeship": "https://www.work24.go.kr/cm/openApi/call/wk/workApiWkApprenticeship.do",
    "capability": "https://www.work24.go.kr/cm/openApi/call/wk/workApiWkCapability.do",
}

_CATEGORY_MAP = {
    "kdt": "국민내일배움카드 훈련과정",
    "apprenticeship": "일학습병행훈련과정",
    "capability": "구직자취업역량 강화프로그램",
}


def fetch_and_store(db: Session) -> tuple[int, str]:
    settings = get_settings()
    all_programs: list[dict] = []
    any_success = False

    fetch_targets = [
        ("kdt",           settings.work24_kdt_api_key or settings.work24_api_key),
        ("apprenticeship", settings.work24_apprentice_api_key or settings.work24_api_key),
        ("capability",    settings.work24_capability_api_key or settings.work24_api_key),
    ]

    for prog_type, api_key in fetch_targets:
        if not api_key:
            logger.info("work24 [%s]: no api key, skipping", prog_type)
            continue
        programs = _fetch_all_pages(prog_type, api_key, settings.work24_request_timeout)
        if programs:
            all_programs.extend(programs)
            any_success = True
            logger.info("work24 [%s]: %d programs fetched", prog_type, len(programs))
        else:
            logger.warning("work24 [%s]: 0 programs returned", prog_type)

    if not any_success or not all_programs:
        logger.warning("work24: all endpoints returned 0 results, fallback to sample")
        n = program_repo.upsert_many(db, SAMPLE_PROGRAMS)
        return n, "sample"

    n = program_repo.upsert_many(db, all_programs)
    logger.info("work24: total %d programs stored", n)
    return n, "work24"


def _fetch_all_pages(prog_type: str, api_key: str, timeout: float) -> list[dict]:
    """페이지네이션으로 전체 데이터 수집. 페이지 제한 없음."""
    url = _ENDPOINTS.get(prog_type, _ENDPOINTS["kdt"])
    all_items: list[dict] = []
    page = 1
    page_size = 100  # 한 번에 가져올 최대 건수

    try:
        with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
            while True:
                params = {
                    "authKey": api_key,
                    "returnType": "JSON",
                    "pageSize": page_size,
                    "pageNum": page,
                    "outType": "1",
                }
                logger.info("work24 [%s] fetching page %d", prog_type, page)
                resp = client.get(url, params=params)
                resp.raise_for_status()

                data = resp.json()
                items = _extract_items(data)

                if not items:
                    logger.info("work24 [%s] page %d: empty, done", prog_type, page)
                    break

                normalized = [
                    _normalize(item, prog_type)
                    for item in items
                    if isinstance(item, dict)
                ]
                normalized = [p for p in normalized if p.get("external_id")]
                all_items.extend(normalized)
                logger.info(
                    "work24 [%s] page %d: %d items (total %d)",
                    prog_type, page, len(normalized), len(all_items)
                )

                # 마지막 페이지 확인
                if len(items) < page_size:
                    logger.info("work24 [%s]: last page reached at page %d", prog_type, page)
                    break

                page += 1

    except Exception as e:
        logger.warning("work24 [%s] fetch error at page %d: %s", prog_type, page, e)

    return all_items


def _extract_items(data: Any) -> list[dict]:
    if not isinstance(data, dict):
        return []
    for key in ["srchList", "returnUseYn", "contents", "list", "data", "items", "result"]:
        val = data.get(key)
        if isinstance(val, list):
            return val
        if isinstance(val, dict):
            for subkey in ["srchList", "list", "items", "contents"]:
                sub = val.get(subkey)
                if isinstance(sub, list):
                    return sub
    return []


def _normalize(raw: dict, prog_type: str) -> dict:
    external_id = str(
        raw.get("trprId") or raw.get("instCd") or raw.get("courseId") or ""
    ).strip()
    if not external_id:
        return {}

    return {
        "title": str(raw.get("trprNm") or raw.get("courseName") or raw.get("title") or "").strip(),
        "provider": str(raw.get("instNm") or raw.get("providerName") or "").strip() or None,
        "program_type": prog_type,
        "category": _CATEGORY_MAP.get(prog_type, "국민내일배움카드 훈련과정"),
        "location": _parse_location(raw),
        "summary": str(raw.get("contents") or raw.get("summary") or raw.get("trprDc") or "").strip() or None,
        "target_audience": str(raw.get("trainTarget") or raw.get("targetAudience") or "").strip() or None,
        "skills": str(raw.get("ncsCd") or raw.get("skills") or "").strip() or None,
        "benefits": str(raw.get("subTit") or raw.get("benefits") or "").strip() or None,
        "schedule": _parse_schedule(raw),
        "tuition": str(raw.get("courseMan") or raw.get("tuition") or "").strip() or None,
        "url": str(raw.get("titleLink") or raw.get("url") or "").strip() or None,
        "source": "work24",
        "external_id": f"{prog_type}-{external_id}",
        "ncs_code": str(raw.get("ncsCd") or "").strip() or None,
        "ncs_name": str(raw.get("ncsNm") or "").strip() or None,
        "tags": _extract_tags(raw, prog_type),
    }


def _parse_location(raw: dict) -> str | None:
    parts = [
        str(raw.get("address") or "").strip(),
        str(raw.get("sido") or "").strip(),
        str(raw.get("sigungu") or "").strip(),
    ]
    loc = " ".join(p for p in parts if p)
    if not loc:
        online = str(raw.get("realClassYn") or raw.get("onlineYn") or "")
        if online.upper() in ("Y", "1", "TRUE"):
            return "온라인"
    return loc or None


def _parse_schedule(raw: dict) -> str | None:
    start = str(raw.get("traStartDate") or raw.get("startDate") or "").strip()
    end = str(raw.get("traEndDate") or raw.get("endDate") or "").strip()
    if start and end:
        return f"{start} ~ {end}"
    return start or str(raw.get("schedule") or "").strip() or None


def _extract_tags(raw: dict, prog_type: str) -> list[str]:
    tags = []
    if prog_type == "kdt":
        tags.append("내일배움카드")
    elif prog_type == "apprenticeship":
        tags.append("일학습병행")
    elif prog_type == "capability":
        tags.append("취업역량강화")
    ncs = str(raw.get("ncsNm") or "").strip()
    if ncs:
        tags.append(ncs)
    return tags[:5]
