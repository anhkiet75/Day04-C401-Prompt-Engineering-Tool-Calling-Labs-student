from __future__ import annotations

import re


def summarize_text(
    text: str = "",
    max_bullets: int = 5,
    language: str = "vi",
) -> dict:
    """Extract top sentences from text as bullet points — no API needed."""
    if not text or not text.strip():
        return {"tool": "summarize", "bullets": [], "bullet_count": 0, "word_count": 0}

    word_count = len(text.split())

    # Split on sentence-ending punctuation, keeping the delimiter
    raw = re.split(r"(?<=[.!?。])\s+", text.strip())

    # Filter out very short fragments and clean whitespace
    sentences = [s.strip().replace("\n", " ") for s in raw if len(s.strip()) >= 20]

    # Score: prefer longer sentences near the start (extractive heuristic)
    scored = [(i, len(s), s) for i, s in enumerate(sentences)]
    # Take first third as high-priority, rest lower priority
    cutoff = max(1, len(scored) // 3)
    priority = scored[:cutoff] + sorted(scored[cutoff:], key=lambda x: -x[1])
    top = priority[:max_bullets]
    # Re-sort by original position to preserve reading order
    top.sort(key=lambda x: x[0])

    prefix = "•" if language == "vi" else "-"
    bullets = [f"{prefix} {s}" for _, _, s in top]

    return {
        "tool": "summarize",
        "bullets": bullets,
        "bullet_count": len(bullets),
        "word_count": word_count,
    }
