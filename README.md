# Geospatial File Measurement API

This project is a FastAPI backend for processing and measuring geospatial vector files uploaded by clients. It accepts KML files and ZIP archives containing Shapefiles, stores metadata in SQLite, and calculates supported geometry measurements in metric units.

## Project Overview

The API was built to demonstrate production-oriented backend engineering for geospatial data processing. The use case is a technical assignment for an internship-level software development engineer role, with emphasis on file validation, clean architecture, CRS handling, geometry measurement, REST APIs, and testing discipline.

## Features

- Accepts `.kml` uploads and `.zip` files that contain a Shapefile
- Validates extension, size, and archive structure
- Safely stores uploaded files in the local uploads directory
- Extracts ZIP archives without path traversal risks
- Reads GeoJSON/KML/Shapefile data using GeoPandas
- Detects source CRS and reprojects to a local projected CRS for accurate measurement
- Measures polygons as area in square metres
- Measures lines as length in metres
- Returns point features without a metric measurement
- Returns explicit unsupported-geometry results instead of crashing
- Persists uploaded file metadata to SQLite with SQLAlchemy
- Exposes Swagger docs through FastAPI

## Tech Stack

- Python 3.11+
- FastAPI
- Uvicorn
- GeoPandas
- Shapely
- PyProj
- Fiona / Pyogrio
- SQLAlchemy
- SQLite
- Pydantic
- Pytest
- python-multipart

## Project Structure

```text
geospatial-file-measurement-api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── files.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── file.py
│   ├── schemas/
│   │   └── file.py
│   └── services/
│       ├── __init__.py
│       ├── crs_service.py
│       ├── file_processor.py
│       └── geometry_service.py
├── tests/
│   ├── test_upload.py
│   ├── test_file_info.py
│   ├── test_measurements.py
│   ├── test_crs.py
│   └── test_validation.py
├── uploads/
├── temp/
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── geospatial.db
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

## API Documentation

The application automatically provides Swagger docs at:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### POST /api/files/

Uploads a KML file or zip archive containing a shapefile.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/files/" -F "file=@survey.kml"
```

Example response:

```json
{
  "id": "abc123",
  "filename": "survey.kml",
  "feature_count": 120,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

### GET /api/files/{id}/

Returns file metadata.

### GET /api/files/{id}/measurements/

Returns per-feature measurement data.

Example response:

```json
{
  "file_id": "abc123",
  "features": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "area": 25430.52,
      "unit": "m²"
    },
    {
      "feature_id": 1,
      "geometry_type": "LineString",
      "length": 1245.73,
      "unit": "m"
    },
    {
      "feature_id": 2,
      "geometry_type": "Point",
      "measurement": null,
      "unit": null
    }
  ]
}
```

## File Processing Flow

Upload → Validation → File Processing → Feature Extraction → CRS Handling → Measurement → Database → Response

## CRS Strategy

A projected spatial reference system is required for metric area and distance calculations. Geographic CRS values such as EPSG:4326 use angular units (degrees), so area and distance must never be computed directly from those coordinates. The application therefore:

1. Reads the source CRS from the uploaded file.
2. Detects whether the CRS is geographic.
3. Uses a centroid-based UTM selection strategy to choose a local projected CRS in metres.
4. Reprojects geometry to that CRS before calculating polygon area or line length.

This ensures area and length values are returned in square metres and metres, respectively.

## Design Decisions

- File validation and ZIP extraction remain in a dedicated file-processing service instead of route handlers.
- CRS logic is separated from API logic to keep transformation rules easy to test and explain.
- Database models use SQLAlchemy so the app can later migrate to PostgreSQL without major architecture changes.
- Validation and error handling are explicit so invalid uploads fail gracefully.

## Error Handling

The API handles invalid input with clear HTTP status codes:

- 400 for invalid files, malformed data, missing shapefile components, unsupported types, and processing failures
- 404 for unknown file IDs
- 422 is left to FastAPI validation where appropriate

Unsupported geometry types are returned as explicit feature entries with `measurement: null` and a message rather than crashing the process.

## Testing

```bash
pytest
```

## Future Scope

- PostgreSQL/PostGIS
- Background processing for large files
- Object storage for uploaded assets
- Authentication and authorization
- Additional geometry types
- Async file processing
- Cloud deployment

## Learning

This project builds practical understanding of FastAPI backend development, geospatial file processing, CRS concepts, geometry measurements, API design, testing, and production-oriented Python architecture.

## Docker

```bash
docker build -t geospatial-file-measurement-api .
docker run -p 8000:8000 geospatial-file-measurement-api
```

## Example curl Requests

```bash
curl -X POST "http://127.0.0.1:8000/api/files/" -F "file=@sample.kml"
curl "http://127.0.0.1:8000/api/files/{id}/"
curl "http://127.0.0.1:8000/api/files/{id}/measurements/"
```

## Final Architecture Summary

The backend follows a simple layered design:

- API routes call service modules
- Services handle file validation and CRS/geometry logic
- SQLAlchemy models store metadata and processed features
- SQLite is used for local development and persistence

This keeps the project understandable for a student developer while still respecting production-quality engineering principles.
