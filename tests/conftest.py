"""Shared test fixtures."""

import pytest

from chrysaline.editor import Document


@pytest.fixture
def empty_doc():
    """An empty document."""
    return Document()


@pytest.fixture
def sample_doc():
    """A document pre-filled with sample markdown."""
    md = (
        "# Welcome\n"
        "\n"
        "This is a **sample** document.\n"
        "\n"
        "## Section One\n"
        "\n"
        "Some text with a [link](https://example.com) here.\n"
        "\n"
        "### Sub-section\n"
        "\n"
        "- item one\n"
        "- item two\n"
    )
    return Document(title="Sample", content=md)
