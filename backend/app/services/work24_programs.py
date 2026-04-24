"""Work24 고용24 Open API 클라이언트.

실제 API 스펙:
  Endpoint : https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do
  Params   : authKey, callTp(L=목록), returnType(XML), startPage(1~1000), display(1~100)
  Response : XML
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
import xmltodict
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories import program_repo
from app.services.program_catalog import SAMPLE_PROGRAMS

logger = logging.getLogger(__name__)

# 실제 Work24 엔드포인트
_BASE_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"

# 유형별 occupation 코드 (Work24 직종코드 — 없으면 전체 조회)
_TYPE_PARAMS: dict[str, dict] = {
    "kdt":           {"srchTraProcessTitle": "", "srchTraArea1": ""},
    "apprenticeship": {"srchTraProcessTitle": "", "srchTraArea1": ""},
    "capability":    {"srchTraProcessTitle": "", "srchTraArea1": ""},
}

_CATEGORY_MAP = {
    "kdt":            "국민내일배움카드 훈련과정",
    "apprenticeship": "일학습병행훈련과정",
    "capability":     "구직자취업역량 강화프로그램",
}


def fetch_and_store(db: Session) -> tuple[int, str]:
    settings = get_settings()
    all_programs: list[dict] = []
    any_success = False

    fetch_targets = [
        ("kdt",            settings.work24_kdt_api_key or settings.work24_api_key),
        ("apprenticeship", settings.work24_apprentice_api_key or settings.work24_api_key),
        ("capability",     settings.work24_capability_api_key or settings.work24_api_key),
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
        logger.warning("work24: all endpoints returned 0, fallback to sample")
        n = program_repo.upsert_many(db, SAMPLE_PROGRAMS)
        return n, "sample"

    n = program_repo.upsert_many(db, all_programs)
    logger.info("work24: total %d programs stored", n)
    return n, "work24"


def _fetch_all_pages(prog_type: str, api_key: str, timeout: float) -> list[dict]:
    """XML 응답을 파싱하며 전체 페이지 수집."""
    all_items: list[dict] = []
    page = 1
    display = 100  # 최대

    try:
        with httpx.Client(timeout=httpx.Timeout(timeout)) as client:
            while True:
                params = {
                    "authKey": api_key,
                    "callTp": "L",
                    "returnType": "XML",
                    "startPage": page,
                    "display": display,
                    **_TYPE_PARAMS.get(prog_type, {}),
                }
                logger.info("work24 [%s] page %d", prog_type, page)
                resp = client.get(_BASE_URL, params=params)
                resp.raise_for_status()

                items = _parse_xml(resp.text)
                if not items:
                    logger.info("work24 [%s] page %d: empty → done", prog_type, page)
                    break

                normalized = [_normalize(item, prog_type) for item in items]
                normalized = [p for p in normalized if p.get("external_id")]
                all_items.extend(normalized)
                logger.info(
                    "work24 [%s] page %d: %d items (total %d)",
                    prog_type, page, len(normalized), len(all_items)
                )

                if len(items) < display:
                    break
                page += 1

    except Exception as e:
        logger.warning("work24 [%s] fetch error page %d: %s", prog_type, page, e)

    return all_items


def _parse_xml(xml_text: str) -> list[dict]:
    """Work24 XML 응답에서 아이템 목록 파싱."""
    try:
        data = xmltodict.parse(xml_text)
        # 가능한 응답 구조 탐색
        root = data.get("result") or data.get("response") or data.get("resultInfo") or data
        if not isinstance(root, dict):
            return []

        for key in ["srchList", "list", "items", "item", "content", "contents"]:
            val = root.get(key)
            if val is None:
                # 한 단계 더 안으로
                for subroot in root.values():
                    if isinstance(subroot, dict):
                        val = subroot.get(key)
                        if val is not None:
                            break
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                return [val]

        return []
    except Exception as e:
        logger.warning("xml parse error: %s | preview: %s", e, xml_text[:300])
        return []


def _normalize(raw: dict, prog_type: str) -> dict:
    external_id = str(
        raw.get("trprId") or raw.get("recrutPblntSn") or
        raw.get("instCd") or raw.get("id") or ""
    ).strip()
    if not external_id:
        return {}

    return {
        "title": str(raw.get("trprNm") or raw.get("recrutPbancTtl") or raw.get("title") or "").strip(),
        "provider": str(raw.get("instNm") or raw.get("companyNm") or "").strip() or None,
        "program_type": prog_type,
        "category": _CATEGORY_MAP.get(prog_type, "국민내일배움카드 훈련과정"),
        "location": _parse_location(raw),
        "summary": str(raw.get("contents") or raw.get("trprDc") or raw.get("detailContents") or "").strip() or None,
        "target_audience": str(raw.get("trainTarget") or raw.get("acntngMth") or "").strip() or None,
        "skills": str(raw.get("ncsCd") or raw.get("occupation") or "").strip() or None,
        "benefits": str(raw.get("subTit") or "").strip() or None,
        "schedule": _parse_schedule(raw),
        "tuition": str(raw.get("courseMan") or raw.get("srwgPay") or "").strip() or None,
        "url": str(raw.get("titleLink") or raw.get("detailUrl") or "").strip() or None,
        "source": "work24",
        "external_id": f"{prog_type}-{external_id}",
        "ncs_code": str(raw.get("ncsCd") or "").strip() or None,
        "ncs_name": str(raw.get("ncsNm") or "").strip() or None,
        "tags": _extract_tags(raw, prog_type),
    }


def _parse_location(raw: dict) -> str | None:
    parts = [
        str(raw.get("workPlcNm") or raw.get("sido") or "").strip(),
        str(raw.get("sigunguNm") or raw.get("sigungu") or "").strip(),
    ]
    loc = " ".join(p for p in parts if p)
    return loc or None


def _parse_schedule(raw: dict) -> str | None:
    start = str(raw.get("traStartDate") or raw.get("recrutPbancBgngYmd") or "").strip()
    end   = str(raw.get("traEndDate")   or raw.get("recrutPbancEndYmd")  or "").strip()
    if start and end:
        return f"{start} ~ {end}"
    return start or None


def _extract_tags(raw: dict, prog_type: str) -> list[str]:
    tags: list[str] = []
    label = {"kdt": "내일배움카드", "apprenticeship": "일학습병행", "capability": "취업역량강화"}
    if prog_type in label:
        tags.append(label[prog_type])
    ncs = str(raw.get("ncsNm") or "").strip()
    if ncs:
        tags.append(ncs)
    return tags[:5]
