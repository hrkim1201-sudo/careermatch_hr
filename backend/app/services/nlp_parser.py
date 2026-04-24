"""자연어 입력에서 지역, 스킬, 온라인 여부를 파싱합니다.

OpenAI가 있으면 GPT로 파싱, 없으면 키워드 규칙 기반 fallback.
"""
from __future__ import annotations

import json
import logging
import re

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def parse_user_input(prompt: str) -> dict:
    """
    Returns:
        {
            "prompt": str,          # 원본 입력
            "skills": list[str],    # 추출된 스킬/키워드
            "location": str,        # 추출된 지역 (없으면 "")
            "online": bool,         # 온라인 선호 여부
            "parsed_by": str        # "openai" | "rule"
        }
    """
    settings = get_settings()
    if settings.openai_api_key:
        try:
            return _openai_parse(prompt, settings)
        except Exception as e:
            logger.warning("openai parse failed, fallback to rule: %s", e)
    return _rule_parse(prompt)


def _openai_parse(prompt: str, settings) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key, timeout=10.0)
    system = """사용자의 취업·훈련 관련 자연어 입력을 분석해서 JSON으로 반환하세요.
반드시 아래 형식만 출력하세요. 다른 텍스트나 마크다운 없이 JSON만 출력.

{
  "skills": ["추출된 기술/직무 키워드 최대 5개"],
  "location": "추출된 지역명 (없으면 빈 문자열)",
  "online": true or false
}

규칙:
- skills: 직무명, 기술스택, 자격증명, 분야명 등
- location: 시/도/구 단위 지역명 (서울, 부산, 강남, 판교 등)
- online: '온라인', '비대면', '재택' 언급 시 true"""

    res = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    raw = res.choices[0].message.content or "{}"
    parsed = json.loads(raw)
    return {
        "prompt": prompt,
        "skills": parsed.get("skills") or [],
        "location": str(parsed.get("location") or "").strip(),
        "online": bool(parsed.get("online", False)),
        "parsed_by": "openai",
    }


def _rule_parse(prompt: str) -> dict:
    """OpenAI 없을 때 키워드 규칙 기반 파싱."""
    text = prompt.lower()

    # 온라인 여부
    online = any(kw in text for kw in ["온라인", "비대면", "재택", "원격"])

    # 지역 추출
    location = ""
    regions = [
        "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
        "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
        "강남", "판교", "여의도", "홍대", "마포", "종로", "강서", "송파",
        "성남", "수원", "안양", "안산", "화성", "용인", "고양", "의정부",
    ]
    for region in regions:
        if region in prompt:
            location = region
            break

    # 스킬 추출 (자주 쓰는 기술/직무 키워드)
    skill_patterns = [
        r"python|파이썬", r"java|자바", r"javascript|자바스크립트",
        r"react|리액트", r"백엔드|backend", r"프론트엔드|frontend",
        r"ai|인공지능|머신러닝|딥러닝", r"데이터\s*분석|data",
        r"전기기사|전기기능사|전기공사", r"용접", r"cnc|선반|밀링",
        r"회계|세무|erp", r"인사|hr|노무",
        r"간호|요양|보건", r"사회복지", r"보육",
        r"요리|조리|바리스타|제과|제빵",
        r"건축|토목|인테리어|실내건축",
        r"정보처리|정보보안|네트워크",
        r"마케팅|sns|광고|콘텐츠",
        r"물류|유통", r"금융|보험|증권",
    ]
    skills = []
    for pattern in skill_patterns:
        if re.search(pattern, text):
            # 패턴에서 대표 키워드 추출
            key = pattern.split("|")[0].replace("\\s*", " ").replace("\\", "")
            skills.append(key)
        if len(skills) >= 5:
            break

    return {
        "prompt": prompt,
        "skills": skills,
        "location": location,
        "online": online,
        "parsed_by": "rule",
    }
