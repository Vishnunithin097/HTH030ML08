"""
Text and numerical preprocessing routines.
"""
import re
from typing import List


def clean_text(text: str) -> str:
    """Basic text cleanup for content-based matching."""
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.lower().split())


def extract_keywords(tags: List[str]) -> str:
    """Combines list of tags into a normalized search query."""
    return " ".join(clean_text(tag) for tag in tags if tag)
