from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
TEMP_DIR = BASE_DIR / "temp"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./geospatial.db")
MAX_UPLOAD_SIZE = 50 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".kml", ".zip"}
REQUIRED_ZIP_COMPONENTS = {".shp", ".shx", ".dbf"}
