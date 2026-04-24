"""Portfolio submission and retrieval."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models import Portfolio
from app.schemas import PortfolioCreate, PortfolioRead

router = APIRouter()


@router.post("", response_model=PortfolioRead)
def create_portfolio(payload: PortfolioCreate, db: Session = Depends(get_db)) -> PortfolioRead:
    row = Portfolio(
        prompt=payload.prompt,
        skills=payload.skills,
        preferences=payload.preferences,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return PortfolioRead.model_validate(row)


@router.get("/{portfolio_id}", response_model=PortfolioRead)
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)) -> PortfolioRead:
    row = db.execute(select(Portfolio).where(Portfolio.id == portfolio_id)).scalar_one_or_none()
    if row is None:
        raise NotFoundError(f"portfolio {portfolio_id} not found")
    return PortfolioRead.model_validate(row)
