"""Match router behavior tests."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_match_returns_sorted_results(seeded_client: TestClient) -> None:
    res = seeded_client.post(
        "/api/match",
        json={
            "prompt": "Python 백엔드 개발자가 되고 싶고 FastAPI를 배우고 싶어요",
            "skills": ["Python", "SQL"],
            "preferences": {"online": True},
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["used_method"] in {"openai", "tfidf"}
    assert body["total_candidates"] >= 6
    assert isinstance(body["results"], list)

    if body["results"]:
        scores = [r["score"] for r in body["results"]]
        assert scores == sorted(scores, reverse=True), "results must be score-desc sorted"


def test_match_uses_tfidf_without_openai_key(seeded_client: TestClient) -> None:
    res = seeded_client.post("/api/match", json={"prompt": "AI 백엔드"})
    assert res.status_code == 200
    body = res.json()
    # Without OPENAI_API_KEY in test env, fallback must be tfidf
    assert body["used_method"] == "tfidf"


def test_match_with_empty_prompt_does_not_crash(seeded_client: TestClient) -> None:
    res = seeded_client.post("/api/match", json={"prompt": "", "skills": []})
    assert res.status_code == 200


def test_guide_endpoint_returns_template_without_openai(seeded_client: TestClient) -> None:
    listing = seeded_client.get("/api/programs").json()
    program_id = listing["programs"][0]["id"]
    res = seeded_client.post(
        f"/api/match/{program_id}/guide",
        json={"prompt": "백엔드 개발자가 되고 싶어요"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["used_method"] == "template"
    assert len(body["guide"]) > 30
    assert len(body["questions"]) == 3


def test_guide_404_for_unknown_program(seeded_client: TestClient) -> None:
    res = seeded_client.post("/api/match/99999/guide", json={"prompt": "test"})
    assert res.status_code == 404
    assert res.json()["code"] == "not_found"
