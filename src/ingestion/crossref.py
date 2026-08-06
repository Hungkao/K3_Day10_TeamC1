from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import logging
import re
from pathlib import Path
import time

import requests

from core.config import Settings

logger = logging.getLogger(__name__)

CROSSREF_API_URL = "https://api.crossref.org/works"


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _clean_text(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_date(date_dict: dict | None) -> str:
    if not date_dict or not isinstance(date_dict, dict):
        return ""
    date_parts = date_dict.get("date-parts")
    if date_parts and isinstance(date_parts, list) and len(date_parts) > 0:
        parts = date_parts[0]
        if len(parts) >= 3:
            return f"{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d}"
        elif len(parts) == 2:
            return f"{parts[0]:04d}-{parts[1]:02d}-01"
        elif len(parts) == 1:
            return f"{parts[0]:04d}-01-01"
    date_time = date_dict.get("date-time")
    if date_time and isinstance(date_time, str):
        return date_time.split("T")[0]
    return ""


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref payload into a list of PaperRecord objects."""
    records: list[PaperRecord] = []

    message = payload.get("message", {}) if isinstance(payload, dict) else {}
    items = message.get("items", []) if isinstance(message, dict) else []

    for item in items:
        if not isinstance(item, dict):
            continue

        paper_id = str(item.get("DOI") or item.get("id") or "").strip()

        title_raw = item.get("title", [])
        if isinstance(title_raw, list):
            title_str = " ".join(str(t) for t in title_raw)
        else:
            title_str = str(title_raw or "")
        title = _clean_text(title_str)

        summary_raw = item.get("abstract") or item.get("summary") or ""
        summary = _clean_text(str(summary_raw))

        if not paper_id or (not title and not summary):
            continue

        authors: list[str] = []
        raw_authors = item.get("author", [])
        if isinstance(raw_authors, list):
            for author in raw_authors:
                if isinstance(author, dict):
                    given = author.get("given", "").strip()
                    family = author.get("family", "").strip()
                    name = author.get("name", "").strip()
                    if given or family:
                        full_name = f"{given} {family}".strip()
                    elif name:
                        full_name = name
                    else:
                        full_name = ""
                    if full_name:
                        authors.append(full_name)
                elif isinstance(author, str) and author.strip():
                    authors.append(author.strip())

        categories: list[str] = []
        raw_subjects = item.get("subject", [])
        if isinstance(raw_subjects, list):
            categories = [str(s).strip() for s in raw_subjects if str(s).strip()]
        primary_category = categories[0] if categories else ""

        published = (
            _extract_date(item.get("published-online"))
            or _extract_date(item.get("published-print"))
            or _extract_date(item.get("published"))
            or _extract_date(item.get("issued"))
            or _extract_date(item.get("created"))
        )
        updated = (
            _extract_date(item.get("deposited"))
            or _extract_date(item.get("indexed"))
            or published
        )

        abs_url = str(item.get("URL") or (f"https://doi.org/{paper_id}" if paper_id else "")).strip()
        pdf_url = ""
        link_list = item.get("link", [])
        if isinstance(link_list, list):
            for link_item in link_list:
                if isinstance(link_item, dict):
                    content_type = str(link_item.get("content-type", "")).lower()
                    intended_app = str(link_item.get("intended-application", "")).lower()
                    url_val = link_item.get("URL", "").strip()
                    if url_val and ("pdf" in content_type or "pdf" in intended_app):
                        pdf_url = url_val
                        break
        if not pdf_url:
            pdf_url = abs_url

        container_titles = item.get("container-title", [])
        if isinstance(container_titles, list) and container_titles:
            comment = str(container_titles[0]).strip()
        elif isinstance(container_titles, str):
            comment = container_titles.strip()
        else:
            comment = str(item.get("publisher", "")).strip()

        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=comment,
            )
        )

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Fetch raw records from Crossref API, save raw response, and parse to list[PaperRecord]."""
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results,
    }
    headers = {
        "User-Agent": "AITCLab/1.0 (mailto:student@lab.aitc.edu.vn)"
    }

    max_retries = 3
    retry_delay = 2.0
    payload: dict = {}

    for attempt in range(max_retries):
        try:
            response = requests.get(CROSSREF_API_URL, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                payload = response.json()
                break
            elif response.status_code in {429, 500, 502, 503, 504}:
                time.sleep(retry_delay * (2 ** attempt))
            else:
                response.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Failed to fetch data from Crossref API: {e}") from e
            time.sleep(retry_delay * (2 ** attempt))

    settings.paths.raw_api_response.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.paths.raw_api_response, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    records = parse_crossref_payload(payload)

    settings.paths.raw_records_json.parent.mkdir(parents=True, exist_ok=True)
    records_dict = [asdict(rec) for rec in records]
    with open(settings.paths.raw_records_json, "w", encoding="utf-8") as f:
        json.dump(records_dict, f, ensure_ascii=False, indent=2)

    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Read JSON snapshot and map into list[PaperRecord]."""
    if not path.exists():
        raise FileNotFoundError(f"Raw records file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return parse_crossref_payload(data)
    elif isinstance(data, list):
        return [PaperRecord(**item) for item in data]
    else:
        raise ValueError(f"Unexpected JSON data format in {path}: expected list or dict.")

