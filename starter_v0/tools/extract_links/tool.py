from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse


def extract_links(
    html: str = "",
    base_url: str = "",
    max_links: int = 20,
) -> dict:
    """Extract all hyperlinks from raw HTML content."""
    if not html or not html.strip():
        return {"tool": "extract_links", "links": [], "link_count": 0}

    # Match href="..." or href='...'
    pattern = re.compile(r'href=["\']([^"\'#\s][^"\']*)["\']', re.IGNORECASE)
    # Match anchor text: capture href value and inner text separately
    text_pattern = re.compile(
        r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )

    raw_hrefs = pattern.findall(html)
    anchor_pairs = {
        m.group(1): re.sub(r'<[^>]+>', '', m.group(2)).strip()
        for m in text_pattern.finditer(html)
    }

    seen: set[str] = set()
    links: list[dict] = []

    for href in raw_hrefs:
        # Skip non-http links
        if href.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue

        # Resolve relative URLs
        if base_url and not href.startswith(("http://", "https://")):
            href = urljoin(base_url, href)

        # Only keep http/https links
        parsed = urlparse(href)
        if parsed.scheme not in ("http", "https"):
            continue

        url = href.rstrip("/")
        if url in seen:
            continue
        seen.add(url)

        links.append({
            "url": url,
            "text": anchor_pairs.get(href, "")[:120],
        })

        if len(links) >= max_links:
            break

    return {
        "tool": "extract_links",
        "links": links,
        "link_count": len(links),
    }
