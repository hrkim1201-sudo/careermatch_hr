"""Per-program study/preparation guide generator.

OpenAI path: chat completion that produces a short Korean guide and
3 self-check questions, returned as structured JSON.

Fallback path: template-driven text using the program's metadata.
This keeps the demo usable without an API key.
"""
from __future__ import annotations

import json
import logging

from app.core.config import get_settings
from app.models import TrainingProgram

logger = logging.getLogger(__name__)


def generate_guide(program: TrainingProgram, user_prompt: str | None = None) -> tuple[str, list[str], str]:
    """Returns (guide_text, questions, used_method)."""
    settings = get_settings()
    if settings.openai_api_key:
        try:
            return *_openai_guide(program, user_prompt or ""), "openai"
        except Exception as e:
            logger.warning("openai guide failed, falling back to template: %s", e)
    return *_template_guide(program), "template"


# --------------------------------------------------------------------------- #
# OpenAI path
# --------------------------------------------------------------------------- #
_PROMPT = """당신은 한국어로 답하는 진로 코치입니다.
사용자가 입력한 희망 사항과 추천된 프로그램 정보를 바탕으로,
이 프로그램을 어떻게 활용해야 하는지 한국어로 7~10문장 분량의 가이드를 작성하세요.
또한 학습자가 시작 전에 점검해볼 자가질문 3개를 만드세요.

응답은 반드시 아래 JSON 형식만 출력하세요. 다른 텍스트나 마크다운 펜스를 출력하지 마세요.
{{
  "guide": "...",
  "questions": ["...", "...", "..."]
}}

[프로그램 정보]
제목: {title}
운영기관: {provider}
요약: {summary}
대상: {target}
스킬: {skills}
일정/비용: {schedule} / {tuition}

[사용자 희망 사항]
{user_prompt}
"""


def _openai_guide(program: TrainingProgram, user_prompt: str) -> tuple[str, list[str]]:
    settings = get_settings()
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_request_timeout)
    rendered = _PROMPT.format(
        title=program.title,
        provider=program.provider or "정보 없음",
        summary=program.summary or "정보 없음",
        target=program.target_audience or "정보 없음",
        skills=program.skills or "정보 없음",
        schedule=program.schedule or "정보 없음",
        tuition=program.tuition or "정보 없음",
        user_prompt=user_prompt or "(입력 없음)",
    )
    res = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[{"role": "user", "content": rendered}],
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    text = res.choices[0].message.content or "{}"
    parsed = json.loads(text)
    guide = (parsed.get("guide") or "").strip()
    questions = [str(q).strip() for q in (parsed.get("questions") or []) if str(q).strip()]
    if not guide:
        raise ValueError("openai returned empty guide")
    return guide, questions[:3]


# --------------------------------------------------------------------------- #
# Template fallback
# --------------------------------------------------------------------------- #
def _template_guide(program: TrainingProgram) -> tuple[str, list[str]]:
    skills_line = (
        f"이 과정에서 다루는 핵심 스킬은 {program.skills}입니다."
        if program.skills
        else "구체적인 스킬 목록은 프로그램 페이지에서 확인하세요."
    )
    schedule_line = (
        f"운영 일정은 {program.schedule}이며, 비용은 {program.tuition or '정보 없음'}입니다."
        if program.schedule
        else "운영 일정은 프로그램 페이지에서 확인하세요."
    )
    target_line = (
        f"대상은 {program.target_audience}입니다." if program.target_audience else ""
    )

    guide = (
        f"{program.title}은(는) {program.provider or '운영기관'}이 진행하는 프로그램입니다. "
        f"{program.summary or ''} "
        f"{target_line} {skills_line} {schedule_line} "
        "수강 전 본인의 현재 역량과 부족한 부분을 정리하고, "
        "프로그램 종료 후 어떤 산출물을 남길지 미리 그려두면 학습 효과가 높아집니다. "
        "또한 같은 카테고리의 다른 프로그램과 일정을 비교한 뒤 최종 결정하시기 바랍니다."
    ).strip()

    questions = [
        "지금 내가 부족하다고 느끼는 핵심 역량을 한 줄로 적을 수 있는가?",
        "이 프로그램을 마치고 만들 산출물(포트폴리오/자격증/실무 경험)이 명확한가?",
        "지원 일정과 사전 학습 시간을 내 일정에 실제로 확보할 수 있는가?",
    ]
    return guide, questions
