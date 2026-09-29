#!/usr/bin/env python3
"""Turn DOIs into BibTeX entries for _bibliography/papers.bib.

Used by .github/workflows/add-publication.yml (run by hand from the Actions tab),
which opens a pull request with whatever this script adds. Without --doi the
script instead scans OpenAlex for works linked to the ORCID in the config; that
mode is kept for local use but is no longer scheduled. Review matters there:
OpenAlex groups works by author automatically, and "Y. Xu" gets mixed up.

Lookup order for each new DOI:
  1. Crossref BibTeX (api.crossref.org/works/<doi>/transform/application/x-bibtex)
  2. an entry built from the OpenAlex record, if Crossref has nothing

Only the standard library is required. If PyYAML is installed (the workflow installs it) it is used
to read the config; otherwise a small built-in parser handles the simple format of that file.

Usage:
  python scripts/update_publications.py                     # scan OpenAlex
  python scripts/update_publications.py --doi 10.1234/abc   # add specific DOIs
  python scripts/update_publications.py --dry-run           # print, change nothing
"""

from __future__ import annotations

import argparse
import difflib
import html
import http.client
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "scripts" / "publication_sync.yml"
OPENALEX = "https://api.openalex.org"
CROSSREF = "https://api.crossref.org"
USER_AGENT = "xu-yuhao.github.io publication sync (+https://github.com/xu-yuhao/XU-yuhao.github.io)"

PREPRINT_TYPES = ("preprint", "posted-content")
MARKER = "% ---- Added automatically by scripts/update_publications.py (review before merging) ----"

# Crossref fields we drop: noisy or redundant with doi.
DROP_FIELDS = {"issn", "isbn", "url", "month", "language"}
FIELD_ORDER = [
    "title", "author", "journal", "booktitle", "note", "publisher", "school", "institution",
    "volume", "number", "pages", "year", "doi", "abbr", "bibtex_show",
]


# --------------------------------------------------------------------------- config


def load_config(path: Path) -> dict:
    """Parse the small YAML config without needing PyYAML.

    Supports `key: value`, `key: [a, b]`, and block lists (`- item`). That is all
    publication_sync.yml uses; anything fancier should go through PyYAML.
    """
    try:
        import yaml  # type: ignore

        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except ImportError:
        pass

    config: dict = {}
    key = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = re.sub(r"(^|\s)#.*$", "", raw).rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        is_item = stripped.startswith("- ")
        indented = line[0] in " \t"
        # List items under `key:` may be indented or start at column 0; both are valid YAML.
        if key is not None and (indented or (is_item and (config[key] is None or isinstance(config[key], list)))):
            if is_item:
                if not isinstance(config[key], list):
                    config[key] = []
                config[key].append(_scalar(stripped[2:]))
            elif ":" in stripped:
                if not isinstance(config[key], dict):
                    config[key] = {}
                k, v = _split_key(stripped)
                config[key][_scalar(k)] = _scalar(v)
            continue
        key, value = _split_key(stripped)
        key, value = _scalar(key), value.strip()
        if value.startswith("[") and not value.endswith("]"):
            raise SystemExit(f"{path}: write the list for `{key}` on one line, or install PyYAML (pip install pyyaml)")
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            config[key] = [_scalar(v) for v in inner.split(",")] if inner else []
        else:
            config[key] = _scalar(value)
    return config


def _split_key(line: str) -> tuple[str, str]:
    """Split `key: value`, allowing a quoted key that itself contains a colon."""
    if line[:1] in "\"'":
        end = line.find(line[0], 1)
        if end > 0 and line[end + 1 : end + 2] == ":":
            return line[: end + 1], line[end + 2 :]
    key, _, value = line.partition(":")
    return key, value


def _scalar(text: str):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text.lower() in ("null", "~", ""):
        return None
    if text.lower() in ("true", "false"):
        return text.lower() == "true"
    return text


# --------------------------------------------------------------------------- HTTP


def http_get(url: str, accept: str = "application/json", retries: int = 3, headers: dict | None = None) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept, **(headers or {})})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as err:
            if err.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            return err.code, err.read().decode("utf-8", errors="replace") if err.fp else ""
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException):
            if attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    return 0, ""


NETWORK_ERRORS = (OSError, http.client.HTTPException)  # URLError, TimeoutError, resets


# --------------------------------------------------------------------------- DOIs and existing bib


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip()
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    return doi.lower() or None


def existing_dois(bib_text: str) -> set[str]:
    found = set()
    for match in re.finditer(r"\bdoi\s*=\s*[{\"]\s*([^}\"]+?)\s*[}\"]", bib_text, flags=re.I):
        norm = normalize_doi(match.group(1))
        if norm:
            found.add(norm)
    return found


def title_fingerprint(title: str) -> str:
    """Lowercase letters/digits only, so LaTeX braces, accents and punctuation don't matter."""
    text = unicodedata.normalize("NFKD", clean_text(title)).encode("ascii", "ignore").decode()
    text = re.sub(r"\\[a-zA-Z]+", "", text)  # drop LaTeX commands like \textit
    return re.sub(r"[^a-z0-9]", "", text.lower())


def existing_titles(bib_text: str) -> dict[str, tuple]:
    """Map title fingerprint -> (entry key, has DOI, entry type, year, title) for every entry in the bib file.

    Entries typed in by hand often have no DOI. Matching on the title keeps them from being proposed
    a second time, and lets the script fill in the missing DOI instead.
    """
    titles: dict[str, tuple] = {}
    for match in re.finditer(r"@\w+\s*\{", bib_text):
        parsed = parse_bibtex_entry(bib_text[match.start():])
        if parsed and parsed[2].get("title"):
            fields = parsed[2]
            fingerprint = title_fingerprint(fields["title"])
            year = int(fields["year"]) if str(fields.get("year", "")).isdigit() else None
            if fingerprint:
                titles.setdefault(fingerprint, (parsed[1], bool(fields.get("doi")), parsed[0], year, clean_text(fields["title"])))
    return titles


def find_title_match(known_titles: dict, fingerprint: str, year) -> tuple[str, tuple] | tuple[None, None]:
    """Exact title match first; otherwise a near-identical title on an entry that still lacks a DOI.

    CVs often carry a working title ("...Algorithms" vs. the published "...an Algorithm"), so a DOI-less
    entry whose title is at least 90% similar and whose year is within one year counts as the same paper.
    """
    if not fingerprint:
        return None, None
    if fingerprint in known_titles:
        return fingerprint, known_titles[fingerprint]
    best, best_ratio = None, 0.9
    for fp, info in known_titles.items():
        if info[1]:
            continue
        if year and info[3] and abs(int(year) - info[3]) > 1:
            continue
        ratio = difflib.SequenceMatcher(None, fingerprint, fp).ratio()
        if ratio >= best_ratio:
            best, best_ratio = fp, ratio
    return (best, known_titles[best]) if best else (None, None)


def insert_doi(bib_text: str, key: str, doi: str) -> str:
    """Add a doi field as the first field of entry `key`."""
    match = re.search(r"(@\w+\s*\{\s*" + re.escape(key) + r"\s*,[ \t]*\n?)", bib_text)
    if not match:
        return bib_text
    return bib_text[: match.end()] + f"  doi = {{{doi}}},\n" + bib_text[match.end():]


def existing_keys(bib_text: str) -> set[str]:
    return {m.group(1) for m in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib_text)}


# --------------------------------------------------------------------------- OpenAlex


@dataclass
class Work:
    doi: str
    title: str
    year: int | None
    work_type: str
    venue: str | None
    venue_type: str | None
    publisher: str | None
    volume: str | None
    issue: str | None
    first_page: str | None
    last_page: str | None
    authors: list[str]
    openalex_id: str
    matched_author: dict = field(default_factory=dict)


def openalex_query(filter_expr: str, api_key: str | None, fetch=http_get) -> list[dict]:
    """List works matching a filter, following cursor pages.

    OpenAlex has required a (free) API key since Feb 2026; the old `mailto` polite pool is gone.
    The key goes in an Authorization header so it never shows up in logged URLs.
    """
    results: list[dict] = []
    cursor = "*"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
    while cursor:
        params = {"filter": filter_expr, "per-page": "100", "cursor": cursor}
        status, body = fetch(f"{OPENALEX}/works?{urllib.parse.urlencode(params, safe=':|,')}", headers=headers)
        if status == 429:
            raise RuntimeError("OpenAlex returned HTTP 429 (daily budget or rate limit). Is OPENALEX_API_KEY set?")
        if status != 200:
            raise RuntimeError(f"OpenAlex returned HTTP {status} for filter {filter_expr!r}: {body[:300]}")
        data = json.loads(body)
        results.extend(data.get("results", []))
        cursor = (data.get("meta") or {}).get("next_cursor")
        if not data.get("results"):
            break
    return results


def openalex_work(doi: str, api_key: str | None, fetch=http_get) -> dict | None:
    """Single work by DOI (free on OpenAlex). Covers DataCite DOIs such as arXiv and Zenodo."""
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
    try:
        status, body = fetch(f"{OPENALEX}/works/doi:{urllib.parse.quote(doi, safe='/')}", headers=headers)
    except NETWORK_ERRORS:
        return None
    return json.loads(body) if status == 200 else None


def work_from_openalex(record: dict, orcid: str | None, author_ids: set[str]) -> Work | None:
    doi = normalize_doi(record.get("doi"))
    if not doi:
        return None
    location = record.get("primary_location") or {}
    source = location.get("source") or {}
    biblio = record.get("biblio") or {}
    authors = []
    matched: dict = {}
    for authorship in record.get("authorships") or []:
        author = authorship.get("author") or {}
        name = author.get("display_name") or authorship.get("raw_author_name") or ""
        authors.append(name)
        a_orcid = (author.get("orcid") or "").rsplit("/", 1)[-1]
        a_id = (author.get("id") or "").rsplit("/", 1)[-1]
        if (orcid and a_orcid == orcid) or (a_id and a_id in author_ids):
            matched = {
                "name": name,
                "raw_name": authorship.get("raw_author_name") or "",
                "position": authorship.get("author_position") or "",
                "institutions": [(i or {}).get("display_name") or "" for i in authorship.get("institutions") or []],
            }
    return Work(
        doi=doi,
        title=clean_text(record.get("title") or record.get("display_name") or ""),
        year=record.get("publication_year"),
        work_type=record.get("type") or "",
        venue=source.get("display_name"),
        venue_type=source.get("type"),
        publisher=source.get("host_organization_name"),
        volume=biblio.get("volume"),
        issue=biblio.get("issue"),
        first_page=biblio.get("first_page"),
        last_page=biblio.get("last_page"),
        authors=authors,
        openalex_id=(record.get("id") or "").rsplit("/", 1)[-1],
        matched_author=matched,
    )


# --------------------------------------------------------------------------- BibTeX


def clean_text(text: str) -> str:
    # Strip real markup (<i>, <sub>, <mml:math>, <jats:italic>) first, then decode entities, so an
    # encoded "&lt;" in a title like "Re &lt; 1" survives as a literal "<".
    text = re.sub(r"</?[A-Za-z][\w:.-]*(?:\s[^<>]*)?/?>", "", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def balance_braces(value: str) -> str:
    """Drop all braces from a value whose braces don't pair up; one stray brace breaks the whole build."""
    depth = 0
    for ch in value:
        depth += {"{": 1, "}": -1}.get(ch, 0)
        if depth < 0:
            break
    return value if depth == 0 else value.replace("{", "").replace("}", "")


def escape_bibtex(text: str) -> str:
    return re.sub(r"(?<!\\)([&%#_])", r"\\\1", text)


def split_name(name: str) -> tuple[str, str]:
    name = name.strip()
    if "," in name:
        last, first = name.split(",", 1)
        return last.strip(), first.strip()
    parts = name.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[-1], " ".join(parts[:-1])


def ascii_slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


STOPWORDS = {"a", "an", "the", "on", "of", "in", "for", "and", "to", "with", "at", "by", "from", "via"}


def make_key(first_author: str, year, title: str, taken: set[str]) -> str:
    last, _ = split_name(first_author) if first_author else ("anon", "")
    words = [w for w in re.findall(r"[A-Za-z0-9]+", title) if w.lower() not in STOPWORDS]
    base = f"{ascii_slug(last) or 'anon'}{year or ''}{ascii_slug(words[0]) if words else ''}"
    key, n = base, 0
    while key in taken:
        n += 1
        key = f"{base}{chr(ord('a') + n - 1)}"
    taken.add(key)
    return key


def parse_bibtex_entry(text: str) -> tuple[str, str, dict[str, str]] | None:
    """Parse one BibTeX entry (as returned by Crossref) into (type, key, fields)."""
    match = re.search(r"@(\w+)\s*\{\s*([^,\s]*)\s*,", text)
    if not match:
        return None
    entry_type, key = match.group(1).lower(), match.group(2)
    pos, fields = match.end(), {}
    n = len(text)
    while pos < n:
        m = re.compile(r"\s*,?\s*([A-Za-z][\w-]*)\s*=\s*").match(text, pos)
        if not m:
            break
        name, pos = m.group(1).lower(), m.end()
        if pos >= n:
            break
        if text[pos] == "{":
            depth, start = 0, pos
            while pos < n:
                if text[pos] == "{":
                    depth += 1
                elif text[pos] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                pos += 1
            value = text[start + 1 : pos]
            pos += 1
        elif text[pos] == '"':
            end = text.index('"', pos + 1)
            value, pos = text[pos + 1 : end], end + 1
        else:
            m2 = re.compile(r"[^,}\s]+").match(text, pos)
            value, pos = (m2.group(0), m2.end()) if m2 else ("", pos)
        fields[name] = value.strip()
    return entry_type, key, fields


def format_entry(entry_type: str, key: str, fields: dict[str, str]) -> str:
    ordered = [f for f in FIELD_ORDER if f in fields] + sorted(f for f in fields if f not in FIELD_ORDER)
    width = max(len(f) for f in ordered)
    lines = [f"@{entry_type}{{{key},"]
    for name in ordered:
        lines.append(f"  {name.ljust(width)} = {{{balance_braces(fields[name])}}},")
    lines.append("}")
    return "\n".join(lines)


def entry_from_crossref(bibtex: str, work: Work | None, key: str, abbr: str | None) -> str | None:
    parsed = parse_bibtex_entry(bibtex)
    if not parsed:
        return None
    entry_type, _, fields = parsed
    # Crossref labels chapters @inbook but gives them a booktitle, which is @incollection in BibTeX terms.
    entry_type = {"inbook": "incollection"}.get(entry_type, entry_type)
    fields = {k: v for k, v in fields.items() if k not in DROP_FIELDS}
    for name in ("title", "journal", "booktitle", "publisher", "note", "school", "institution", "howpublished"):
        if name in fields:
            fields[name] = escape_bibtex(clean_text(fields[name]))
    if "author" in fields:
        fields["author"] = clean_text(fields["author"])
    doi = normalize_doi(fields.get("doi")) or (work.doi if work else None)
    if doi:
        fields["doi"] = doi
    if entry_type == "misc" and "note" not in fields:
        venue = fields.pop("howpublished", "") or fields.get("publisher", "") or (work.venue if work else "")
        if venue:
            fields["note"] = venue
    if abbr:
        fields["abbr"] = abbr
    fields["bibtex_show"] = "true"
    return format_entry(entry_type, key, fields)


def entry_from_openalex(work: Work, key: str, abbr: str | None) -> str:
    venue_type = (work.venue_type or "").lower()
    if work.work_type in ("book-chapter",):
        entry_type, venue_field = "incollection", "booktitle"
    elif work.work_type == "dissertation":
        entry_type, venue_field = "phdthesis", "school"
    elif venue_type == "conference" or work.work_type == "proceedings-article":
        entry_type, venue_field = "inproceedings", "booktitle"
    elif work.work_type in ("preprint", "posted-content"):
        entry_type, venue_field = "misc", "note"  # the site's bib layout shows `note` for @misc
    else:
        entry_type, venue_field = "article", "journal"
    fields: dict[str, str] = {"title": escape_bibtex(work.title)}
    authors = []
    for name in work.authors:
        last, first = split_name(name)
        authors.append(f"{last}, {first}" if first else last)
    if authors:
        fields["author"] = escape_bibtex(" and ".join(authors))
    if work.venue:
        fields[venue_field] = escape_bibtex(clean_text(work.venue))
    if work.publisher and entry_type not in ("phdthesis", "misc"):
        fields["publisher"] = escape_bibtex(work.publisher)
    if work.volume:
        fields["volume"] = str(work.volume)
    if work.issue:
        fields["number"] = str(work.issue)
    if work.first_page:
        pages = str(work.first_page)
        if work.last_page and str(work.last_page) != pages:
            pages += f"--{work.last_page}"
        fields["pages"] = pages
    if work.year:
        fields["year"] = str(work.year)
    fields["doi"] = work.doi
    if abbr:
        fields["abbr"] = abbr
    fields["bibtex_show"] = "true"
    return format_entry(entry_type, key, fields)


def crossref_bibtex(doi: str, mailto: str | None, fetch=http_get) -> str | None:
    url = f"{CROSSREF}/works/{urllib.parse.quote(doi, safe='/')}/transform/application/x-bibtex"
    if mailto:
        url += f"?mailto={urllib.parse.quote(mailto)}"
    try:
        status, body = fetch(url, accept="application/x-bibtex")
    except NETWORK_ERRORS:
        return None
    if status == 200 and body.lstrip().startswith("@"):
        return body
    return None


def crossref_work(doi: str, mailto: str | None, fetch=http_get) -> Work | None:
    """Minimal metadata for --doi additions when OpenAlex has no record."""
    url = f"{CROSSREF}/works/{urllib.parse.quote(doi, safe='/')}"
    if mailto:
        url += f"?mailto={urllib.parse.quote(mailto)}"
    try:
        status, body = fetch(url)
    except NETWORK_ERRORS:
        return None
    if status != 200:
        return None
    msg = json.loads(body).get("message", {})
    authors = [" ".join(p for p in (a.get("given"), a.get("family")) if p) or a.get("name", "") for a in msg.get("author", [])]
    year = None
    for date_key in ("published-print", "published-online", "issued"):
        parts = (msg.get(date_key) or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            year = parts[0][0]
            break
    first, _, last = (msg.get("page") or "").partition("-")
    venue = (msg.get("container-title") or [None])[0]
    crossref_type = msg.get("type", "")
    return Work(
        doi=doi,
        title=clean_text((msg.get("title") or [""])[0]),
        year=year,
        work_type={"journal-article": "article", "proceedings-article": "proceedings-article", "book-chapter": "book-chapter",
                   "posted-content": "preprint", "dissertation": "dissertation"}.get(crossref_type, crossref_type),
        venue=venue,
        venue_type="conference" if crossref_type == "proceedings-article" else "journal",
        publisher=msg.get("publisher"),
        volume=msg.get("volume"),
        issue=msg.get("issue"),
        first_page=first or None,
        last_page=last or None,
        authors=authors,
        openalex_id="",
    )


# --------------------------------------------------------------------------- main flow


def collect_candidates(config: dict, api_key: str | None, fetch=http_get) -> list[Work]:
    orcid = (config.get("orcid") or "").strip() or None
    if orcid:
        orcid = orcid.rsplit("/", 1)[-1]
    author_ids = {str(a).rsplit("/", 1)[-1] for a in (config.get("openalex_author_ids") or []) if a}
    if not orcid and not author_ids:
        raise SystemExit("scripts/publication_sync.yml needs an `orcid` or `openalex_author_ids` entry.")
    since = config.get("from_publication_date")
    date_filter = f",from_publication_date:{since}" if since else ""
    records: list[dict] = []
    if orcid:
        records += openalex_query(f"authorships.author.orcid:{orcid}{date_filter}", api_key, fetch)
    if author_ids:
        records += openalex_query(f"authorships.author.id:{'|'.join(sorted(author_ids))}{date_filter}", api_key, fetch)
    allowed_types = set(config.get("work_types") or [])
    works: dict[str, Work] = {}
    for record in records:
        work = work_from_openalex(record, orcid, author_ids)
        if not work or work.doi in works:
            continue
        if allowed_types and work.work_type not in allowed_types:
            continue
        works[work.doi] = work
    return sorted(works.values(), key=lambda w: (w.year or 0, w.title), reverse=True)


def venue_abbr(config: dict, venue: str | None) -> str | None:
    table = config.get("venue_abbreviations") or {}
    if not venue or not isinstance(table, dict):
        return None
    for name, abbr in table.items():
        if name.lower() == venue.lower():
            return abbr
    return None


def build_summary(
    added: list[tuple[Work, str, str]],
    filled: list[tuple[Work, str, str]],
    skipped_ignored: int,
    orcid: str | None,
    same_title: dict[str, str] | None = None,
    unresolved: list[str] | None = None,
    weekly: bool = True,
) -> str:
    same_title = same_title or {}
    lines = [
        "Weekly OpenAlex check found publications that are not in `_bibliography/papers.bib` yet."
        if weekly
        else "Entries for the DOIs you entered, with metadata from Crossref (or OpenAlex when Crossref has none).",
        "",
    ]
    if weekly:
        lines += [
            "**Check every entry before merging.** OpenAlex assigns works to authors automatically and",
            "common names get mixed up. For an entry that is not yours:",
            "",
            "1. delete it from `papers.bib` in this PR (Files changed → ⋯ → Edit file), and",
            "2. add its DOI under `ignore_dois` in `scripts/publication_sync.yml`, so it is not proposed again.",
            "",
        ]
    else:
        lines += ["**Check the entries below, then merge this pull request to publish them.**", ""]
    if weekly:
        lines += [
            "While this PR is open and has your edits, the weekly check skips itself so your edits are not overwritten.",
            "If none of these papers are yours, add their DOIs to `ignore_dois` on `main` before closing this PR.",
            "",
        ]
    if added:
        lines += [
            "### New entries",
            "",
            "| # | Year | Title | Venue | Matched author (position; institutions) | Source |",
            "|---|------|-------|-------|------------------------------------------|--------|",
        ]
    for i, (work, key, source) in enumerate(added, 1):
        m = work.matched_author
        institutions = ", ".join(i for i in m.get("institutions") or [] if i) or "no institution listed"
        who = "n/a (added by DOI)" if not m else f"{m.get('raw_name') or m.get('name')} ({m.get('position')}; {institutions})"
        title = work.title.replace("|", "\\|")
        if work.doi in same_title:
            title += f" **(same title as existing `{same_title[work.doi]}`: preprint vs. published version? keep one)**"
        lines.append(
            f"| {i} | {work.year or ''} | [{title}](https://doi.org/{work.doi}) `{key}` | {work.venue or ''} | {who} | {source} |"
        )
    if filled:
        lines += [
            "",
            "### DOIs added to existing entries",
            "",
            "These entries were already in the file without a DOI. Check that each pair of titles is the same paper.",
            "",
            "| Entry | Title in papers.bib | DOI | Title from Crossref/OpenAlex |",
            "|-------|---------------------|-----|------------------------------|",
        ]
        for work, key, old_title in filled:
            bar = chr(92) + "|"
            lines.append(f"| `{key}` | {old_title.replace('|', bar)} | [{work.doi}](https://doi.org/{work.doi}) | {work.title.replace('|', bar)} |")
    if unresolved:
        lines += ["", "### DOIs that could not be added", "", "Neither Crossref nor OpenAlex returned metadata for:", ""]
        lines += [f"- `{doi}`" for doi in unresolved]
    if weekly:
        lines += ["", f"ORCID used: `{orcid or 'none'}`. DOIs skipped via ignore list: {skipped_ignored}."]
    return "\n".join(lines) + "\n"


def run(argv: list[str] | None = None, fetch=http_get) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--bib", type=Path, default=None, help="BibTeX file to append to (default: from config)")
    parser.add_argument("--doi", nargs="*", default=None, help="Add these DOIs instead of scanning OpenAlex")
    parser.add_argument("--summary", type=Path, default=None, help="Write a Markdown summary (PR body) here")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    bib_path = args.bib or (REPO_ROOT / (config.get("target_bib") or "_bibliography/papers.bib"))
    bib_text = bib_path.read_text(encoding="utf-8") if bib_path.exists() else ""
    known = existing_dois(bib_text)
    known_titles = existing_titles(bib_text)
    ignored = {normalize_doi(d) for d in (config.get("ignore_dois") or []) if d}
    api_key = os.environ.get("OPENALEX_API_KEY") or None
    mailto = config.get("mailto")

    if args.doi:
        # Whitespace or commas only: some real DOIs (old Wiley SICI ones) contain semicolons.
        requested = [normalize_doi(d) for chunk in args.doi for d in re.split(r"[\s,]+", chunk) if d.strip()]
        candidates = []
        for doi in dict.fromkeys(d for d in requested if d):
            if doi in known:
                prefix = "::notice::" if os.environ.get("GITHUB_ACTIONS") else ""
                print(f"{prefix}{doi} is already in {bib_path.name}; nothing to add for it.")
                continue
            record = None if (work := crossref_work(doi, mailto, fetch)) else openalex_work(doi, api_key, fetch)
            work = work or (work_from_openalex(record, None, set()) if record else None)
            candidates.append(work or Work(doi, "", None, "", None, None, None, None, None, None, None, [], ""))
    else:
        candidates = collect_candidates(config, api_key, fetch)
    # Published versions before preprints, so a hand-entered article gets the journal DOI, not the preprint's.
    candidates.sort(key=lambda w: w.work_type in PREPRINT_TYPES)

    # Keys must be unique across every .bib file the site renders, not just the one being appended to.
    taken = set(existing_keys(bib_text))
    for other in bib_path.parent.glob("*.bib"):
        if other.resolve() != bib_path.resolve():
            taken |= existing_keys(other.read_text(encoding="utf-8"))
    added: list[tuple[Work, str, str]] = []
    filled: list[tuple[Work, str, str]] = []
    same_title: dict[str, str] = {}
    unresolved: list[str] = []
    entries: list[str] = []
    skipped_ignored = 0
    for work in candidates:
        if work.doi in known:
            continue
        if work.doi in ignored:
            skipped_ignored += 1
            continue
        fingerprint = title_fingerprint(work.title) if work.title else ""
        match_fp, match = find_title_match(known_titles, fingerprint, work.year)
        if match:
            key, has_doi, entry_type, match_year, match_title = match
            is_preprint = work.work_type in PREPRINT_TYPES
            if not has_doi and (not is_preprint or entry_type in ("misc", "unpublished")):
                filled.append((work, key, match_title))
                known_titles[match_fp] = (key, True, entry_type, match_year, match_title)
                known.add(work.doi)
                continue
            # Same title but a different DOI (preprint vs. journal version, or a generic title such as
            # "Editorial"): propose it anyway and flag it, rather than silently dropping it.
            same_title[work.doi] = key
        bibtex = crossref_bibtex(work.doi, mailto, fetch)
        parsed = parse_bibtex_entry(bibtex) if bibtex else None
        if parsed:
            fields = parsed[2]
            first_author = fields.get("author", "").split(" and ")[0]
            key = make_key(first_author, fields.get("year") or work.year, clean_text(fields.get("title", "")), taken)
            venue = clean_text(fields.get("journal") or fields.get("booktitle") or "") or work.venue
        else:
            key = make_key(work.authors[0] if work.authors else "", work.year, work.title, taken)
            venue = work.venue
        abbr = venue_abbr(config, venue)
        entry = entry_from_crossref(bibtex, work, key, abbr) if parsed else None
        source = "Crossref"
        if entry is None:
            if not work.title:
                print(f"skip {work.doi}: neither Crossref nor OpenAlex has metadata for it", file=sys.stderr)
                unresolved.append(work.doi)
                continue
            entry = entry_from_openalex(work, key, abbr)
            source = "OpenAlex"
        entries.append(entry)
        added.append((work, key, source))
        known.add(work.doi)
        if fingerprint:
            known_titles.setdefault(fingerprint, (key, True, parsed[0] if parsed else "", work.year, work.title))

    if not entries and not filled:
        if unresolved and args.doi:
            print("Could not add: " + ", ".join(unresolved), file=sys.stderr)
            return 1
        print("No new publications.")
        return 0

    new_text = bib_text
    for work, key, _ in filled:
        new_text = insert_doi(new_text, key, work.doi)
        print(f"{key}: added doi {work.doi}")
    if entries:
        block = "\n\n".join(entries)
        print(block)
        if new_text and not new_text.endswith("\n"):
            new_text += "\n"
        new_text += f"\n{MARKER}\n\n{block}\n"
    if args.dry_run:
        return 0
    bib_path.write_text(new_text, encoding="utf-8")
    if args.summary:
        orcid = (config.get("orcid") or "").rsplit("/", 1)[-1] or None
        args.summary.write_text(build_summary(added, filled, skipped_ignored, orcid, same_title, unresolved, weekly=not args.doi), encoding="utf-8")
    print(f"Added {len(entries)} new entr{'y' if len(entries) == 1 else 'ies'}, filled {len(filled)} DOI(s) in {bib_path}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
