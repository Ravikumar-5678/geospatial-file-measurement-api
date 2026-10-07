from __future__ import annotations

import geopandas as gpd
from shapely.geometry import Point

from app.services.crs_service import choose_projected_crs, project_for_measurement


def test_crs_transformation() -> None:
    gdf = gpd.GeoDataFrame(geometry=[Point(0, 0)], crs="EPSG:4326")
    reprojected = project_for_measurement(gdf)
    assert reprojected.crs is not None
    assert reprojected.crs.to_epsg() is not None


def test_missing_crs_is_rejected() -> None:
    gdf = gpd.GeoDataFrame(geometry=[Point(0, 0)])
    try:
        choose_projected_crs(gdf)
        assert False, "Expected ValueError for missing CRS"
    except ValueError:
        pass
