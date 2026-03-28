"""Core markdown editor functionality."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Document:
    """Represents a Markdown document."""

    title: str = ""
    content: str = ""
    _history: list[str] = field(default_factory=list, repr=False)

    def update(self, new_content: str) -> None:
        """Replace the document content, saving the previous version to history."""
        self._history.append(self.content)
        self.content = new_content

    def undo(self) -> bool:
        """Revert to the previous content. Returns True if undo was performed."""
        if not self._history:
            return False
        self.content = self._history.pop()
        return True

    @property
    def word_count(self) -> int:
        """Return the number of words in the document."""
        return len(self.content.split()) if self.content.strip() else 0

    @property
    def line_count(self) -> int:
        """Return the number of lines in the document."""
        if not self.content:
            return 0
        return self.content.count("\n") + 1


def extract_headings(markdown: str) -> list[tuple[int, str]]:
    """Extract headings from markdown text.

    Returns a list of (level, title) tuples.
    """
    headings: list[tuple[int, str]] = []
    for line in markdown.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append((level, title))
    return headings


def markdown_to_plaintext(markdown: str) -> str:
    """Strip basic markdown formatting and return plain text."""
    text = markdown
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(\*{1,3}|_{1,3})(.+?)\1", r"\2", text)
    text = re.sub(r"`{1,3}[^`]*`{1,3}", "", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[>\-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    return text.strip()


def find_links(markdown: str) -> list[tuple[str, str]]:
    """Extract links from markdown text.

    Returns a list of (text, url) tuples.
    """
    return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", markdown)
