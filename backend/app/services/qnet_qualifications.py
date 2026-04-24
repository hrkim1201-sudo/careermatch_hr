"""Q-Net 국가기술자격 종목 목록 + 시험정보 API 클라이언트.

두 엔드포인트 모두 XML을 반환합니다.
응답 파싱에는 xmltodict를 사용합니다.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
import xmltodict
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories import qualification_repo

logger = logging.getLogger(__name__)

# Q-Net 자격구분 코드 → 한글 레이블
_QUAL_TYPE_MAP = {
    "T": "기술사", "E": "기능장", "I": "기사",
    "S": "산업기사", "K": "기능사", "C": "서비스",
}

# 자격구분별 시험정보 엔드포인트 (InquiryTestInformationNTQSVC)
_EXAM_INFO_FUNCS = {
    "기술사": "getEngineerInformationList",
    "기능장": "getMasterCraftsmanInformationList",
    "기사": "getCraftsmanEngineerInformationList",
    "산업기사": "getCraftsmanEngineerInformationList",
    "기능사": "getCraftsmanInformationList",
}


def fetch_and_store(db: Session) -> tuple[int, int]:
    """자격종목 목록 + 시험일정을 가져와 DB에 저장. (종목 수, 일정 수) 반환."""
    settings = get_settings()
    timeout = httpx.Timeout(settings.qnet_request_timeout)

    with httpx.Client(timeout=timeout) as client:
        quals = _fetch_qual_list(client, settings)
        qual_count = qualification_repo.upsert_qualifications(db, quals)
        logger.info("qualifications upserted: %d", qual_count)

        schedules = _fetch_exam_schedules(client, settings)
        sched_count = qualification_repo.upsert_schedules(db, schedules)
        logger.info("exam schedules upserted: %d", sched_count)

    return qual_count, sched_count


def _fetch_qual_list(client: httpx.Client, settings) -> list[dict]:
    """국가기술자격 종목 목록 조회 (InquiryListNationalQualifcationSVC)."""
    results: list[dict] = []
    try:
        resp = client.get(
            settings.qnet_qual_list_url + "/getList",
            params={"serviceKey": settings.qnet_api_key_decoded},
        )
        resp.raise_for_status()
        data = xmltodict.parse(resp.text)
        items = _extract_items(data)
        for item in items:
            payload = _normalize_qual(item)
            if payload.get("qual_code"):
                results.append(payload)
    except Exception as e:
        logger.warning("Q-Net qual list fetch failed: %s", e)
    return results


def _fetch_exam_schedules(client: httpx.Client, settings) -> list[dict]:
    """종목별 시험 시행일정 조회 (InquiryTestInformationNTQSVC)."""
    results: list[dict] = []
    # 기사·산업기사·기능사 합산
    for func_name in [
        "getCraftsmanEngineerInformationList",
        "getCraftsmanInformationList",
        "getEngineerInformationList",
        "getMasterCraftsmanInformationList",
    ]:
        try:
            resp = client.get(
                settings.qnet_exam_info_url + f"/{func_name}",
                params={"serviceKey": settings.qnet_api_key_decoded},
            )
            resp.raise_for_status()
            data = xmltodict.parse(resp.text)
            items = _extract_items(data)
            for item in items:
                payload = _normalize_schedule(item)
                if payload.get("qual_code"):
                    results.append(payload)
        except Exception as e:
            logger.warning("Q-Net exam schedule fetch failed [%s]: %s", func_name, e)
    return results


def _extract_items(data: dict) -> list[dict]:
    """xmltodict 결과에서 item 목록을 안전하게 꺼냄."""
    try:
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {})
        if not items:
            return []
        item = items.get("item", [])
        if isinstance(item, dict):
            return [item]
        return item or []
    except Exception:
        return []


def _normalize_qual(raw: dict[str, Any]) -> dict:
    qual_type_code = str(raw.get("grdCd") or "")
    return {
        "qual_code": str(raw.get("jmCd") or "").strip(),
        "qual_name": str(raw.get("jmNm") or "").strip(),
        "qual_type": _QUAL_TYPE_MAP.get(qual_type_code, qual_type_code) or None,
        "job_field_code": str(raw.get("mdobCd") or "").strip() or None,
        "job_field_name": str(raw.get("mdobNm") or "").strip() or None,
        "mid_job_field": str(raw.get("dobNm") or "").strip() or None,
        "related_jobs": str(raw.get("relJob") or "").strip() or None,
        "ministry": str(raw.get("insttNm") or "").strip() or None,
        "detail_url": f"https://www.q-net.or.kr/crf005.do?id=crf00503&jmInfoTop_examInstiCd=1&jmInfoTop_jmCd={raw.get('jmCd', '')}",
    }


def _normalize_schedule(raw: dict[str, Any]) -> dict:
    return {
        "qual_code": str(raw.get("jmCd") or "").strip(),
        "qual_name": str(raw.get("jmNm") or "").strip(),
        "year": str(raw.get("implYy") or "").strip() or None,
        "round_no": str(raw.get("implSeq") or "").strip() or None,
        "written_reg_start": _safe_date(raw.get("docRegStartDt")),
        "written_reg_end": _safe_date(raw.get("docRegEndDt")),
        "written_exam_start": _safe_date(raw.get("docExamStartDt")),
        "written_exam_end": _safe_date(raw.get("docExamEndDt")),
        "written_result_date": _safe_date(raw.get("docPassDt")),
        "practical_reg_start": _safe_date(raw.get("pracRegStartDt")),
        "practical_reg_end": _safe_date(raw.get("pracRegEndDt")),
        "practical_exam_start": _safe_date(raw.get("pracExamStartDt")),
        "practical_exam_end": _safe_date(raw.get("pracExamEndDt")),
        "practical_result_date": _safe_date(raw.get("pracPassDt")),
        "source": "qnet",
    }


def _safe_date(val: Any) -> str | None:
    if not val:
        return None
    s = str(val).strip().replace("-", "").replace(".", "")
    return s[:8] if len(s) >= 8 else s or None
