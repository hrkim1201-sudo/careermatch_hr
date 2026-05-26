"""Match router - NCS-based career path recommendation."""
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
from app.services.nlp_parser import parse_prompt

router = APIRouter()


@router.post("/parse", response_model=ParsedInput)
def parse_input(req: ParseRequest) -> ParsedInput:
    """Parse natural language input into structured search conditions."""
    result = parse_prompt(req.prompt)
    return ParsedInput(
        location=result.get("region"),
        skills=result.get("job_keywords", []),
        online=result.get("online", False),
    )


@router.post("/direct", response_model=MatchResponse)
def direct_match(req: DirectMatchRequest, db: Session = Depends(get_db)) -> MatchResponse:
    """Natural language input to recommendation in one step."""
    parsed = parse_prompt(req.prompt or "")

    match_req = MatchRequest(
        prompt=req.prompt,
        skills=parsed.get("job_keywords", []),
        preferences={
            "location": parsed.get("region"),
            "online": parsed.get("online", False),
        },
        top_k=req.top_k,
    )

    items, used_method, total = matcher.run_match(db, match_req)
    portal_keywords = (parsed.get("job_keywords") or [])[:3]

    return MatchResponse(
        results=items,
        used_method=used_method,
        total_candidates=total,
        parsed_keywords=portal_keywords,
        parsed_region=parsed.get("region"),
    )


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
