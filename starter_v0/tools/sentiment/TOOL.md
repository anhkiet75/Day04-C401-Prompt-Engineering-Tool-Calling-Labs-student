---
name: sentiment
track: core
kind: local_formatter
provider: none
requires_env: []
inputs: [text, items]
outputs: [label, score, breakdown, item_count]
side_effect: false
---

# sentiment

Analyzes the sentiment of a text or a list of social media posts and classifies
each as positive, negative, or neutral using a keyword-based heuristic.

Use after `timeline` or `social_search` to gauge the overall tone of posts
about a topic or from an account.

## Inputs

- `text` (str, optional): a single block of text to analyze
- `items` (list of dicts, optional): list of items with a `summary` or `title` field
  (compatible with the output format of `timeline`, `social_search`, and `lookup`)

At least one of `text` or `items` must be provided.

## Outputs

- `label`: overall sentiment — `"positive"`, `"negative"`, or `"neutral"`
- `score`: float in [-1, 1] — positive means overall positive tone
- `breakdown`: dict with counts `{"positive": N, "negative": N, "neutral": N}`
- `item_count`: number of texts analyzed

## Notes

- Pure local heuristic — no API key required
- Uses Vietnamese + English keyword lists covering common sentiment words
- Scores each sentence/item independently, then averages
