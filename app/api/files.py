from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from shapely import wkt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.file import ProcessedFeature, ProcessingStatus, UploadedFile
from app.schemas.file import FeatureMeasurement, FileInfoResponse, FileMeasurementsResponse, FileUploadResponse
from app.services.crs_service import project_for_measurement
from app.services.file_processor import (
    CorruptedFileError,
    FileProcessingError,
    MissingShapefileError,
    UnsupportedFileTypeError,
    prepare_geodataframe,
    store_uploaded_file,
    validate_upload,
)
from app.services.geometry_service import measure_feature

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["files"])


@router.post(
    "/",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process a geospatial file",
    description="Accept a KML or Shapefile ZIP, persist metadata, and calculate supported measurements.",
)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)) -> FileUploadResponse:
    try:
        ext = validate_upload(file)
        stored_path = store_uploaded_file(file)

        db_file = UploadedFile(
            original_filename=file.filename or "unknown",
            stored_file_path=str(stored_path),
            processing_status=ProcessingStatus.PROCESSING.value,
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        try:
            gdf = prepare_geodataframe(stored_path, ext)
            if gdf.crs is None:
                raise ValueError("The file does not declare a valid CRS.")

            projected_gdf = project_for_measurement(gdf)
            db_file.original_filename = file.filename or "unknown"
            db_file.source_crs = str(gdf.crs)
            db_file.feature_count = int(len(gdf))
            db_file.processing_status = ProcessingStatus.COMPLETED.value
            db_file.error_message = None

            for feature_id, row in projected_gdf.iterrows():
                geometry = row.geometry
                if geometry is None:
                    continue
                feature = ProcessedFeature(
                    file_id=db_file.id,
                    feature_id=int(feature_id),
                    geometry_type=geometry.geom_type,
                    geometry_wkt=geometry.wkt,
                    properties=row.to_dict() if hasattr(row, "to_dict") else None,
                    crs=str(projected_gdf.crs),
                )
                db.add(feature)

            db.commit()
            db.refresh(db_file)
            return FileUploadResponse(
                id=db_file.id,
                filename=db_file.original_filename,
                feature_count=db_file.feature_count,
                crs=db_file.source_crs,
                status=db_file.processing_status,
                created_at=db_file.created_at,
            )
        except (ValueError, TypeError, FileProcessingError) as exc:
            db_file.processing_status = ProcessingStatus.FAILED.value
            db_file.error_message = str(exc)
            db.commit()
            logger.exception("Processing failed for file %s", db_file.id)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    except (UnsupportedFileTypeError, CorruptedFileError, MissingShapefileError, FileProcessingError, ValueError) as exc:
        logger.exception("Upload validation failed")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/{file_id}/",
    response_model=FileInfoResponse,
    summary="Fetch file metadata",
    description="Return stored metadata for a previously uploaded file.",
)
def get_file_info(file_id: str, db: Session = Depends(get_db)) -> FileInfoResponse:
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileInfoResponse(
        id=db_file.id,
        filename=db_file.original_filename,
        feature_count=db_file.feature_count,
        crs=db_file.source_crs,
        status=db_file.processing_status,
        created_at=db_file.created_at,
    )


@router.get(
    "/{file_id}/measurements/",
    response_model=FileMeasurementsResponse,
    summary="Get measurements for all features",
    description="Return supported measurements for every feature associated with the uploaded file.",
)
def get_measurements(file_id: str, db: Session = Depends(get_db)) -> FileMeasurementsResponse:
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    records = db.query(ProcessedFeature).filter(ProcessedFeature.file_id == file_id).all()
    features: list[FeatureMeasurement] = []

    for record in records:
        geometry: Any = None
        try:
            if record.geometry_wkt:
                geometry = wkt.loads(record.geometry_wkt)
        except Exception:
            geometry = None

        if geometry is None:
            features.append(
                FeatureMeasurement(
                    feature_id=record.feature_id,
                    geometry_type=record.geometry_type,
                    measurement=None,
                    unit=None,
                    area=None,
                    length=None,
                    message="Measurement not supported for this geometry type",
                )
            )
            continue

        measurement_dict = measure_feature(record.feature_id, geometry, record.geometry_type)
        features.append(FeatureMeasurement(**measurement_dict))

    return FileMeasurementsResponse(file_id=file_id, features=features)
