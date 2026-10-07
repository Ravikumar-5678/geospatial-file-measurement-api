from __future__ import annotations

from shapely.geometry import LineString, Point, Polygon


def measure_feature(feature_id: int, geometry, geometry_type: str) -> dict:
    """Return a measurement payload for a single feature using projected coordinates."""
    geometry_type = geometry_type or geometry.geom_type
    if geometry_type == "Point":
        return {
            "feature_id": feature_id,
            "geometry_type": geometry_type,
            "measurement": None,
            "unit": None,
            "area": None,
            "length": None,
            "message": None,
        }

    if geometry_type in {"Polygon", "MultiPolygon"}:
        area_value = float(geometry.area)
        return {
            "feature_id": feature_id,
            "geometry_type": geometry_type,
            "measurement": area_value,
            "unit": "m²",
            "area": area_value,
            "length": None,
            "message": None,
        }

    if geometry_type in {"LineString", "MultiLineString"}:
        length_value = float(geometry.length)
        return {
            "feature_id": feature_id,
            "geometry_type": geometry_type,
            "measurement": length_value,
            "unit": "m",
            "area": None,
            "length": length_value,
            "message": None,
        }

    return {
        "feature_id": feature_id,
        "geometry_type": geometry_type,
        "measurement": None,
        "unit": None,
        "area": None,
        "length": None,
        "message": "Measurement not supported for this geometry type",
    }
