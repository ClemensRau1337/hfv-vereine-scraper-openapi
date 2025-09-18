from __future__ import annotations

import asyncio
import os
import re
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from .utils import extract_postcode_city, slugify

BASE_LIST_URL = os.getenv("BASE_LIST_URL", "https://www.hfv.de/vereine")
USER_AGENT = "HFV-Vereine-API (++https://github.com/ClemensRau1337/hfv-vereine-scraper-openapi)"
CONCURRENCY = int(os.getenv("SCRAPE_CONCURRENCY", "8"))


def _absolute(url: str, href: str) -> str:
    return urljoin(url, href)


async def _fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, headers={"User-Agent": USER_AGENT}, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        resp.raise_for_status()
        return await resp.text()


def _sanitize_url(u: str | None) -> str | None:
    if not u:
        return None
    u = u.strip()
    if u.lower() in {"http://", "https://"}:
        return None
    if u.startswith("www."):
        u = "https://" + u
    p = urlparse(u)
    if p.scheme in ("http", "https") and p.netloc:
        return u
    return None


async def scrape_vereine_list(session: aiohttp.ClientSession) -> list[dict]:
    html = await _fetch(session, BASE_LIST_URL)
    soup = BeautifulSoup(html, "html.parser")

    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True)
        if not text:
            continue
        abs_url = _absolute(BASE_LIST_URL, href)
        parsed = urlparse(abs_url)
        if parsed.path.startswith("/vereine/") and parsed.path.rstrip("/") != "/vereine":
            if parsed.netloc and "hfv.de" in parsed.netloc:
                links.add((text, abs_url))

    vereine = []
    seen_slugs = set()
    for name, url in sorted(links, key=lambda x: slugify(x[0])):
        slug = url.rstrip("/").split("/")[-1]
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        vereine.append({"id": slug, "name": name, "url": url})
    return vereine


def _cleanup_city(city: str | None) -> str | None:
    if not city:
        return None
    city = re.sub(r"\bDeutschland\b", "", city, flags=re.I)
    city = re.sub(r"\(\s*\)", "", city)
    city = re.sub(r"\s{2,}", " ", city)
    city = city.strip(" ,")
    return city or None


def _parse_address_from_soup(soup: BeautifulSoup) -> tuple[dict | None, str | None]:
    txt = soup.get_text("\n", strip=True)
    m = re.search(
        r"Anschrift\s*:\s*(.+?)(?:Kontakt|Über uns|Sportschule|Newsletter|Datenschutzerklärung|Impressum|$)",
        txt,
        flags=re.I | re.S,
    )
    block = m.group(1).strip() if m else None

    if not block:
        node = soup.find(string=re.compile(r"Anschrift", re.I))
        if node and node.parent:
            block = re.sub(r"^Anschrift\s*:\s*", "", node.parent.get_text(" ", strip=True), flags=re.I)

    if not block:
        return None, None

    url_match = re.search(r"(https?://\S+|www\.[^\s]+)", block)
    found_url = None
    if url_match:
        found_url = url_match.group(0)
        block = block.replace(found_url, "").strip()
        found_url = _sanitize_url(found_url)

    block = re.sub(r"\s{2,}", " ", block).strip()

    postcode, city = extract_postcode_city(block)
    street = block.split(postcode)[0].strip() if postcode else None
    city = _cleanup_city(city)

    address = {
        "full": block,
        "street": street,
        "postcode": postcode,
        "city": city,
    }
    address = {k: v for k, v in address.items() if v}
    return (address if address else None), found_url


async def scrape_verein_detail(session: aiohttp.ClientSession, url: str) -> dict:
    html = await _fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")

    name = None
    h1 = soup.find("h1")
    if h1:
        name = h1.get_text(" ", strip=True)

    address, extra_url = _parse_address_from_soup(soup)

    email = None
    phone = None
    website = None
    SOCIAL = (
        "facebook.com",
        "instagram.com",
        "tiktok.com",
        "youtube.com",
        "linkedin.com",
        "x.com",
        "twitter.com",
        "open.spotify.com",
    )
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("mailto:"):
            email = href.replace("mailto:", "").strip()
        elif href.startswith("tel:"):
            phone = href.replace("tel:", "").strip()
        elif href.startswith("http"):
            host = urlparse(href).netloc
            if "hfv.de" not in host and not any(s in href for s in SOCIAL):
                website = href
                break

    if not website and extra_url:
        website = extra_url

    website = _sanitize_url(website)

    if website and website.strip().lower() in {"http://", "https://"}:
        website = None

    detail = {
        "name": name,
        "address": address,
        "phone": phone,
        "email": email,
        "website": website,
    }

    return {k: v for k, v in detail.items() if v}


async def scrape_all() -> dict[str, dict]:
    connector = aiohttp.TCPConnector(limit_per_host=CONCURRENCY, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        vereine = await scrape_vereine_list(session)

        sem = asyncio.Semaphore(CONCURRENCY)

        async def work(v):
            async with sem:
                details = await scrape_verein_detail(session, v["url"])
                data = {**v, **details}
                return v["id"], data

        results = await asyncio.gather(*[work(v) for v in vereine], return_exceptions=True)
        out: dict[str, dict] = {}
        for res in results:
            if isinstance(res, Exception):
                continue
            slug, data = res
            out[slug] = data
        return out
