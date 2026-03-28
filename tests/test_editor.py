"""Tests for chrysaline.editor module."""

import pytest

from chrysaline.editor import (
    Document,
    extract_headings,
    find_links,
    markdown_to_plaintext,
)


class TestDocument:
    """Tests for the Document dataclass."""

    def test_default_values(self, empty_doc):
        assert empty_doc.title == ""
        assert empty_doc.content == ""
        assert empty_doc.word_count == 0
        assert empty_doc.line_count == 0

    def test_word_count(self, sample_doc):
        assert sample_doc.word_count > 0

    def test_line_count(self, sample_doc):
        assert sample_doc.line_count == 13

    def test_update_changes_content(self, empty_doc):
        empty_doc.update("hello world")
        assert empty_doc.content == "hello world"

    def test_update_preserves_history(self, empty_doc):
        empty_doc.update("v1")
        empty_doc.update("v2")
        assert empty_doc.content == "v2"

    def test_undo_restores_previous(self, empty_doc):
        empty_doc.update("v1")
        empty_doc.update("v2")
        result = empty_doc.undo()
        assert result is True
        assert empty_doc.content == "v1"

    def test_undo_on_empty_history(self, empty_doc):
        assert empty_doc.undo() is False

    def test_multiple_undos(self, empty_doc):
        empty_doc.update("v1")
        empty_doc.update("v2")
        empty_doc.update("v3")
        empty_doc.undo()
        empty_doc.undo()
        assert empty_doc.content == "v1"

    def test_undo_all(self, empty_doc):
        empty_doc.update("v1")
        empty_doc.undo()
        assert empty_doc.content == ""
        assert empty_doc.undo() is False

    def test_word_count_whitespace_only(self):
        doc = Document(content="   \n\n  ")
        assert doc.word_count == 0

    def test_line_count_single_line(self):
        doc = Document(content="hello")
        assert doc.line_count == 1


class TestExtractHeadings:
    """Tests for the extract_headings function."""

    def test_empty_input(self):
        assert extract_headings("") == []

    def test_single_heading(self):
        result = extract_headings("# Title")
        assert result == [(1, "Title")]

    def test_multiple_levels(self, sample_doc):
        result = extract_headings(sample_doc.content)
        assert result == [
            (1, "Welcome"),
            (2, "Section One"),
            (3, "Sub-section"),
        ]

    def test_no_headings(self):
        assert extract_headings("Just plain text\nwith lines") == []

    def test_heading_without_space(self):
        assert extract_headings("#NoSpace") == []

    @pytest.mark.parametrize(
        "level",
        [1, 2, 3, 4, 5, 6],
    )
    def test_all_heading_levels(self, level):
        md = f"{'#' * level} Heading {level}"
        result = extract_headings(md)
        assert result == [(level, f"Heading {level}")]


class TestMarkdownToPlaintext:
    """Tests for the markdown_to_plaintext function."""

    def test_strips_bold(self):
        assert markdown_to_plaintext("**bold**") == "bold"

    def test_strips_italic(self):
        assert markdown_to_plaintext("*italic*") == "italic"

    def test_strips_links(self):
        assert markdown_to_plaintext("[text](http://url)") == "text"

    def test_strips_images(self):
        result = markdown_to_plaintext("![alt](http://img.png)")
        assert result == "alt"

    def test_strips_headings(self):
        result = markdown_to_plaintext("## Heading")
        assert result == "Heading"

    def test_empty_input(self):
        assert markdown_to_plaintext("") == ""

    def test_plain_text_unchanged(self):
        assert markdown_to_plaintext("no formatting here") == "no formatting here"


class TestFindLinks:
    """Tests for the find_links function."""

    def test_no_links(self):
        assert find_links("no links") == []

    def test_single_link(self):
        result = find_links("[click](https://example.com)")
        assert result == [("click", "https://example.com")]

    def test_multiple_links(self):
        md = "[a](http://a.com) and [b](http://b.com)"
        result = find_links(md)
        assert result == [("a", "http://a.com"), ("b", "http://b.com")]

    def test_finds_link_in_sample(self, sample_doc):
        result = find_links(sample_doc.content)
        assert ("link", "https://example.com") in result
