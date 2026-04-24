"""추천 엔드포인트."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.repositories import program_repo
from app.schemas import (
    DirectMatchRequest,
    GuideResponse,
    MatchRequest,
    MatchResponse,
    ParsedInput,
    ParseRequest,
)
from app.services import guide_generator, matcher
from app.services.nlp_parser import parse_user_input

router = APIRouter()


@router.post("/parse", response_model=ParsedInput)
def parse_input(req: ParseRequest) -> ParsedInput:
    """자연어 입력을 파싱해서 지역·스킬·온라인 여부를 추출합니다."""
    result = parse_user_input(req.prompt)
    return ParsedInput(**result)


@router.post("/direct", response_model=MatchResponse)
def direct_match(req: DirectMatchRequest, db: Session = Depends(get_db)) -> MatchResponse:
    """자연어 입력 → 파싱 → 추천을 한 번에 처리합니다."""
    parsed = parse_user_input(req.prompt)
    match_req = MatchRequest(
        prompt=req.prompt,
        skills=parsed["skills"],
        preferences={
            "location": parsed["location"],
            "online": parsed["online"],
        },
        top_k=req.top_k,
    )
    items, used_method, total = matcher.run_match(db, match_req)
    return MatchResponse(results=items, used_method=used_method, total_candidates=total)


@router.post("", response_model=MatchResponse)
def match(req: MatchRequest, db: Session = Depends(get_db)) -> MatchResponse:
    items, used_method, total = matcher.run_match(db, req)
    return MatchResponse(results=items, used_method=used_method, total_candidates=total)


@router.post("/{program_id}/guide", response_model=GuideResponse)
def guide(program_id: int, req: MatchRequest, db: Session = Depends(get_db)) -> GuideResponse:
    program = program_repo.get_by_id(db, program_id)
    if program is None:
        raise NotFoundError(f"program {program_id} not found")
    text, questions, used_method = guide_generator.generate_guide(program, req.prompt)
    return GuideResponse(guide=text, questions=questions, used_method=used_method)
