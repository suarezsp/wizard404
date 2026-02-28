"""Tests del módulo de resúmenes automáticos."""
import pytest
from wizard404_core.summary import summarize_text


def test_summarize_empty():
    assert summarize_text("") == ""
    assert summarize_text(None) == ""
    assert summarize_text("   ") == ""


def test_summarize_short_text_unchanged():
    short = "Hello world."
    assert summarize_text(short, max_chars=300) == short


def test_summarize_truncates_at_max_chars():
    long_text = "A" * 400
    result = summarize_text(long_text, max_chars=100)
    assert len(result) <= 103
    assert result.endswith("...")


def test_summarize_cuts_at_sentence():
    text = "First sentence. Second sentence. Third sentence."
    result = summarize_text(text, max_chars=25)
    assert "First sentence." in result
    assert result.strip().endswith(".") or result.endswith("...")
