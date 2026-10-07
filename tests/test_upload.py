from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_kml_bytes() -> bytes:
    return b"""<?xml version='1.0' encoding='UTF-8'?>
<kml xmlns='http://www.opengis.net/kml/2.2'>
  <Placemark>
    <name>Square</name>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>0,0 0,1 1,1 1,0 0,0</coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
</kml>"""


def test_successful_kml_upload() -> None:
    response = client.post(
        "/api/files/",
        files={"file": ("sample.kml", create_kml_bytes(), "application/vnd.google-earth.kml+xml")},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["filename"] == "sample.kml"
    assert payload["status"] == "COMPLETED"
    assert payload["feature_count"] >= 1


def test_invalid_file_type() -> None:
    response = client.post(
        "/api/files/",
        files={"file": ("bad.txt", b"not geospatial data", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
