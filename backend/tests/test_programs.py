"""Programs router smoke tests."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_programs_empty(client: TestClient) -> None:
    res = client.get("/api/programs")
    assert res.status_code == 200
    body = res.json()
    assert body["programs"] == []
    assert body["source"] == "empty"


def test_list_programs_seeded(seeded_client: TestClient) -> None:
    res = seeded_client.get("/api/programs")
    assert res.status_code == 200
    body = res.json()
    assert len(body["programs"]) >= 6
    assert body["source"] == "sample"
    assert body["counts"]["total"] >= 6


def test_refresh_falls_back_to_sample_without_key(client: TestClient) -> None:
    # No WORK24_API_KEY in env → should populate sample data and report source="sample"
    res = client.post("/api/programs/refresh")
    assert res.status_code == 200
    body = res.json()
    assert body["fetched"] >= 1
    assert body["source"] == "sample"
