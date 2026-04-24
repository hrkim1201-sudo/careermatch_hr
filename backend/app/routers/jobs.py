"""Jobs endpoint placeholder.

Reserved for future Work24 채용공고 (job posting) integration.
Kept as a stub so the router registration in main.py never breaks
when expansion happens.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_jobs() -> dict:
    return {"items": [], "message": "jobs endpoint reserved for future expansion"}
