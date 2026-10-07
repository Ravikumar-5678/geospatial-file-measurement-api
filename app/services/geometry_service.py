from __future__ import annotations

from typing import Any


def measure_feature(feature_id: int, geometry: Any, geometry_type: str | None = None) -> dict[str, Any]:
    """Return measurement payload for a single geometry after projection to metres."""
    geom_type = geometry_type or getattr(geometry, "geom_type", "Unknown")

    if geom_type == "Point":
        return {
            "feature_id": feature_id,
            "geometry_type": geom_type,
            "measurement": None,
            "unit": None,
            "area": None,
            "length": None,
            "message": None,
        }

    if geom_type in {"Polygon", "MultiPolygon"}:
        value = float(geometry.area)
        return {
            "feature_id": feature_id,
            "geometry_type": geom_type,
            "measurement": value,
            "unit": "m²",
            "area": value,
            "length": None,
            "message": None,
        }

    if geom_type in {"LineString", "MultiLineString"}:
        value = float(geometry.length)
        return {
            "feature_id": feature_id,
            "geometry_type": geom_type,
            "measurement": value,
            "unit": "m",
            "area": None,
            "length": value,
            "message": None,
        }

    return {
        "feature_id": feature_id,
        "geometry_type": geom_type,
        "measurement": None,
        "unit": None,
        "area": None,
        "length": None,
        "message": "Measurement not supported for this geometry type",
    }
