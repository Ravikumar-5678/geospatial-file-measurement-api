from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.files import router as files_router
from app.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Geospatial File Measurement API",
    version="1.0.0",
    description=(
        "Upload KML and Shapefile ZIP files, extract feature details, and compute "
        "supported measurements using CRS-aware geospatial logic."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(files_router, prefix="/api")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Geospatial File Measurement API is running."}
