import re
import unicodedata

UMLAUTS = {
    "ä": "ae",
    "Ä": "Ae",
    "ö": "oe",
    "Ö": "Oe",
    "ü": "ue",
    "Ü": "Ue",
    "ß": "ss",
}


def normalize_umlauts(text: str) -> str:
    for src, repl in UMLAUTS.items():
        text = text.replace(src, repl)
    return text


def slugify(text: str) -> str:
    text = normalize_umlauts(text.lower())
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^a-z0-9\s\-\/]", "", text)
    text = text.replace("/", "-")
    text = re.sub(r"\s+", "-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text


def extract_postcode_city(address: str):
    if not address:
        return (None, None)
    m = re.search(r"(\b\d{5}\b)\s+([\wÄÖÜäöüß\-\.\s\(\),]+)", address)
    if not m:
        return (None, None)

    postcode, raw_city = m.group(1), m.group(2).strip()
    raw_city = re.sub(r"\bDeutschland\b", "", raw_city, flags=re.I).strip()
    raw_city = re.sub(r"\(\s*\)", "", raw_city).strip()
    raw_city = re.sub(r"\s{2,}", " ", raw_city)

    return postcode, raw_city or None


def clean_text(s: str | None) -> str | None:
    if s is None:
        return None
    s = " ".join(s.split())
    return s or None
