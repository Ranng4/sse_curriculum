"""Mention parser — extract @username references from post/comment content.

AI-generated: @mention support per 指导.md §2.2.
"""

from __future__ import annotations

import re

# Matches @username patterns (Chinese/English/alphanumeric, 2-32 chars)
_MENTION_RE = re.compile(r"@([\w一-鿿㐀-䶿]{2,32})")


def extract_mentions(text: str) -> list[str]:
    """Return list of unique @mentioned usernames in text."""
    matches = _MENTION_RE.findall(text)
    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            result.append(m)
    return result


def highlight_mentions(text: str) -> str:
    """Wrap @mentions in markdown-style links for frontend rendering."""
    return _MENTION_RE.sub(r'[@\1](/profile/\1)', text)
