from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from . import cache
from .models import Verein, VereinListItem

from fastapi.responses import RedirectResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.environ.setdefault("CACHE_FILE", "/tmp/vereine_cache.json")
    try:
        await cache.load_cache()
    except Exception:
        pass

    if cache.is_stale():
        asyncio.create_task(cache.refresh_cache(force=True))

    yield

    try:
        await cache.close()
    except Exception:
        pass


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

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")

@app.get("/vereine", response_model=list[VereinListItem])
async def get_vereine():
    try:
        data = await cache.get_all()
    except Exception:
        raise HTTPException(status_code=503, detail="Cache wird aufgebaut, bitte kurz später erneut versuchen.")
    if not data:
        raise HTTPException(status_code=503, detail="Cache wird aufgebaut, bitte kurz später erneut versuchen.")
    return [{"id": v["id"], "name": v["name"], "url": v["url"]} for v in data]


@app.get("/verein/{identifier}", response_model=Verein)
async def get_verein(identifier: str):
    data = await cache.get_by_identifier(identifier)
    if not data:
        raise HTTPException(status_code=404, detail="Verein nicht gefunden")
    return data


handler = Mangum(app)
