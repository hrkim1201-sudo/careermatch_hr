"""Work24 고용24 Open API 클라이언트.

프로그램 유형별로 별도 API 키와 엔드포인트를 사용합니다.
  - KDT          : 국민내일배움카드 훈련과정
  - Apprenticeship: 일학습병행훈련과정
  - Capability   : 구직자취업역량 강화프로그램

API 호출 실패 시 샘플 데이터로 fallback합니다.
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

# Work24 API 엔드포인트
_ENDPOINTS = {
    "kdt": "https://www.work24.go.kr/cm/openApi/call/wk/workApiWkKdt.do",
    "apprenticeship": "https://www.work24.go.kr/cm/openApi/call/wk/workApiWkApprenticeship.do",
    "capability": "https://www.work24.go.kr/cm/openApi/call/wk/workApiWkCapability.do",
}

# 카테고리 레이블
_CATEGORY_MAP = {
    "kdt": "국민내일배움카드 훈련과정",
    "apprenticeship": "일학습병행훈련과정",
    "capability": "구직자취업역량 강화프로그램",
}


def fetch_and_store(db: Session) -> tuple[int, str]:
    """Work24 API에서 프로그램을 가져와 DB에 저장. (count, source) 반환."""
    settings = get_settings()
    all_programs: list[dict] = []
    any_success = False

    # KDT 훈련과정
    if settings.work24_kdt_api_key:
        programs = _fetch_programs(
            "kdt",
            settings.work24_kdt_api_key,
            settings.work24_request_timeout,
        )
        if programs:
            all_programs.extend(programs)
            any_success = True
            logger.info("work24 kdt: %d programs fetched", len(programs))

    # 일학습병행
    if settings.work24_apprentice_api_key:
        programs = _fetch_programs(
            "apprenticeship",
            settings.work24_apprentice_api_key,
            settings.work24_request_timeout,
        )
        if programs:
            all_programs.extend(programs)
            any_success = True
            logger.info("work24 apprenticeship: %d programs fetched", len(programs))

    # 구직자취업역량강화
    if settings.work24_capability_api_key:
        programs = _fetch_programs(
            "capability",
            settings.work24_capability_api_key,
            settings.work24_request_timeout,
        )
        if programs:
            all_programs.extend(programs)
            any_success = True
            logger.info("work24 capability: %d programs fetched", len(programs))

    # 일반 키 fallback (kdt 엔드포인트에 시도)
    if not any_success and settings.work24_api_key:
        programs = _fetch_programs(
            "kdt",
            settings.work24_api_key,
            settings.work24_request_timeout,
        )
        if programs:
            all_programs.extend(programs)
            any_success = True

    if not any_success or not all_programs:
        logger.warning("work24 all endpoints failed, falling back to sample data")
        n = program_repo.upsert_many(db, SAMPLE_PROGRAMS)
        return n, "sample"

    n = program_repo.upsert_many(db, all_programs)
    return n, "work24"


def _fetch_programs(prog_type: str, api_key: str, timeout: float) -> list[dict]:
    """단일 Work24 엔드포인트에서 프로그램 목록을 가져옵니다."""
    url = _ENDPOINTS.get(prog_type, _ENDPOINTS["kdt"])
    all_items: list[dict] = []
    page = 1
    page_size = 100

    try:
        with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
            while True:
                params = {
                    "authKey": api_key,
                    "returnType": "JSON",
                    "pageSize": page_size,
                    "pageNum": page,
                    "outType": "1",  # 목록
                }
                resp = client.get(url, params=params)
                resp.raise_for_status()

                data = resp.json()
                items = _extract_items(data)

                if not items:
                    break

                normalized = [
                    _normalize(item, prog_type)
                    for item in items
                    if isinstance(item, dict)
                ]
                normalized = [p for p in normalized if p.get("external_id")]
                all_items.extend(normalized)

                # 마지막 페이지 체크
                if len(items) < page_size:
                    break
                page += 1

                # 최대 10페이지 (1000개)
                if page > 10:
                    break

    except Exception as e:
        logger.warning("work24 fetch failed [%s]: %s", prog_type, e)

    return all_items


def _extract_items(data: Any) -> list[dict]:
    """Work24 JSON 응답에서 아이템 목록 추출."""
    if not isinstance(data, dict):
        return []
    # 가능한 응답 구조들
    for key in ["srchList", "returnUseYn", "contents", "list", "data", "items"]:
        val = data.get(key)
        if isinstance(val, list):
            return val
        if isinstance(val, dict):
            for subkey in ["srchList", "list", "items"]:
                sub = val.get(subkey)
                if isinstance(sub, list):
                    return sub
    return []


def _normalize(raw: dict, prog_type: str) -> dict:
    """Work24 응답 필드 → 내부 스키마 변환."""
    # Work24 API 필드명 (실제 응답에 따라 조정 필요)
    external_id = (
        str(raw.get("trprId") or raw.get("instCd") or raw.get("courseId") or "").strip()
    )
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
        online = raw.get("realClassYn") or raw.get("onlineYn") or ""
        if str(online).upper() in ("Y", "1", "TRUE"):
            return "온라인"
    return loc or None


def _parse_schedule(raw: dict) -> str | None:
    start = str(raw.get("traStartDate") or raw.get("startDate") or "").strip()
    end = str(raw.get("traEndDate") or raw.get("endDate") or "").strip()
    if start and end:
        return f"{start} ~ {end}"
    if start:
        return start
    return str(raw.get("schedule") or "").strip() or None


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
