import pytest
from fastapi.testclient import TestClient
from workbench.web.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_root_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "企业级AI短视频制作工作台" in response.text


def test_get_finops_balance_endpoint(client):
    response = client.get("/api/finops/balance")
    assert response.status_code == 200
    data = response.json()
    assert "current_balance" in data
    assert "is_safe" in data
    assert data["is_safe"] is True


def test_get_current_project(client):
    response = client.get("/api/project")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert len(data["shots"]) >= 1


def test_get_ledger_endpoint(client):
    response = client.get("/api/finops/ledger")
    assert response.status_code == 200
    data = response.json()
    assert "ledger" in data
    assert "total_cost" in data


def test_get_presets_and_load(client):
    response = client.get("/api/presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 3

    load_res = client.post("/api/project/preset/libai")
    assert load_res.status_code == 200
    assert "李白" in load_res.json()["title"]


def test_pipelines_endpoint(client):
    response = client.get("/api/pipelines")
    assert response.status_code == 200
    pipelines = response.json()
    assert len(pipelines) >= 10


def test_media_preview_svg_endpoint(client):
    response = client.get("/api/media/preview/1/START/A?v=1&id=abcdef")
    assert response.status_code == 200
    assert "image/svg+xml" in response.headers["content-type"]
    assert "<svg" in response.text
