"""자연어 → 구조화된 검색 조건 파싱.

gpt-4o-mini 없으면 규칙 기반 fallback 사용.
"""
from __future__ import annotations
import logging
import re
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# 지역 키워드
_REGIONS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
    "수원", "성남", "안양", "안산", "고양", "용인", "창원", "청주", "천안",
    "판교", "분당", "강남", "강서", "마포", "종로", "홍대", "신촌",
]

# 직무 키워드 사전 (동의어 확장)
_JOB_SYNONYMS = {
    "백엔드": ["백엔드", "back-end", "backend", "서버", "API", "Spring", "Django", "FastAPI"],
    "프론트엔드": ["프론트엔드", "front-end", "frontend", "React", "Vue", "UI", "웹"],
    "풀스택": ["풀스택", "fullstack", "full-stack"],
    "데이터": ["데이터", "data", "분석", "analytics", "SQL", "파이썬"],
    "AI": ["AI", "인공지능", "머신러닝", "딥러닝", "ML", "LLM"],
    "DevOps": ["DevOps", "클라우드", "AWS", "Docker", "Kubernetes", "인프라"],
    "보안": ["보안", "security", "정보보안", "해킹"],
    "전기": ["전기", "전기기사", "전기기능사", "배전", "전력"],
    "기계": ["기계", "CNC", "용접", "자동화", "로봇", "냉동"],
    "건설": ["건설", "건축", "토목", "인테리어", "조경"],
    "회계": ["회계", "세무", "경리", "재무", "ERP"],
    "마케팅": ["마케팅", "광고", "SNS", "브랜드"],
    "요리": ["요리", "조리", "제과", "제빵", "바리스타", "카페"],
    "복지": ["사회복지", "요양", "보육", "상담", "복지사"],
}


def parse_prompt(prompt: str) -> dict:
    """자연어 입력을 파싱해 검색 조건 반환."""
    settings = get_settings()

    # OpenAI 있으면 AI 파싱
    if settings.openai_api_key:
        try:
            return _parse_with_ai(prompt, settings)
        except Exception as e:
            logger.warning("AI parse failed: %s, fallback to rule-based", e)

    return _parse_with_rules(prompt)


def _parse_with_ai(prompt: str, settings) -> dict:
    """gpt-4o-mini로 파싱."""
    from openai import OpenAI
    import json

    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "사용자의 취업/학습 관련 자연어 문장을 분석해 JSON으로 반환하세요.\n"
                    "fields: region(지역명 또는 null), job_keywords(핵심 직무/스킬 키워드 배열, 최대 5개), "
                    "online(온라인 선호 boolean), experience_level(신입/경력/무관), "
                    "expanded_keywords(동의어·관련어 포함 확장 키워드 배열, 최대 10개)\n"
                    "JSON만 반환, 설명 없이."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_tokens=300,
    )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


def _parse_with_rules(prompt: str) -> dict:
    """규칙 기반 파싱 (fallback)."""
    text = prompt.lower()

    # 지역 추출
    region = None
    for r in _REGIONS:
        if r in prompt:
            region = r
            break

    # 온라인 여부
    online = any(w in text for w in ["온라인", "비대면", "원격", "재택"])

    # 핵심 키워드 추출
    job_keywords = []
    expanded_keywords = []
    for category, synonyms in _JOB_SYNONYMS.items():
        for syn in synonyms:
            if syn.lower() in text:
                job_keywords.append(category)
                expanded_keywords.extend(synonyms[:5])
                break

    # 경력 레벨
    if any(w in text for w in ["신입", "처음", "입문", "시작"]):
        exp = "신입"
    elif any(w in text for w in ["경력", "이직", "전환"]):
        exp = "경력"
    else:
        exp = "무관"

    # 키워드 없으면 명사 추출
    if not job_keywords:
        words = re.findall(r'[가-힣a-zA-Z]{2,}', prompt)
        stop = {"하고", "싶어", "싶다", "원해", "필요", "배우", "취업", "공백", "면접",
                "준비", "이에요", "입니다", "해요", "있어", "없어", "많이", "조금"}
        job_keywords = [w for w in words if w not in stop][:5]
        expanded_keywords = job_keywords.copy()

    return {
        "region": region,
        "job_keywords": list(dict.fromkeys(job_keywords)),
        "expanded_keywords": list(dict.fromkeys(expanded_keywords)),
        "online": online,
        "experience_level": exp,
    }


def build_query_text(prompt: str, parsed: dict) -> str:
    """파싱 결과를 임베딩용 쿼리 텍스트로 변환."""
    parts = [prompt]  # 원문 포함

    if parsed.get("job_keywords"):
        parts.append(" ".join(parsed["job_keywords"]))

    if parsed.get("expanded_keywords"):
        parts.append(" ".join(parsed["expanded_keywords"]))

    if parsed.get("region"):
        parts.append(parsed["region"])

    return " ".join(parts)
