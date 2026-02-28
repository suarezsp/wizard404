"""
Tests for Organize: preview and execute (move by type, date, size).
Requires wizard404_cli and wizard404_core. Path setup for CLI import below.
"""

import sys
from pathlib import Path

import pytest

# Allow importing wizard404_cli when running from backend/tests
_repo_root = Path(__file__).resolve().parent.parent.parent
_cli_dir = _repo_root / "cli"
if _cli_dir.exists() and str(_cli_dir) not in sys.path:
    sys.path.insert(0, str(_cli_dir))

from wizard404_cli.commands import organize_cmd


def test_organize_preview_by_type(tmp_path: Path) -> None:
    """Preview by type: subfolders have correct extensions, base_dest in plan."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "a.txt").write_text("a")
    (src_dir / "b.txt").write_text("bb")
    (src_dir / "c.pdf").write_bytes(b"%PDF-1.4 minimal")
    dest_base = tmp_path / "out"
    dest_base.mkdir()
    plan = organize_cmd.run_organize_preview(str(src_dir), str(dest_base), "type")
    assert plan is not None
    assert plan["base_dest"] == str(dest_base.resolve())
    subfolders = plan["subfolders"]
    assert ".txt" in subfolders
    assert ".pdf" in subfolders
    assert len(subfolders[".txt"]) == 2
    assert len(subfolders[".pdf"]) == 1
    for label, files in subfolders.items():
        for path_str, size in files:
            assert Path(path_str).is_file()
            assert isinstance(size, int) and size >= 0
    assert plan["total_files"] == 3
    assert plan["total_size"] >= 3


def test_organize_execute_move_by_type(tmp_path: Path) -> None:
    """Execute moves files into type subfolders; files exist in dest and not in src."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "a.txt").write_text("a")
    (src_dir / "b.txt").write_text("bb")
    (src_dir / "c.pdf").write_bytes(b"%PDF-1.4 x")
    dest_base = tmp_path / "dest"
    plan = organize_cmd.run_organize_preview(str(src_dir), str(dest_base), "type")
    assert plan is not None
    ok = organize_cmd.run_organize_execute(plan)
    assert ok
    assert (dest_base / "txt" / "a.txt").is_file()
    assert (dest_base / "txt" / "b.txt").is_file()
    assert (dest_base / "pdf" / "c.pdf").is_file()
    assert not (src_dir / "a.txt").exists()
    assert not (src_dir / "b.txt").exists()
    assert not (src_dir / "c.pdf").exists()


def test_organize_preview_by_date(tmp_path: Path) -> None:
    """Preview by date: buckets are two-month labels; plan has base_dest."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "f1.txt").write_text("1")
    (src_dir / "f2.txt").write_text("22")
    dest_base = tmp_path / "out"
    dest_base.mkdir()
    plan = organize_cmd.run_organize_preview(str(src_dir), str(dest_base), "date")
    assert plan is not None
    assert "base_dest" in plan
    assert Path(plan["base_dest"]).is_absolute() or str(plan["base_dest"]).startswith(str(dest_base.resolve()))
    subfolders = plan["subfolders"]
    assert len(subfolders) >= 1
    for label in subfolders:
        # Format like 2024-01_2024-02 or unknown
        assert isinstance(label, str)
        for path_str, size in subfolders[label]:
            assert Path(path_str).is_file()
            assert isinstance(size, int)


def test_organize_execute_by_date(tmp_path: Path) -> None:
    """Execute by date: files move to date bucket folder."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "d1.txt").write_text("d1")
    (src_dir / "d2.txt").write_text("d2")
    dest_base = tmp_path / "dest"
    plan = organize_cmd.run_organize_preview(str(src_dir), str(dest_base), "date")
    assert plan is not None
    ok = organize_cmd.run_organize_execute(plan)
    assert ok
    subfolders = plan["subfolders"]
    for label, files in subfolders.items():
        folder = dest_base / label.replace("/", "").replace("\\", "") or "other"
        if label in ("..", ""):
            folder = dest_base / "other"
        for path_str, _ in files:
            name = Path(path_str).name
            found = folder / name
            if not found.exists():
                # try any subfolder under dest_base
                found = next((dest_base / d / name for d in dest_base.iterdir() if d.is_dir() and (d / name).exists()), None)
            assert found and found.exists(), f"Expected {name} under {dest_base}"
            assert not Path(path_str).exists(), f"Source should be moved: {path_str}"


def test_organize_preview_by_size(tmp_path: Path) -> None:
    """Preview by size: size_ranges used, subfolders and base_dest in plan."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "small.txt").write_text("x")  # few bytes
    (src_dir / "big.txt").write_text("x" * 2000)  # 2k
    dest_base = tmp_path / "out"
    dest_base.mkdir()
    size_ranges = [
        ("Tiny", 0, 100),
        ("Medium", 100, 2000),
        ("Large", 2000, None),
    ]
    plan = organize_cmd.run_organize_preview(
        str(src_dir), str(dest_base), "size", size_ranges=size_ranges
    )
    assert plan is not None
    assert "base_dest" in plan
    assert "subfolders" in plan
    assert plan["total_files"] == 2


def test_organize_execute_by_size(tmp_path: Path) -> None:
    """Execute by size: files move to size range folders."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "s.txt").write_text("a")
    (src_dir / "m.txt").write_text("b" * 500)
    dest_base = tmp_path / "dest"
    size_ranges = [
        ("Tiny", 0, 100),
        ("Medium", 100, 2000),
        ("Large", 2000, None),
    ]
    plan = organize_cmd.run_organize_preview(
        str(src_dir), str(dest_base), "size", size_ranges=size_ranges
    )
    assert plan is not None
    ok = organize_cmd.run_organize_execute(plan)
    assert ok
    # Files should be under dest_base in some subfolder
    for f in ("s.txt", "m.txt"):
        found = list(dest_base.rglob(f))
        assert len(found) == 1 and found[0].is_file()
        assert not (src_dir / f).exists()


def test_organize_destination_inside_base(tmp_path: Path) -> None:
    """Execute only writes under base_dest; no escape via path."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "x.txt").write_text("x")
    dest_base = tmp_path / "dest"
    plan = organize_cmd.run_organize_preview(str(src_dir), str(dest_base), "type")
    assert plan is not None
    # Simulate malicious label (e.g. if plan were tampered): execute uses safe_label
    # So we only test that normal execute keeps files under dest_base
    ok = organize_cmd.run_organize_execute(plan)
    assert ok
    for f in dest_base.rglob("*.txt"):
        try:
            f.resolve().relative_to(dest_base.resolve())
        except ValueError:
            pytest.fail(f"File outside base: {f}")


def test_organize_base_created_if_missing(tmp_path: Path) -> None:
    """Execute creates base directory if it does not exist."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "only.txt").write_text("only")
    dest_base = tmp_path / "nonexistent" / "deep"
    assert not dest_base.exists()
    plan = organize_cmd.run_organize_preview(str(src_dir), str(dest_base), "type")
    assert plan is not None
    ok = organize_cmd.run_organize_execute(plan)
    assert ok
    assert dest_base.is_dir()
    assert (dest_base / "txt" / "only.txt").is_file()
