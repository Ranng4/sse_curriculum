"""Content filter service — sensitive word filtering for posts and comments.

AI-generated: automatic moderation per 指导.md §5.1.
"""

from __future__ import annotations

import re

# Sensitive word list (configurable; for demo purposes)
_SENSITIVE_WORDS: list[tuple[str, str]] = [
    # (pattern, category)
    (r"荐股|推.*票|带.*单", "荐股行为"),
    (r"涨停|跌停|拉升|砸盘", "操纵市场"),
    (r"加.*群|加.*微信|加.*QQ", "引流"),
    (r"赌博|博彩|赌场", "赌博"),
    (r"色情|黄色|成人", "色情"),
    (r"fake.*id|假.*证", "虚假证件"),
    (r"内幕|内部消息|庄家", "内幕交易"),
    (r"保证.*收益|稳赚|包赚", "虚假承诺"),
    (r"杠杆.*配资|场外配资", "非法配资"),
    (r"代客.*理财|代.*操盘", "违规代操"),
]

# Whitelist: legitimate financial terms that match patterns but are OK
_WHITELIST = {"涨停板分析", "跌停板分析", "技术拉升", "内幕消息辟谣"}


class ContentFilterResult:
    def __init__(self, passed: bool, reason: str | None = None, category: str | None = None):
        self.passed = passed
        self.reason = reason
        self.category = category


class ContentFilter:
    """Check content against sensitive word patterns."""

    def check(self, text: str) -> ContentFilterResult:
        if not text or not text.strip():
            return ContentFilterResult(passed=True)

        text_lower = text.lower()

        for pattern, category in _SENSITIVE_WORDS:
            match = re.search(pattern, text_lower)
            if match:
                matched_text = match.group(0)
                # Check whitelist
                if any(wl in text for wl in _WHITELIST):
                    continue
                return ContentFilterResult(
                    passed=False,
                    reason=f'内容包含违规信息（匹配词: "{matched_text}"）',
                    category=category,
                )

        return ContentFilterResult(passed=True)

    def get_violation_message(self, result: ContentFilterResult) -> str:
        if result.passed:
            return ""
        return f"[{result.category}] {result.reason}"


# Singleton
content_filter = ContentFilter()
