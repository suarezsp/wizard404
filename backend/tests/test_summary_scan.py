"""
Tests for summary_scan: get_entropy_message (directory order/disorder messages).
"""

import pytest

from wizard404_core.models import DirectoryStats
from wizard404_core.summary_scan import get_entropy_message


def test_entropy_empty_stats():
    s = DirectoryStats()
    msg = get_entropy_message(s)
    assert "Empty" in msg or "empty" in msg.lower()


def test_entropy_no_extensions():
    s = DirectoryStats(total_files=0, total_size=0, by_extension={})
    msg = get_entropy_message(s)
    assert "Empty" in msg or "empty" in msg.lower() or "No recognized" in msg


def test_entropy_clean_few_extensions():
    s = DirectoryStats(
        total_files=100,
        total_size=1000,
        by_extension={".txt": 50, ".pdf": 50},
        by_type={"text/plain": 50, "application/pdf": 50},
    )
    msg = get_entropy_message(s)
    assert "clean" in msg.lower() or "order" in msg.lower()


def test_entropy_high_many_extensions():
    s = DirectoryStats(
        total_files=50,
        total_size=5000,
        by_extension={".a": 1, ".b": 1, ".c": 1, ".d": 1, ".e": 1, ".f": 1, ".g": 1, ".h": 1, ".i": 1, ".j": 1, ".k": 1, ".l": 1, ".m": 1, ".n": 1},
        by_type={},
    )
    msg = get_entropy_message(s)
    assert "entropy" in msg.lower() or "disorder" in msg.lower() or "organiz" in msg.lower()
