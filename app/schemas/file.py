from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: str | None = None
    status: Literal["PROCESSING", "COMPLETED", "FAILED"]
    created_at: datetime | None = None


class FileInfoResponse(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: str | None = None
    status: Literal["PROCESSING", "COMPLETED", "FAILED"]
    created_at: datetime | None = None


class FeatureMeasurement(BaseModel):
    feature_id: int
    geometry_type: str
    measurement: float | None = None
    unit: str | None = None
    area: float | None = None
    length: float | None = None
    message: str | None = None


class FileMeasurementsResponse(BaseModel):
    file_id: str
    features: list[FeatureMeasurement]


class ErrorResponse(BaseModel):
    detail: str


class FeatureRecord(BaseModel):
    feature_id: int
    geometry_type: str
    geometry: Any
    properties: dict[str, Any] | None = None
    crs: str | None = None
