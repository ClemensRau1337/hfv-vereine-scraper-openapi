# hfv-vereine-scraper-openapi

[![CI](https://img.shields.io/github/actions/workflow/status/ClemensRau1337/hfv-vereine-scraper-openapi/ci.yml?label=CI)](../../actions/workflows/ci.yml)
[![Release Deploy](https://img.shields.io/github/actions/workflow/status/ClemensRau1337/hfv-vereine-scraper-openapi/release-deploy.yml?label=release%20deploy)](../../actions/workflows/release-deploy.yml)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/ClemensRau1337/hfv-vereine-scraper-openapi?sort=semver)](https://github.com/ClemensRau1337/hfv-vereine-scraper-openapi/releases)
[![Last Commit](https://img.shields.io/github/last-commit/ClemensRau1337/hfv-vereine-scraper-openapi)](https://github.com/ClemensRau1337/hfv-vereine-scraper-openapi/commits)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen?logo=fastapi)](https://5lsowpjrbxps4pukffbiytebdu0tffuf.lambda-url.eu-central-1.on.aws)
[![Demo Status](https://img.shields.io/website?url=https%3A%2F%2F5lsowpjrbxps4pukffbiytebdu0tffuf.lambda-url.eu-central-1.on.aws&label=demo&up_message=online&down_message=offline)](https://5lsowpjrbxps4pukffbiytebdu0tffuf.lambda-url.eu-central-1.on.aws)
[![Docs](https://img.shields.io/badge/OpenAPI-Docs-blue)](https://5lsowpjrbxps4pukffbiytebdu0tffuf.lambda-url.eu-central-1.on.aws/docs)
[![OpenAPI JSON](https://img.shields.io/badge/OpenAPI-JSON-informational)](https://5lsowpjrbxps4pukffbiytebdu0tffuf.lambda-url.eu-central-1.on.aws/openapi.json)

Open-Source FastAPI, der Vereine vom **Hamburger Fußball-Verband** (Quelle: <https://www.hfv.de/vereine>) scraped, cached und über 2 Endpunkte anbietet.

- `GET /vereine` → Liste **nur** mit `id`, `name`, `url`
- `GET /verein/{id_or_name}` → Details inkl. **strukturierter** `address` (`full`, `street`, `postcode`, `city`) sowie `phone`, `email`, `website`

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

Datenquelle: **HFV.de** – <https://www.hfv.de/vereine>
