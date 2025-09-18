from __future__ import annotations

from contextlib import asynccontextmanager

from typing import List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import cache
from .models import Verein, VereinListItem

@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache.load_cache()
    yield
    await cache.close()

app = FastAPI(
    title="HFV Vereine Scraper Open API (Unoffiziell)",
    version="1.0.0",
    description="Scraped Vereinsdaten vom Hamburger Fußball-Verband (HFV) mit strukturierten Adressen.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/vereine", response_model=List[VereinListItem])
async def get_vereine():
    data = await cache.get_all()
    return [{"id": v["id"], "name": v["name"], "url": v["url"]} for v in data]

@app.get("/verein/{identifier}", response_model=Verein)
async def get_verein(identifier: str):
    data = await cache.get_by_identifier(identifier)
    if not data:
        raise HTTPException(status_code=404, detail="Verein nicht gefunden")
    return data