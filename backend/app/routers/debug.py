"""개발용 디버그 엔드포인트. 실제 Work24 API 응답을 그대로 반환합니다."""
import logging
from typing import Any

import httpx
from fastapi import APIRouter
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/work24/raw")
def work24_raw_response() -> dict[str, Any]:
    """Work24 API 실제 응답을 그대로 반환합니다. 필드명 확인용."""
    settings = get_settings()

    # 사용 가능한 키 확인
    keys = {
        "work24_api_key": bool(settings.work24_api_key),
        "work24_kdt_api_key": bool(settings.work24_kdt_api_key),
        "work24_apprentice_api_key": bool(settings.work24_apprentice_api_key),
        "work24_capability_api_key": bool(settings.work24_capability_api_key),
    }

    results = {}

    # 엔드포인트별 테스트
    test_cases = [
        {
            "name": "kdt_v1",
            "url": "https://www.work24.go.kr/cm/openApi/call/wk/workApiWkKdt.do",
            "key": settings.work24_kdt_api_key or settings.work24_api_key,
        },
        {
            "name": "kdt_v2",
            "url": "https://www.work24.go.kr/cm/openApi/call/wk/workOpenApiList.do",
            "key": settings.work24_kdt_api_key or settings.work24_api_key,
        },
        {
            "name": "capability",
            "url": "https://www.work24.go.kr/cm/openApi/call/wk/workApiWkCapability.do",
            "key": settings.work24_capability_api_key or settings.work24_api_key,
        },
    ]

    for case in test_cases:
        if not case["key"]:
            results[case["name"]] = {"error": "no api key"}
            continue
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    case["url"],
                    params={
                        "authKey": case["key"],
                        "returnType": "JSON",
                        "pageSize": 3,
                        "pageNum": 1,
                        "outType": "1",
                    },
                )
                results[case["name"]] = {
                    "status_code": resp.status_code,
                    "url": str(resp.url),
                    # 응답 앞부분 2000자만
                    "body_preview": resp.text[:2000],
                }
        except Exception as e:
            results[case["name"]] = {"error": str(e)}

    return {
        "keys_present": keys,
        "results": results,
    }
