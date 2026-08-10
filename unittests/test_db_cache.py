"""
Tests for the opt-in test database cache.

The invalidation tests are the regression tests for the defect that motivated PR #321: an earlier
version of the cache keyed entries on the input XML alone, so a change to the code that builds a
database left the key untouched and the suite asserted against a database built by the previous
version of the code. These tests fail if anyone narrows the key back down.

Everything here is fast and needs no submodule: the databases are ordinary files with made-up
contents, since the cache does not care what is inside them.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pytest

from ._db_cache import CachePaths, cached_db, fingerprint, is_enabled

_ENV_VAR = "FUNDAMEND_TEST_DB_CACHE"


@pytest.fixture()
def paths(tmp_path: Path) -> CachePaths:
    """A complete set of cache paths inside tmp_path, so no test touches the real cache."""
    repo_root = tmp_path / "repo"
    source_root = repo_root / "src" / "fundamend"
    unittests_root = repo_root / "unittests"
    source_root.mkdir(parents=True)
    unittests_root.mkdir(parents=True)
    (source_root / "ahbview.py").write_text("def build(): ...\n", encoding="utf-8")
    (source_root / "materialize_ahb_view.sql").write_text("select 1;\n", encoding="utf-8")
    (unittests_root / "conftest.py").write_text("# fixtures\n", encoding="utf-8")
    lock_path = repo_root / "uv.lock"
    lock_path.write_text("ahbicht==1.0.0\n", encoding="utf-8")
    return CachePaths(
        repo_root=repo_root,
        source_root=source_root,
        lock_path=lock_path,
        unittests_root=unittests_root,
        cache_dir=tmp_path / "cache",
    )


def _make_input(paths: CachePaths, name: str, content: str = "<AHB/>") -> Path:
    path = paths.repo_root / "xml-migs-and-ahbs" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _counting_builder(tmp_path: Path, calls: list[int], content: str = "payload") -> object:
    """Return a builder that records every invocation and writes a real (tiny) SQLite file."""

    def build() -> Path:
        calls.append(1)
        database_path = tmp_path / f"built-{len(calls)}.sqlite"
        with sqlite3.connect(database_path) as connection:
            connection.execute("CREATE TABLE t (v TEXT)")
            connection.execute("INSERT INTO t VALUES (?)", (content,))
        return database_path

    return build


def _read_back(database_path: Path) -> list[str]:
    with sqlite3.connect(database_path) as connection:
        return [row[0] for row in connection.execute("SELECT v FROM t")]


# ---------------------------------------------------------------------------------------------
# enabling
# ---------------------------------------------------------------------------------------------


def test_disabled_by_default_builds_every_time(
    paths: CachePaths, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(_ENV_VAR, raising=False)
    calls: list[int] = []
    builder = _counting_builder(tmp_path, calls)

    first = cached_db("some-key", builder, paths=paths)  # type: ignore[arg-type]
    second = cached_db("some-key", builder, paths=paths)  # type: ignore[arg-type]

    assert len(calls) == 2, "with the cache disabled every call must build"
    assert _read_back(first) == ["payload"]
    assert _read_back(second) == ["payload"]
    assert not paths.cache_dir.exists(), "a disabled cache must not create anything on disk"


@pytest.mark.parametrize("value", ["0", "false", "no", "", "  "])
def test_non_enabling_values_keep_the_cache_off(
    value: str, paths: CachePaths, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(_ENV_VAR, value)
    calls: list[int] = []

    cached_db("some-key", _counting_builder(tmp_path, calls), paths=paths)  # type: ignore[arg-type]
    cached_db("some-key", _counting_builder(tmp_path, calls), paths=paths)  # type: ignore[arg-type]

    assert not is_enabled()
    assert len(calls) == 2
    assert not paths.cache_dir.exists()


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "Yes"])
def test_enabling_values_switch_the_cache_on(value: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_ENV_VAR, value)
    assert is_enabled()


def test_enabled_builds_once_and_serves_copies(
    paths: CachePaths, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(_ENV_VAR, "1")
    calls: list[int] = []
    builder = _counting_builder(tmp_path, calls)

    first = cached_db("some-key", builder, paths=paths)  # type: ignore[arg-type]
    second = cached_db("some-key", builder, paths=paths)  # type: ignore[arg-type]

    assert len(calls) == 1, "the second request must be served from the cache"
    assert _read_back(first) == _read_back(second) == ["payload"]
    assert first != second, "every caller gets its own copy"


def test_different_keys_do_not_share_an_entry(
    paths: CachePaths, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(_ENV_VAR, "1")
    calls: list[int] = []

    cached_db("key-a", _counting_builder(tmp_path, calls, "a"), paths=paths)  # type: ignore[arg-type]
    second = cached_db("key-b", _counting_builder(tmp_path, calls, "b"), paths=paths)  # type: ignore[arg-type]

    assert len(calls) == 2
    assert _read_back(second) == ["b"]


def test_unusable_cache_directory_falls_back_to_building(
    paths: CachePaths, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(_ENV_VAR, "1")
    # A *file* where the cache directory should go: mkdir fails on every platform, unlike a
    # read-only directory, which does not reliably block writes on Windows.
    blocked = tmp_path / "blocked"
    blocked.write_text("not a directory", encoding="utf-8")
    unusable = CachePaths(
        repo_root=paths.repo_root,
        source_root=paths.source_root,
        lock_path=paths.lock_path,
        unittests_root=paths.unittests_root,
        cache_dir=blocked,
    )
    calls: list[int] = []

    with pytest.warns(UserWarning, match="cache unusable"):
        built = cached_db("some-key", _counting_builder(tmp_path, calls), paths=unusable)  # type: ignore[arg-type]

    assert len(calls) == 1
    assert _read_back(built) == ["payload"], "a broken cache must never break the run"


# ---------------------------------------------------------------------------------------------
# the fingerprint: what must and must not change the key
# ---------------------------------------------------------------------------------------------


def test_fingerprint_is_stable_for_identical_inputs(paths: CachePaths) -> None:
    files = [_make_input(paths, "MSCONS_AHB.xml")]
    assert fingerprint("recipe", files, paths=paths) == fingerprint("recipe", files, paths=paths)


def test_fingerprint_ignores_input_order(paths: CachePaths) -> None:
    one = _make_input(paths, "one.xml", "<one/>")
    two = _make_input(paths, "two.xml", "<two/>")
    assert fingerprint("recipe", [one, two], paths=paths) == fingerprint("recipe", [two, one], paths=paths)


def test_recipe_change_invalidates(paths: CachePaths) -> None:
    files = [_make_input(paths, "MSCONS_AHB.xml")]
    assert fingerprint("ahb_raw_drop0", files, paths=paths) != fingerprint("ahb_raw_drop1", files, paths=paths)


def test_input_content_change_invalidates(paths: CachePaths) -> None:
    file = _make_input(paths, "MSCONS_AHB.xml", "<AHB>old</AHB>")
    before = fingerprint("recipe", [file], paths=paths)
    file.write_text("<AHB>new</AHB>", encoding="utf-8")
    assert fingerprint("recipe", [file], paths=paths) != before


def test_input_validity_dates_change_invalidates(paths: CachePaths) -> None:
    file = _make_input(paths, "MSCONS_AHB.xml")
    early = fingerprint("recipe", [(file, date(2024, 10, 1), None)], paths=paths)
    late = fingerprint("recipe", [(file, date(2025, 6, 6), None)], paths=paths)
    assert early != late


def _fingerprint_of_variant(paths: CachePaths, mutate: object) -> str:
    """Build a second, independent stub tree that differs only as ``mutate`` says, and hash it."""
    variant_root = paths.repo_root.parent / "repo-variant"
    if variant_root.exists():
        raise AssertionError("variant root must be built exactly once per test")
    variant_source = variant_root / "src" / "fundamend"
    variant_unittests = variant_root / "unittests"
    variant_source.mkdir(parents=True)
    variant_unittests.mkdir(parents=True)
    for source, destination in (
        (paths.source_root, variant_source),
        (paths.unittests_root, variant_unittests),
    ):
        for path in source.rglob("*"):
            if path.is_file():
                target = destination / path.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())
    variant_lock = variant_root / "uv.lock"
    variant_lock.write_bytes(paths.lock_path.read_bytes())
    variant = CachePaths(
        repo_root=variant_root,
        source_root=variant_source,
        lock_path=variant_lock,
        unittests_root=variant_unittests,
        cache_dir=variant_root / "cache",
    )
    mutate(variant)  # type: ignore[operator]
    # the same input file, at the same repo-relative path, so only the code differs
    input_file = variant_root / "xml-migs-and-ahbs" / "MSCONS_AHB.xml"
    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text("<AHB/>", encoding="utf-8")
    return fingerprint("recipe", [input_file], paths=variant)


def test_python_source_change_invalidates(paths: CachePaths) -> None:
    baseline = _make_input(paths, "MSCONS_AHB.xml")
    before = fingerprint("recipe", [baseline], paths=paths)
    after = _fingerprint_of_variant(
        paths, lambda variant: (variant.source_root / "ahbview.py").write_text("def build(): return 1\n")
    )
    assert after != before, "a change to a builder module must invalidate the cache"


def test_sql_source_change_invalidates(paths: CachePaths) -> None:
    baseline = _make_input(paths, "MSCONS_AHB.xml")
    before = fingerprint("recipe", [baseline], paths=paths)
    after = _fingerprint_of_variant(
        paths,
        lambda variant: (variant.source_root / "materialize_ahb_view.sql").write_text("select 2;\n"),
    )
    assert after != before, (
        "the .sql view definitions are read at runtime and executed into the database, "
        "so editing one must invalidate the cache"
    )


def test_new_source_file_invalidates(paths: CachePaths) -> None:
    baseline = _make_input(paths, "MSCONS_AHB.xml")
    before = fingerprint("recipe", [baseline], paths=paths)
    after = _fingerprint_of_variant(
        paths, lambda variant: (variant.source_root / "new_view.sql").write_text("select 3;\n")
    )
    assert after != before


def test_lock_file_change_invalidates(paths: CachePaths) -> None:
    baseline = _make_input(paths, "MSCONS_AHB.xml")
    before = fingerprint("recipe", [baseline], paths=paths)
    after = _fingerprint_of_variant(paths, lambda variant: variant.lock_path.write_text("ahbicht==2.0.0\n"))
    assert after != before, "a dependency bump changes what ahb_expressions contains"


def test_unittests_change_invalidates(paths: CachePaths) -> None:
    baseline = _make_input(paths, "MSCONS_AHB.xml")
    before = fingerprint("recipe", [baseline], paths=paths)
    after = _fingerprint_of_variant(
        paths, lambda variant: (variant.unittests_root / "conftest.py").write_text("# different fixtures\n")
    )
    assert after != before, "the fixtures decide which views a built database receives"


def test_ignored_directories_do_not_invalidate(paths: CachePaths) -> None:
    baseline = _make_input(paths, "MSCONS_AHB.xml")
    before = fingerprint("recipe", [baseline], paths=paths)

    def add_ignored_files(variant: CachePaths) -> None:
        snapshots = variant.unittests_root / "__snapshots__"
        snapshots.mkdir()
        (snapshots / "test_something.ambr").write_text("# serializer version: 1\n", encoding="utf-8")
        examples = variant.unittests_root / "example_files"
        examples.mkdir()
        (examples / "UTILTS_AHB.xml").write_text("<AHB/>\n", encoding="utf-8")
        (variant.unittests_root / "conftest.pyc").write_bytes(b"\x00compiled")

    after = _fingerprint_of_variant(paths, add_ignored_files)
    assert after == before, "snapshots, example files and bytecode do not change how a database is built"
