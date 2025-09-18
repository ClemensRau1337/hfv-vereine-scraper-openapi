from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from . import scraper
from .utils import slugify

CACHE_FILE = os.getenv("CACHE_FILE", "data/vereine_cache.json")
CACHE_PATH = Path(CACHE_FILE)

CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "1440"))

_cache: dict[str, dict] = {}
_last_loaded: datetime | None = None


def _now() -> datetime:
    return datetime.now(UTC)


def _is_file_fresh(ts: str | None) -> bool:
    if not ts:
        return False
    try:
        dt = datetime.fromisoformat(ts)
    except Exception:
        return False
    return (_now() - dt) < timedelta(minutes=CACHE_TTL_MINUTES)


async def load_cache() -> None:
    """Lädt Cache-Datei, wenn frisch – sonst initialer Refresh."""
    global _cache, _last_loaded

    parent = CACHE_PATH.parent
    if parent and not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)

    if CACHE_PATH.exists():
        try:
            payload = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            meta = payload.get("__meta__", {})
            data = payload.get("data", {})
            if isinstance(data, dict) and _is_file_fresh(meta.get("last_updated")):
                _cache = data
                _last_loaded = _now()
                return
        except Exception:
            pass

    await refresh_cache(force=True)


async def refresh_cache(force: bool = False) -> None:
    """Scraped neu, wenn veraltet oder 'force'."""
    global _cache, _last_loaded

    if not force and not is_stale():
        return

    data = await scraper.scrape_all()
    _cache = data
    _last_loaded = _now()

    payload = {
        "__meta__": {"last_updated": _last_loaded.isoformat()},
        "data": _cache,
    }

    parent = CACHE_PATH.parent
    if parent and not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)

    CACHE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def is_stale() -> bool:
    if _last_loaded is None:
        return True
    return (_now() - _last_loaded) > timedelta(minutes=CACHE_TTL_MINUTES)


async def get_all() -> list[dict]:
    if is_stale():
        await refresh_cache(force=True)
    return sorted(_cache.values(), key=lambda d: d.get("name", "").lower())


async def get_by_identifier(identifier: str) -> dict | None:
    if is_stale():
        await refresh_cache(force=True)

    if identifier in _cache:
        return _cache[identifier]

    name_slug = slugify(identifier)
    if name_slug in _cache:
        return _cache[name_slug]

    for v in _cache.values():
        if slugify(v.get("name", "")) == name_slug:
            return v
    return None


async def close() -> None:
    return
