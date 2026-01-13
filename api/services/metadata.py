"""Metadata extraction service for URLs."""

from datetime import datetime
from typing import Any

import aiohttp
from bs4 import BeautifulSoup


class MetadataFetchError(Exception):
    """Custom exception for metadata fetch errors."""
    pass


async def fetch_metadata(url: str, timeout: int = 10) -> dict[str, str | None]:
    """
    Fetch metadata (title, author, date) from URL.

    Args:
        url: URL to fetch metadata from
        timeout: Request timeout in seconds

    Returns:
        Dictionary with title, author, publishedDate (None if not found)

    Raises:
        MetadataFetchError: If fetch fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; rlog/1.0; +https://github.com/ossama/rlog)"
                }
            ) as response:
                if response.status != 200:
                    raise MetadataFetchError(f"HTTP {response.status} when fetching {url}")

                html = await response.text()

    except aiohttp.ClientError as e:
        raise MetadataFetchError(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise MetadataFetchError(f"Unexpected error fetching metadata: {str(e)}")

    return extract_metadata_from_html(html, url)


def extract_metadata_from_html(html: str, url: str) -> dict[str, str | None]:
    """
    Extract metadata from HTML content.

    Attempts to extract from:
    1. Open Graph tags (og:title, og:author, article:published_time)
    2. Twitter Card tags (twitter:title, twitter:creator)
    3. JSON-LD structured data
    4. Standard HTML meta tags
    5. Fallback to <title> tag

    Args:
        html: HTML content
        url: Original URL (for context)

    Returns:
        Dictionary with title, author, publishedDate
    """
    soup = BeautifulSoup(html, "lxml")

    metadata: dict[str, str | None] = {
        "title": None,
        "author": None,
        "publishedDate": None,
    }

    # Try Open Graph tags first (most reliable)
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        metadata["title"] = og_title["content"]

    og_author = soup.find("meta", property="article:author")
    if og_author and og_author.get("content"):
        metadata["author"] = og_author["content"]

    og_published = soup.find("meta", property="article:published_time")
    if og_published and og_published.get("content"):
        metadata["publishedDate"] = _parse_date(og_published["content"])

    # Try Twitter Card tags
    if not metadata["title"]:
        twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
        if twitter_title and twitter_title.get("content"):
            metadata["title"] = twitter_title["content"]

    if not metadata["author"]:
        twitter_creator = soup.find("meta", attrs={"name": "twitter:creator"})
        if twitter_creator and twitter_creator.get("content"):
            # Twitter creator is usually @username, clean it up
            creator = twitter_creator["content"].strip()
            metadata["author"] = creator.lstrip("@")

    # Try standard meta tags
    if not metadata["author"]:
        author_meta = soup.find("meta", attrs={"name": "author"})
        if author_meta and author_meta.get("content"):
            metadata["author"] = author_meta["content"]

    if not metadata["publishedDate"]:
        date_meta = soup.find("meta", attrs={"name": "publishedDate"}) or \
                    soup.find("meta", attrs={"name": "date"}) or \
                    soup.find("meta", attrs={"property": "dc:date"})
        if date_meta and date_meta.get("content"):
            metadata["publishedDate"] = _parse_date(date_meta["content"])

    # Fallback to <title> tag
    if not metadata["title"]:
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            metadata["title"] = title_tag.string.strip()

    # Special handling for common sites
    metadata = _apply_site_specific_parsing(soup, url, metadata)

    return metadata


def _parse_date(date_string: str) -> str | None:
    """
    Parse various date formats into YYYY-MM-DD.

    Args:
        date_string: Date string in various formats

    Returns:
        Normalized date string (YYYY-MM-DD) or original if parsing fails
    """
    # Common formats to try
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 with timezone
        "%Y-%m-%dT%H:%M:%S",     # ISO 8601 without timezone
        "%Y-%m-%d",              # Simple YYYY-MM-DD
        "%B %d, %Y",             # January 15, 2024
        "%b %d, %Y",             # Jan 15, 2024
        "%d %B %Y",              # 15 January 2024
        "%m/%d/%Y",              # 01/15/2024
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_string.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # If all parsing fails, return first 10 chars (might be YYYY-MM-DD anyway)
    return date_string[:10] if len(date_string) >= 10 else None


def _apply_site_specific_parsing(
    soup: BeautifulSoup,
    url: str,
    metadata: dict[str, str | None]
) -> dict[str, str | None]:
    """
    Apply site-specific parsing rules for better metadata extraction.

    Args:
        soup: BeautifulSoup object
        url: Original URL
        metadata: Current metadata dictionary

    Returns:
        Updated metadata dictionary
    """
    # Medium articles
    if "medium.com" in url or "towardsdatascience.com" in url:
        if not metadata["author"]:
            author_link = soup.find("a", {"rel": "author"})
            if author_link:
                metadata["author"] = author_link.get_text(strip=True)

    # Dev.to articles
    if "dev.to" in url:
        if not metadata["author"]:
            author_meta = soup.find("meta", {"name": "author"})
            if author_meta:
                metadata["author"] = author_meta.get("content")

    # Substack
    if "substack.com" in url:
        if not metadata["author"]:
            author_elem = soup.find("a", {"class": "frontend-pencraft-Text-module__decoration-hover-underline--BEYAn"})
            if author_elem:
                metadata["author"] = author_elem.get_text(strip=True)

    # ArXiv papers
    if "arxiv.org" in url:
        if not metadata["author"]:
            author_meta = soup.find("meta", {"name": "citation_author"})
            if author_meta:
                metadata["author"] = author_meta.get("content")

        if not metadata["publishedDate"]:
            date_meta = soup.find("meta", {"name": "citation_date"})
            if date_meta:
                metadata["publishedDate"] = date_meta.get("content")

    return metadata


async def fetch_metadata_safe(url: str) -> dict[str, str | None]:
    """
    Safely fetch metadata with fallback to basic info on error.

    Args:
        url: URL to fetch metadata from

    Returns:
        Metadata dictionary (never raises, returns minimal info on error)
    """
    try:
        return await fetch_metadata(url)
    except Exception:
        # On any error, return minimal metadata
        return {
            "title": url,  # Use URL as fallback title
            "author": None,
            "publishedDate": None,
        }
