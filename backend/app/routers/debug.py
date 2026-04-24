"""개발용 디버그 엔드포인트."""
import logging
from typing import Any

import httpx
from fastapi import APIRouter
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

_BASE_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"


@router.get("/work24/raw")
def work24_raw_response() -> dict[str, Any]:
    """Work24 실제 API 응답 확인용."""
    settings = get_settings()

    keys_present = {
        "work24_api_key":           bool(settings.work24_api_key),
        "work24_kdt_api_key":       bool(settings.work24_kdt_api_key),
        "work24_apprentice_api_key": bool(settings.work24_apprentice_api_key),
        "work24_capability_api_key": bool(settings.work24_capability_api_key),
    }

    test_keys = [
        ("kdt",         settings.work24_kdt_api_key or settings.work24_api_key),
        ("capability",  settings.work24_capability_api_key or settings.work24_api_key),
    ]

    results = {}
    for name, api_key in test_keys:
        if not api_key:
            results[name] = {"error": "no api key"}
            continue
        try:
            with httpx.Client(timeout=12.0) as client:
                resp = client.get(
                    _BASE_URL,
                    params={
                        "authKey": api_key,
                        "callTp": "L",
                        "returnType": "XML",
                        "startPage": 1,
                        "display": 3,
                    },
                )
                results[name] = {
                    "status_code": resp.status_code,
                    "url": str(resp.url),
                    "body_preview": resp.text[:3000],
                }
        except Exception as e:
            results[name] = {"error": str(e)}

    return {"keys_present": keys_present, "results": results}
