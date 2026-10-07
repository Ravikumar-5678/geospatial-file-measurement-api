from __future__ import annotations

import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text

from app.database import Base


class ProcessingStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    original_filename = Column(String, nullable=False)
    stored_file_path = Column(String, nullable=False)
    feature_count = Column(Integer, default=0)
    source_crs = Column(String, nullable=True)
    processing_status = Column(String, default=ProcessingStatus.PROCESSING.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    error_message = Column(Text, nullable=True)


class ProcessedFeature(Base):
    __tablename__ = "processed_features"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    file_id = Column(String, ForeignKey("uploaded_files.id"), nullable=False)
    feature_id = Column(Integer, nullable=False)
    geometry_type = Column(String, nullable=False)
    geometry_wkt = Column(Text, nullable=True)
    properties = Column(JSON, nullable=True)
    crs = Column(String, nullable=True)
