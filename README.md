# Geospatial File Measurement API

This project implements a production-minded FastAPI backend for uploading and measuring geospatial features from KML files and Shapefile ZIP archives. It demonstrates secure upload handling, geospatial parsing, CRS-aware measurement logic, SQLite persistence, and clean service-oriented design.

## Features

- Supports `.kml` and `.zip` containing shapefiles
- Validates upload size and structure
- Extracts and validates shapefile archives (`.shp`, `.shx`, `.dbf`)
- Reads vector data with GeoPandas and Shapely
- Detects CRS metadata graciously
- Reprojects to a local projected CRS before distance/area calculations
- Measures polygons as area in square metres and lines as length in metres
- Returns unsupported geometry results without crashing
- Stores metadata in SQLite using SQLAlchemy
- Provides Swagger docs at `/docs`

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
app/
  api/
    files.py
  models/
    file.py
  schemas/
    file.py
  services/
    crs_service.py
    file_processor.py
    geometry_service.py
  config.py
  database.py
  main.py
uploads/
temp/
tests/
requirements.txt
Dockerfile
docker-compose.yml
README.md
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

Open Swagger UI at `http://127.0.0.1:8000/docs` to browse available API endpoints and example payloads.

## Endpoints

### POST /api/files/

Upload a KML or Shapefile ZIP and receive a summary response.

Example request:

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

Fetch metadata for a previously uploaded file.

### GET /api/files/{id}/measurements/

Return per-feature measurement payloads.

## File Processing Flow

Upload → Validation → File Processing → Feature Extraction → CRS Handling → Measurement → Database → Response

## CRS Strategy

Geographic CRS coordinates such as EPSG:4326 use degrees, which cannot be used directly to compute area or distance in metres. The API first detects the input CRS. When the source CRS is geographic, it computes a centroid and chooses a UTM-based projected CRS for the local footprint before calculating all measurements. This keeps the measurement values consistent and returns distances and areas in metres or square metres.

## Design Decisions

- The file processor handles validation and archive extraction.
- CRS logic lives in a dedicated service so it can be tested independently.
- Geometry measurement is isolated from the API layer for maintainability.
- SQLite is chosen for local development while preserving a SQLAlchemy abstraction that lends itself to future PostgreSQL adoption.

## Error Handling

The API returns 400 for invalid uploads, corrupted files, missing shapefile components, or malformed geospatial data. Missing file IDs use 404. Unsupported geometries return a successful payload with `measurement: null` and a message rather than crashing. Internal errors are logged without exposing stack traces to clients.

## Testing

```bash
pytest
```

## Future Scope

- PostgreSQL/PostGIS support
- Background processing for large files
- Storage in object storage providers
- Authentication and authorization
- Additional geometry types
- Async processing for high throughput
- Cloud deployment and container orchestration

## Learning

This project adds practical experience with FastAPI backend design, geospatial file ingestion, CRS concepts, geometry measurement, validation, tests, and production-oriented Python architecture.

