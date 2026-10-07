from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from uuid import uuid4

import geopandas as gpd
from fastapi import UploadFile

from app.config import MAX_UPLOAD_SIZE, REQUIRED_ZIP_COMPONENTS, SUPPORTED_EXTENSIONS, TEMP_DIR, UPLOAD_DIR


class FileProcessingError(ValueError):
    """Base exception for file validation and processing failures."""


class UnsupportedFileTypeError(FileProcessingError):
    pass


class CorruptedFileError(FileProcessingError):
    pass


class MissingShapefileError(FileProcessingError):
    pass


def safe_file_name(filename: str) -> str:
    base_name = os.path.basename(filename)
    stem, ext = os.path.splitext(base_name)
    clean_stem = "".join(ch for ch in stem if ch.isalnum() or ch in {"-", "_"})
    return f"{clean_stem or 'upload'}_{uuid4().hex}{ext.lower()}"


def validate_upload(file: UploadFile) -> str:
    """Validate extension and size before the file is persisted."""
    if file is None or file.filename is None:
        raise UnsupportedFileTypeError("No file was uploaded.")

    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{extension}'. Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}."
        )

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_UPLOAD_SIZE:
        raise UnsupportedFileTypeError("Uploaded file exceeds the 50 MB size limit.")

    return extension


def store_uploaded_file(file: UploadFile) -> Path:
    """Persist the uploaded file to a safe folder using a generated filename."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = safe_file_name(file.filename or "upload.bin")
    stored_path = UPLOAD_DIR / stored_name
    with stored_path.open("wb") as destination:
        shutil.copyfileobj(file.file, destination)
    return stored_path


def extract_zip_shapefile(zip_path: Path) -> Path:
    """Extract a ZIP archive containing a shapefile into a temp directory and return the .shp path."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    working_dir = TEMP_DIR / f"extract_{uuid4().hex}"
    working_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                target = PurePosixPath(member.filename)
                if target.is_absolute() or ".." in target.parts:
                    raise MissingShapefileError("ZIP archive contains unsafe paths.")
                destination = (working_dir / target).resolve()
                if not str(destination).startswith(str(working_dir.resolve())):
                    raise MissingShapefileError("ZIP archive contains an invalid extraction path.")
                if member.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, destination.open("wb") as output:
                    shutil.copyfileobj(source, output)

            extracted_files = [path for path in working_dir.rglob("*") if path.is_file()]
            found_exts = {path.suffix.lower() for path in extracted_files}
            missing = REQUIRED_ZIP_COMPONENTS - found_exts
            if missing:
                raise MissingShapefileError(
                    "ZIP archive is missing required Shapefile components: " + ", ".join(sorted(missing))
                )

            shapefile = next((path for path in extracted_files if path.suffix.lower() == ".shp"), None)
            if shapefile is None:
                raise MissingShapefileError("ZIP archive does not contain a valid .shp file.")
            return shapefile
    except zipfile.BadZipFile as exc:
        raise CorruptedFileError("The uploaded ZIP file is corrupted or unreadable.") from exc


def read_geodataframe(file_path: Path) -> gpd.GeoDataFrame:
    """Attempt to read a geospatial file and raise a user-friendly validation error if it is invalid."""
    try:
        gdf = gpd.read_file(file_path)
    except Exception as exc:  # pragma: no cover - broad catch for malformed input
        raise CorruptedFileError("The geospatial file is malformed or could not be decoded.") from exc

    if gdf.empty:
        raise CorruptedFileError("The geospatial file contains no features to process.")

    if gdf.crs is None:
        raise ValueError("The file does not declare a valid CRS.")

    return gdf


def prepare_geodataframe(file_path: Path, extension: str) -> gpd.GeoDataFrame:
    """Resolve the shapefile path inside a ZIP archive when needed and read the data."""
    if extension == ".zip":
        shapefile = extract_zip_shapefile(file_path)
        return read_geodataframe(shapefile)
    return read_geodataframe(file_path)


def cleanup_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
