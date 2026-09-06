from pathlib import Path

from fastapi.testclient import TestClient
from redforge.main import app

client = TestClient(app)


def test_repository_scan_api(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )

    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "example"
dependencies = [
    "fastapi>=0.116.0",
]
""",
        encoding="utf-8",
    )

    response = client.post(
        "/api/v1/repository/scan",
        json={
            "path": str(tmp_path),
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["name"] == tmp_path.name
    assert payload["total_files"] == 2
    assert payload["frameworks"] == ["FastAPI"]
    assert payload["project_types"] == ["Python"]
    assert payload["manifests"] == ["pyproject.toml"]


def test_repository_scan_api_returns_404_for_missing_path(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing"

    response = client.post(
        "/api/v1/repository/scan",
        json={
            "path": str(missing_path),
        },
    )

    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]
