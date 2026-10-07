from __future__ import annotations

import io
import zipfile

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_corrupted_zip_rejected() -> None:
    response = client.post(
        "/api/files/",
        files={"file": ("broken.zip", b"this is not a zip", "application/zip")},
    )
    assert response.status_code == 400
    assert "corrupted" in response.json()["detail"].lower()


def test_zip_without_shapefile_rejected() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("notes.txt", "hello")
    response = client.post(
        "/api/files/",
        files={"file": ("broken.zip", buffer.getvalue(), "application/zip")},
    )
    assert response.status_code == 400
    assert "missing" in response.json()["detail"].lower()
