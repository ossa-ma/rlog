import json
import re
from datetime import datetime
from typing import Any

import aiohttp
from bs4 import BeautifulSoup


class MetadataFetchError(Exception):
    """Custom exception for metadata fetch errors."""

    pass


def _normalize_name(name: str | None) -> str | None:
    """Normalize author names (handle Last, First format)."""
    if not name:
        return None
    # Handle "Last, First" format
    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        if len(parts) == 2:
            return f"{parts[1]} {parts[0]}"
    # Handle multiple spaces/newlines
    return re.sub(r"\s+", " ", name).strip()


def _parse_date(date_string: str) -> str | None:
    """Parse various date formats into YYYY-MM-DD."""
    if not date_string:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%m/%d/%Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_string.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # If all parsing fails, try to extract YYYY-MM-DD pattern
    match = re.search(r"\d{4}-\d{2}-\d{2}", date_string)
    if match:
        return match.group(0)

    return None


async def fetch_metadata(url: str, timeout: int = 10) -> dict[str, str | None]:
    """
    Fetch metadata from URL (matches Raycast extraction quality).

    Args:
        url: URL to fetch metadata from
        timeout: Request timeout in seconds

    Returns:
        Dictionary with title, author, publishedDate (YYYY-MM-DD format)

    Raises:
        MetadataFetchError: If fetch fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            ) as response:
                if response.status != 200:
                    raise MetadataFetchError(f"HTTP {response.status}")

                content_type = response.headers.get("content-type", "")

                # Handle PDF
                if "application/pdf" in content_type:
                    filename = url.split("/")[-1].replace(".pdf", "")
                    return {"title": filename, "author": None, "publishedDate": None}

                # Only handle HTML
                if "text/html" not in content_type:
                    return {"title": url, "author": None, "publishedDate": None}

                html = await response.text()

    except aiohttp.ClientError as e:
        raise MetadataFetchError(f"Network error: {str(e)}")
    except Exception as e:
        raise MetadataFetchError(f"Unexpected error: {str(e)}")

    return _extract_metadata_from_html(html, url)


def _extract_metadata_from_html(html: str, url: str) -> dict[str, str | None]:
    """Extract metadata from HTML (matches Raycast logic)."""
    soup = BeautifulSoup(html, "lxml")

    # Try JSON-LD first (most reliable)
    json_ld_data = None
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, dict) and data.get("@type") in [
                "Article",
                "BlogPosting",
                "NewsArticle",
                "ScholarlyArticle",
            ]:
                json_ld_data = data
                break
        except (json.JSONDecodeError, AttributeError):
            pass

    # Extract Title
    title = _extract_title(soup, url, json_ld_data)

    # Extract Author
    author = _extract_author(soup, url, json_ld_data)

    # Extract Date
    published_date = _extract_date(soup, json_ld_data)

    return {
        "title": title or url,
        "author": author,
        "publishedDate": published_date,
    }


def _extract_title(soup: BeautifulSoup, url: str, json_ld: dict | None) -> str | None:
    """Extract title with Raycast-level sophistication."""
    # 1. JSON-LD
    if json_ld:
        if json_ld.get("headline"):
            return json_ld["headline"].strip()
        if json_ld.get("name"):
            return json_ld["name"].strip()

    # 2. ArXiv special handling
    if "arxiv.org" in url:
        h1_title = soup.find("h1", class_="title")
        if h1_title:
            text = h1_title.get_text()
            # Remove "Title:" prefix
            return re.sub(r"^Title:\s*", "", text, flags=re.IGNORECASE).strip()

    # 3. Citation title
    citation_title = soup.find("meta", {"name": "citation_title"})
    if citation_title and citation_title.get("content"):
        return citation_title["content"].strip()

    # 4. DC title
    dc_title = soup.find("meta", {"name": re.compile(r"DC\.title|dc\.title", re.I)})
    if dc_title and dc_title.get("content"):
        return dc_title["content"].strip()

    # 5. Open Graph title
    og_title = soup.find("meta", {"property": "og:title"})
    page_title = soup.find("title")
    page_title_text = page_title.get_text().strip() if page_title else ""

    if og_title and og_title.get("content"):
        og_text = og_title["content"].strip()
        if og_text != page_title_text:
            return og_text

    # 6. Smart H1 extraction (filter out site titles)
    h1s = soup.find_all("h1")
    if h1s:
        # Filter out likely site titles
        content_h1s = []
        for h1 in h1s:
            h1_classes = h1.get("class", None)
            if not isinstance(h1_classes, list):
                h1_classes = [str(h1_classes)]

            h1_id = str(h1.get("id", ""))

            attributes = h1_classes + [h1_id]
            if not any(x in attributes for x in ["menu-title", "site-title", "logo"]):
                content_h1s.append(h1)

        if content_h1s:
            # Prefer h1 inside main/article
            for h1 in content_h1s:
                if h1.find_parent(["main", "article"]):
                    return h1.get_text().strip()
            # Fallback to first filtered h1
            return content_h1s[0].get_text().strip()

    # 7. Page title fallback
    if page_title_text:
        return page_title_text

    return None


def _get_str_attr(tag: Any, attr: str) -> str | None:
    """Safely get string attribute from BeautifulSoup tag."""
    val = tag.get(attr)
    if isinstance(val, list):
        return " ".join(str(v) for v in val)
    return str(val) if val is not None else None


def _extract_author(soup: BeautifulSoup, url: str, json_ld: dict | None) -> str | None:
    """Extract author with academic paper handling."""
    # Check if academic paper
    citation_authors = [
        _normalize_name(_get_str_attr(meta, "content"))
        for meta in soup.find_all("meta", {"name": "citation_author"})
        if _get_str_attr(meta, "content")
    ]

    is_academic = (
        len(citation_authors) > 0
        or "arxiv.org" in url
        or "openreview.net" in url
        or (json_ld and json_ld.get("@type") == "ScholarlyArticle")
    )

    # 1. JSON-LD author
    if json_ld and json_ld.get("author"):
        authors_data = json_ld["author"]
        if not isinstance(authors_data, list):
            authors_data = [authors_data]

        authors = [
            _normalize_name(a.get("name") if isinstance(a, dict) else a) for a in authors_data
        ]
        authors = [a for a in authors if a]

        if authors:
            if is_academic:
                return f"{authors[0]} et al." if len(authors) > 1 else authors[0]
            return authors[0] if len(authors) == 1 else ", ".join(authors[:4])

    # 2. Citation authors (academic)
    if citation_authors:
        return f"{citation_authors[0]} et al." if len(citation_authors) > 1 else citation_authors[0]

    # 3. DC creator
    dc_authors = [
        _normalize_name(_get_str_attr(meta, "content"))
        for meta in soup.find_all(
            "meta", {"name": re.compile(r"DC\.(creator|author)|dc\.(creator|author)", re.I)}
        )
        if _get_str_attr(meta, "content")
    ]
    if dc_authors:
        return f"{dc_authors[0]} et al." if len(dc_authors) > 1 else dc_authors[0]

    # 4. Standard meta tags
    for name in ["author", "article:author", "og:author", "twitter:creator"]:
        meta = soup.find("meta", {"name": name}) or soup.find("meta", {"property": name})
        content = _get_str_attr(meta, "content") if meta else None
        if content:
            author = _normalize_name(content)
            if author:
                return author.lstrip("@")  # Remove @ from Twitter handles

    # 5. rel=author link
    author_link = soup.find("a", {"rel": "author"})
    if author_link:
        return _normalize_name(author_link.get_text())

    # 6. Class-based
    for class_name in ["author", "byline"]:
        elem = soup.find(class_=class_name)
        if elem:
            return _normalize_name(elem.get_text())

    return None


def _extract_date(soup: BeautifulSoup, json_ld: dict | None) -> str | None:
    """Extract publication date in YYYY-MM-DD format."""
    # 1. JSON-LD
    if json_ld:
        for key in ["datePublished", "dateCreated"]:
            if json_ld.get(key):
                return _parse_date(json_ld[key])

    # 2. Meta tags (in priority order)
    meta_names = [
        "citation_publication_date",
        "citation_date",
        "DC.date",
        "dc.date",
        "DCTERMS.issued",
        "article:published_time",
        "date",
        "og:published_time",
    ]

    for name in meta_names:
        meta = soup.find("meta", {"name": name}) or soup.find("meta", {"property": name})
        content = _get_str_attr(meta, "content") if meta else None
        if content:
            date = _parse_date(content)
            if date:
                return date

    # 3. <time> element
    time_elem = soup.find("time", {"datetime": True})
    if time_elem:
        return _parse_date(time_elem["datetime"])

    time_elem = soup.find("time")
    if time_elem and time_elem.get("datetime"):
        return _parse_date(time_elem["datetime"])

    # 4. Text heuristic "Published: [Date]"
    body_text = soup.get_text()
    match = re.search(r"Published:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})", body_text)
    if match:
        return _parse_date(match.group(1))

    return None


async def fetch_metadata_safe(url: str) -> dict[str, str | None]:
    """
    Safely fetch metadata with fallback.

    Returns:
        Metadata dictionary (never raises)
    """
    try:
        return await fetch_metadata(url)
    except Exception:
        return {
            "title": url,
            "author": None,
            "publishedDate": None,
        }
