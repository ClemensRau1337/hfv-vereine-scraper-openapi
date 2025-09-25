from __future__ import annotations

import asyncio
import json
import os
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from pathlib import Path

from . import scraper
from .utils import slugify

CACHE_FILE = os.getenv("CACHE_FILE", "data/vereine_cache.json")
CACHE_PATH = Path(CACHE_FILE)

# Weich: nach so vielen Minuten wird im Hintergrund neu gebaut (aber weiterhin bedient).
CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "1440"))  # 24h

# Hart: wenn älter als das, wird einmalig synchron neu gebaut (um uralten Cache zu vermeiden).
CACHE_MAX_STALE_MINUTES = int(os.getenv("CACHE_MAX_STALE_MINUTES", str(7 * 24 * 60)))  # 7 Tage

_cache: dict[str, dict] = {}
_last_loaded: datetime | None = None

_refresh_lock = asyncio.Lock()
_refresh_task: asyncio.Task | None = None


def _now() -> datetime:
    return datetime.now(UTC)


def _parse_iso_dt(ts: str | None) -> datetime | None:
    if not ts:
        return None
    with suppress(Exception):
        return datetime.fromisoformat(ts)
    return None


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)  # atomar


def _age_minutes(dt: datetime | None) -> float | None:
    if dt is None:
        return None
    return (_now() - dt).total_seconds() / 60.0


def is_stale() -> bool:
    """Weiche Stale-Grenze: danach im Hintergrund refreshen."""
    if _last_loaded is None:
        return True
    return _now() - _last_loaded > timedelta(minutes=CACHE_TTL_MINUTES)


def is_hard_expired() -> bool:
    """Harte Expire-Grenze: danach einmalig synchron neu bauen."""
    if _last_loaded is None:
        return True
    return _now() - _last_loaded > timedelta(minutes=CACHE_MAX_STALE_MINUTES)


def _schedule_refresh() -> None:
    """Nur einen einzigen parallelen Refresh zulassen."""
    global _refresh_task
    if _refresh_task and not _refresh_task.done():
        return
    _refresh_task = asyncio.create_task(refresh_cache())


async def load_cache() -> None:
    """
    Lädt IMMER vorhandene Cache-Datei in den Speicher (auch wenn alt),
    und triggert ggf. einen Hintergrund-Refresh. Nur wenn gar nichts da ist,
    wird einmalig synchron gescraped.
    """
    global _cache, _last_loaded

    parent = CACHE_PATH.parent
    if parent and not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)

    if CACHE_PATH.exists():
        with suppress(Exception):
            payload = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            meta = payload.get("__meta__", {})
            data = payload.get("data", {})
            if isinstance(data, dict):
                _cache = data
                _last_loaded = _parse_iso_dt(meta.get("last_updated")) or _now()

    # Falls noch gar keine Daten da sind -> einmalig synchron aufbauen
    if not _cache:
        await refresh_cache(force=True)
        return

    # Haben Daten: ggf. im Hintergrund aktualisieren
    if is_stale():
        _schedule_refresh()


async def refresh_cache(force: bool = False) -> None:
    """Scraped neu. Bei Fehlern bleiben die alten Daten erhalten."""
    global _cache, _last_loaded

    async with _refresh_lock:
        if not force and not is_stale():
            return

        try:
            data = await scraper.scrape_all()
        except Exception:
            # Fehler: alten Cache behalten
            return

        _cache = data or {}
        _last_loaded = _now()

        payload = {
            "__meta__": {"last_updated": _last_loaded.isoformat()},
            "data": _cache,
        }

        parent = CACHE_PATH.parent
        if parent and not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)

        _atomic_write(
            CACHE_PATH,
            json.dumps(payload, ensure_ascii=False, indent=2),
        )


async def get_all() -> list[dict]:
    """
    Liefert immer sofort Daten. Bei 'stale' wird nur im Hintergrund aktualisiert.
    Wenn der Cache hart abgelaufen ist, wird einmalig synchron erneuert.
    """
    if is_hard_expired():
        await refresh_cache(force=True)
    elif is_stale():
        _schedule_refresh()
    return sorted(_cache.values(), key=lambda d: d.get("name", "").lower())


async def get_by_identifier(identifier: str) -> dict | None:
    if is_hard_expired():
        await refresh_cache(force=True)
    elif is_stale():
        _schedule_refresh()

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
