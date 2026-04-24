"""Recommendation endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.repositories import program_repo
from app.schemas import GuideResponse, MatchRequest, MatchResponse
from app.services import guide_generator, matcher

router = APIRouter()


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
