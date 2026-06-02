from __future__ import annotations

import re

_POSITIVE = {
    # English
    "good", "great", "excellent", "amazing", "awesome", "fantastic", "wonderful",
    "brilliant", "outstanding", "superb", "love", "best", "positive", "success",
    "win", "winning", "growth", "improve", "improved", "breakthrough", "innovative",
    "exciting", "excited", "happy", "hope", "promising", "strong", "leading",
    # Vietnamese
    "tốt", "tuyệt", "xuất sắc", "tuyệt vời", "hay", "tích cực", "thành công",
    "phát triển", "cải thiện", "đột phá", "hứa hẹn", "mạnh", "vui", "hạnh phúc",
    "yêu", "thích", "tiến bộ", "hiệu quả", "nhanh", "chính xác",
}

_NEGATIVE = {
    # English
    "bad", "terrible", "awful", "horrible", "worst", "fail", "failure", "error",
    "crash", "broken", "dangerous", "risk", "threat", "problem", "issue", "concern",
    "disappointing", "disappointed", "wrong", "harmful", "toxic", "fraud", "scam",
    "loss", "decline", "drop", "falling", "fear", "worry", "crisis", "disaster",
    # Vietnamese
    "tệ", "xấu", "thất bại", "lỗi", "nguy hiểm", "rủi ro", "vấn đề", "lo ngại",
    "sụp đổ", "giảm", "mất", "khủng hoảng", "thảm họa", "sai", "độc hại",
    "gian lận", "lừa đảo", "lo lắng", "sợ", "hại",
}


def _score_text(text: str) -> float:
    """Return a score in [-1, 1] for a single text string."""
    words = set(re.findall(r"\b\w+\b", text.lower()))
    pos = len(words & _POSITIVE)
    neg = len(words & _NEGATIVE)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total


def analyze_sentiment(
    text: str = "",
    items: list[dict] | None = None,
) -> dict:
    """Classify sentiment of a text or list of social/web items."""
    texts: list[str] = []

    if text and text.strip():
        texts.append(text.strip())

    for item in (items or []):
        content = item.get("summary") or item.get("title") or ""
        if content:
            texts.append(content)

    if not texts:
        return {
            "tool": "sentiment",
            "label": "neutral",
            "score": 0.0,
            "breakdown": {"positive": 0, "negative": 0, "neutral": 0},
            "item_count": 0,
        }

    scores = [_score_text(t) for t in texts]
    avg = sum(scores) / len(scores)

    breakdown = {
        "positive": sum(1 for s in scores if s > 0),
        "negative": sum(1 for s in scores if s < 0),
        "neutral": sum(1 for s in scores if s == 0),
    }

    if avg > 0.05:
        label = "positive"
    elif avg < -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "tool": "sentiment",
        "label": label,
        "score": round(avg, 3),
        "breakdown": breakdown,
        "item_count": len(texts),
    }
