---
name: extract_links
track: core
kind: local_formatter
provider: none
requires_env: []
inputs: [html, base_url, max_links]
outputs: [links, link_count]
side_effect: false
---

# extract_links

Extracts all hyperlinks from raw HTML content returned by the `fetch` tool.

Use after `fetch` when the user wants to explore links inside an article or page —
e.g. "find all links in this page", "what other articles does this link to?".

## Inputs

- `html` (str, required): raw HTML string (the `content` field from `fetch` output)
- `base_url` (str, optional): base URL to resolve relative links (e.g. `https://example.com`)
- `max_links` (int, default=20): maximum number of links to return

## Outputs

- `links`: list of dicts with `url` and `text` fields
- `link_count`: total number of unique links found (before max_links cap)

## Notes

- Pure local extraction using regex — no API key required
- Deduplicates URLs, skips javascript: and mailto: links
- Relative URLs are resolved if `base_url` is provided
