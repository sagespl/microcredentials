"""Scraper for GPW analyst recommendations published on biznesradar.pl."""
from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from data.db import initialize_database, insert_recommendation

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.biznesradar.pl/rekomendacje/"
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AGPW-bot/1.0"}

_TICKER_RE = re.compile(r"^(?P<ticker>\S+)(?:\s*\((?P<company>.+)\))?$")


def _parse_number(text: str) -> float | None:
    """Parse a Polish-formatted number ("1 117,00", "+18,92%", "-") into a float."""
    if text is None:
        return None
    text = text.strip().replace("\xa0", " ")
    if text in ("", "-"):
        return None
    text = text.replace("%", "").replace(" ", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def _parse_profile(text: str) -> tuple[str, str | None]:
    """Split a "TICKER (Company)" profile cell into (ticker, company_name)."""
    match = _TICKER_RE.match(text.strip())
    if not match:
        return text.strip(), None
    return match.group("ticker"), match.group("company")


def fetch_recommendations_html(url: str = DEFAULT_URL, timeout: float = 10.0) -> str:
    """Download the recommendations page HTML."""
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_recommendations(html: str, source_url: str = DEFAULT_URL) -> list[dict]:
    """Parse the recommendations table HTML into a list of row dicts."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if table is None:
        return []

    rows = table.find_all("tr")[1:]  # skip header row
    results = []
    for row in rows:
        cells = [c.get_text(" ", strip=True) for c in row.find_all("td")]
        if len(cells) < 8:
            continue

        ticker, company_name = _parse_profile(cells[0])
        published_at = cells[6].strip()
        if not published_at:
            continue

        results.append(
            {
                "ticker": ticker,
                "company_name": company_name,
                "recommendation": cells[1].strip() or None,
                "target_price": _parse_number(cells[2]),
                "current_price": _parse_number(cells[3]),
                "potential_pct": _parse_number(cells[4]),
                "price_at_issue": _parse_number(cells[5]),
                "published_at": published_at,
                "author": cells[7].strip() or None,
                "source_url": source_url,
            }
        )
    return results


def save_recommendations(rows: list[dict], path: Path | str | None = None) -> int:
    """Persist parsed recommendation rows into SQLite via upsert."""
    count = 0
    for row in rows:
        insert_recommendation(path=path, **row)
        count += 1
    logger.info("Saved %d recommendation rows", count)
    return count


def scrape_recommendations(url: str = DEFAULT_URL, path: Path | str | None = None) -> int:
    """Fetch, parse and persist analyst recommendations. Returns number of rows saved."""
    html = fetch_recommendations_html(url)
    rows = parse_recommendations(html, source_url=url)
    return save_recommendations(rows, path=path)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Scrape GPW analyst recommendations from biznesradar.pl")
    parser.add_argument("--url", default=DEFAULT_URL, help="Recommendations page URL")
    args = parser.parse_args()

    initialize_database()
    count = scrape_recommendations(args.url)
    logger.info("Scraped and saved %d recommendations", count)


if __name__ == "__main__":
    main()
