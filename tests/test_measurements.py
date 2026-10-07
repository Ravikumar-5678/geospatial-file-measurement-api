from __future__ import annotations

from shapely.geometry import LineString, Point, Polygon

from app.services.geometry_service import measure_feature


def test_polygon_area() -> None:
    polygon = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
    result = measure_feature(0, polygon, "Polygon")
    assert result["area"] == 1.0
    assert result["unit"] == "m²"


def test_line_length() -> None:
    line = LineString([(0, 0), (0, 3)])
    result = measure_feature(0, line, "LineString")
    assert result["length"] == 3.0
    assert result["unit"] == "m"


def test_point_is_handled_without_measurement() -> None:
    point = Point(1, 2)
    result = measure_feature(0, point, "Point")
    assert result["measurement"] is None
    assert result["unit"] is None


def test_unsupported_geometry_message() -> None:
    multigeom = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    result = measure_feature(0, multigeom, "MultiPolygon")
    assert result["message"] == "Measurement not supported for this geometry type"
