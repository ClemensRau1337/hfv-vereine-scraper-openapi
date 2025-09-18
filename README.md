# hfv-vereine-scraper-openapi

Open-Source FastAPI, der Vereine vom **Hamburger Fußball-Verband** (Quelle: https://www.hfv.de/vereine) scraped, cached und über 2 Endpunkte anbietet.

- `GET /vereine` → Liste **nur** mit `id`, `name`, `url`
- `GET /verein/{id_or_name}` → Details inkl. **strukturierter** `address` (`full`, `street`, `postcode`, `city`) sowie `phone`, `email`, `website`

> Stand: 2025-09-17

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# http://127.0.0.1:8000  (Docs: /docs)
```

## Konfiguration (Env)

- `CACHE_TTL_MINUTES` (Default: `1440`) – Cache-Gültigkeit
- `SCRAPE_CONCURRENCY` (Default: `8`) – parallele Requests
- `BASE_LIST_URL` (Default: `https://www.hfv.de/vereine`) – Quelle der Vereinsliste
- `USER_AGENT` (Default: `HFV-Vereine-API (+https://github.com/ClemensRau1337/hfv-vereine-scraper-openapi)`)

## Hinweise / Etikette

- Bitte **robots.txt / Nutzungsbedingungen** der Quelle beachten.
- Cache reduziert die Last auf der Zielseite, bitte verantwortungsvoll nutzen.
- Es werden **öffentliche Vereinsdaten** verarbeitet (Adresse/Kontakt).

## Struktur

```
hfv_vereine_api/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ scraper.py
│  ├─ cache.py
│  ├─ models.py
│  └─ utils.py
├─ data/
│  └─ vereine_cache.json
├─ tests/
│  └─ test_api.py
├─ requirements.txt
├─ pyproject.toml
├─ Dockerfile
├─ .gitignore
└─ LICENSE
```

## Attribution

Datenquelle: **HFV.de** – https://www.hfv.de/vereine
