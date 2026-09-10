from pathlib import Path

from fastapi.testclient import TestClient
from redforge.main import app

client = TestClient(app)


def test_deep_impact_api(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    response = client.post(
        "/api/v1/autonomy/impact/deep",
        json={"repository_path": str(tmp_path), "changed_files": ["a.py"]},
    )
    assert response.status_code == 200
    assert response.json()["changed_files"] == ["a.py"]
