import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_endpoints_monkeypatched(monkeypatch):
    async def fake_get_all(refresh: bool = False):
        return [
            {"id": "asv-bergedorf-lohbruegge-von-1885-e-v", "name": "ASV Bergedorf-Lohbrügge von 1885 e.V.", "url": "https://www.hfv.de/vereine/asv-bergedorf-lohbruegge-von-1885-e-v/"},
            {"id": "test-fc", "name": "Test FC", "url": "https://www.hfv.de/vereine/test-fc/"},
        ]

    async def fake_get_by_identifier(identifier: str, refresh: bool = False):
        if identifier in ("test-fc", "Test FC"):
            return {
                "id": "test-fc",
                "name": "Test FC",
                "url": "https://www.hfv.de/vereine/test-fc/",
                "address": {"full": "Musterstr. 1 12345 Hamburg", "street": "Musterstr. 1", "postcode": "12345", "city": "Hamburg"}
            }
        return None

    async def fake_load_cache():
        return

    import app.cache as cache
    monkeypatch.setattr(cache, "get_all", fake_get_all)
    monkeypatch.setattr(cache, "get_by_identifier", fake_get_by_identifier)
    monkeypatch.setattr(cache, "load_cache", fake_load_cache)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/vereine")
        assert r.status_code == 200
        lst = r.json()
        assert isinstance(lst, list)
        assert {"id", "name", "url"} <= set(lst[0].keys())

        r2 = await ac.get("/verein/test-fc")
        assert r2.status_code == 200
        payload = r2.json()
        assert payload["id"] == "test-fc"
        assert "address" in payload and "full" in payload["address"]
        r3 = await ac.get("/verein/nichtvorhanden")
        assert r3.status_code == 404