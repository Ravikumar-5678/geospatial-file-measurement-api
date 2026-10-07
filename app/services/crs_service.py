from __future__ import annotations

import math

import geopandas as gpd
from pyproj import CRS


def choose_projected_crs(gdf: gpd.GeoDataFrame) -> str:
    """Choose a local projected CRS in metres for area and length calculations."""
    if gdf.empty:
        raise ValueError("Geodataframe is empty.")
    if gdf.crs is None:
        raise ValueError("Missing CRS metadata in the source geospatial file.")

    source_crs = CRS.from_user_input(gdf.crs)
    if not source_crs.is_geographic:
        return source_crs.to_string()

    centroid = gdf.unary_union.centroid
    if centroid is None or not math.isfinite(centroid.x) or not math.isfinite(centroid.y):
        raise ValueError("Unable to estimate the geometry centroid for CRS selection.")

    lon = centroid.x
    lat = centroid.y
    utm_zone = int((lon + 180) / 6) + 1
    if lat >= 0:
        epsg_code = 32600 + utm_zone
    else:
        epsg_code = 32700 + utm_zone

    return f"EPSG:{epsg_code}"


def project_for_measurement(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject a geographic GeoDataFrame into a local projected CRS in metres."""
    if gdf.crs is None:
        raise ValueError("Missing CRS metadata in the source geospatial file.")

    target_crs = choose_projected_crs(gdf)
    return gdf.to_crs(target_crs)
