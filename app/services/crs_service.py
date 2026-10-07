from __future__ import annotations

import math

import geopandas as gpd
from pyproj import CRS


def choose_projected_crs(gdf: gpd.GeoDataFrame) -> str:
    """Select a projected CRS in metres based on the geometry centroid."""
    if gdf.empty:
        raise ValueError("The geodataframe is empty.")

    if gdf.crs is None:
        raise ValueError("The source file is missing CRS metadata.")

    source_crs = CRS.from_user_input(gdf.crs)
    if not source_crs.is_geographic:
        return source_crs.to_string()

    centroid = gdf.unary_union.centroid
    if centroid is None or not math.isfinite(centroid.x) or not math.isfinite(centroid.y):
        raise ValueError("Unable to determine a valid centroid for CRS selection.")

    zone = int((centroid.x + 180) / 6) + 1
    epsg_code = 32600 + zone if centroid.y >= 0 else 32700 + zone
    return f"EPSG:{epsg_code}"


def project_for_measurement(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject geographic data into a projected CRS before computing distances and areas."""
    if gdf.crs is None:
        raise ValueError("The source file is missing CRS metadata.")

    target_crs = choose_projected_crs(gdf)
    return gdf.to_crs(target_crs)
