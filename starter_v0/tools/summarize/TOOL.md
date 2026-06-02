---
name: summarize
track: core
kind: local_formatter
provider: none
requires_env: []
inputs: [text, max_bullets, language]
outputs: [bullets, bullet_count, word_count]
side_effect: false
---

# summarize

Extracts the key sentences from a long text and returns them as a bullet-point list.

Use when the user wants to summarize content already fetched from a URL or a paper,
without making an additional API call.

## Inputs

- `text` (str, required): the text to summarize
- `max_bullets` (int, default=5): maximum number of bullet points to return
- `language` (str, enum: vi/en, default="vi"): output language prefix style

## Outputs

- `bullets`: list of extracted summary sentences
- `bullet_count`: actual number of bullets returned
- `word_count`: word count of the input text

## Notes

- Pure local extraction — no API key required
- Splits on sentence-ending punctuation, filters fragments under 20 chars
- Prioritizes sentences from the opening third of the text (topic sentences), then fills remaining slots with the longest sentences from the rest
- Re-orders selected sentences by original position to preserve reading flow
