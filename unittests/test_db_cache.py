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

import shutil
import sqlite3
from collections.abc import Callable
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from ._db_cache import DEFAULT_PATHS, CachePaths, cached_db, fingerprint, is_enabled

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


def _counting_builder(tmp_path: Path, calls: list[int], content: str = "payload") -> Callable[[], Path]:
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

    first = cached_db("some-key", builder, paths=paths)
    second = cached_db("some-key", builder, paths=paths)

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

    cached_db("some-key", _counting_builder(tmp_path, calls), paths=paths)
    cached_db("some-key", _counting_builder(tmp_path, calls), paths=paths)

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

    first = cached_db("some-key", builder, paths=paths)
    second = cached_db("some-key", builder, paths=paths)

    assert len(calls) == 1, "the second request must be served from the cache"
    assert _read_back(first) == _read_back(second) == ["payload"]
    assert first != second, "every caller gets its own copy"


def test_different_keys_do_not_share_an_entry(
    paths: CachePaths, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(_ENV_VAR, "1")
    calls: list[int] = []

    cached_db("key-a", _counting_builder(tmp_path, calls, "a"), paths=paths)
    second = cached_db("key-b", _counting_builder(tmp_path, calls, "b"), paths=paths)

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
        built = cached_db("some-key", _counting_builder(tmp_path, calls), paths=unusable)

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


def test_input_path_change_invalidates(paths: CachePaths) -> None:
    """Two files with identical contents at different paths must not share a cache entry."""
    here = _make_input(paths, "FV2410/MSCONS_AHB.xml", "<AHB/>")
    there = _make_input(paths, "FV2504/MSCONS_AHB.xml", "<AHB/>")
    assert here.read_bytes() == there.read_bytes(), "the point of this test is identical contents"
    assert fingerprint("recipe", [here], paths=paths) != fingerprint("recipe", [there], paths=paths)


def test_fingerprint_survives_moving_the_checkout(paths: CachePaths, tmp_path: Path) -> None:
    """
    Paths enter the key repo-relative, so relocating a checkout must not discard the cache.

    The pre-removal implementation hashed ``str(path)``, i.e. an absolute, OS-flavoured path; this
    test fails if that ever comes back.
    """
    original_input = _make_input(paths, "FV2410/MSCONS_AHB.xml")
    before = fingerprint("recipe", [original_input], paths=paths)

    moved_root = tmp_path / "somewhere" / "else" / "repo"
    moved_root.parent.mkdir(parents=True)
    shutil.copytree(paths.repo_root, moved_root)
    moved = replace(
        paths,
        repo_root=moved_root,
        source_root=moved_root / "src" / "fundamend",
        lock_path=moved_root / "uv.lock",
        unittests_root=moved_root / "unittests",
        cache_dir=moved_root / "cache",
    )

    after = fingerprint("recipe", [moved_root / "xml-migs-and-ahbs" / "FV2410" / "MSCONS_AHB.xml"], paths=moved)
    assert after == before, "an identical tree at a different absolute location must hash the same"


def test_input_validity_dates_change_invalidates(paths: CachePaths) -> None:
    file = _make_input(paths, "MSCONS_AHB.xml")
    early = fingerprint("recipe", [(file, date(2024, 10, 1), None)], paths=paths)
    late = fingerprint("recipe", [(file, date(2025, 6, 6), None)], paths=paths)
    assert early != late


def _fingerprint_of_variant(paths: CachePaths, mutate: Callable[[CachePaths], object]) -> str:
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
    mutate(variant)
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
        # These must land under the *source* root, which is walked without the only_python filter.
        # Putting them under the unittests root would prove nothing: everything here lacks a .py
        # suffix, so the only_python filter would drop them before the exclusion rules were consulted
        # and the test would pass even with _IGNORED_DIRECTORIES emptied.
        bytecode = variant.source_root / "__pycache__"
        bytecode.mkdir()
        (bytecode / "ahbview.cpython-312.pyc").write_bytes(b"\x00compiled")
        nested = variant.source_root / "sqlmodels" / "__pycache__"
        nested.mkdir(parents=True)
        (nested / "internals.cpython-312.pyc").write_bytes(b"\x00compiled")
        (variant.source_root / "ahbview.pyc").write_bytes(b"\x00loose bytecode")

    after = _fingerprint_of_variant(paths, add_ignored_files)
    assert after == before, (
        "bytecode does not change how a database is built; if it did, ordinary recompilation "
        "would invalidate every cache entry and the cache would silently stop caching"
    )


def test_snapshots_and_example_files_do_not_invalidate(paths: CachePaths) -> None:
    baseline = _make_input(paths, "MSCONS_AHB.xml")
    before = fingerprint("recipe", [baseline], paths=paths)

    def add_test_data(variant: CachePaths) -> None:
        snapshots = variant.unittests_root / "__snapshots__"
        snapshots.mkdir()
        # a .py inside an ignored directory: only _IGNORED_DIRECTORIES can keep this out
        (snapshots / "helper.py").write_text("# not a builder\n", encoding="utf-8")
        (snapshots / "test_something.ambr").write_text("# serializer version: 1\n", encoding="utf-8")
        examples = variant.unittests_root / "example_files"
        examples.mkdir()
        (examples / "conftest.py").write_text("# not a builder either\n", encoding="utf-8")

    after = _fingerprint_of_variant(paths, add_test_data)
    assert after == before, "snapshots and example files do not influence how a database is built"


def test_missing_source_root_changes_the_key(paths: CachePaths) -> None:
    """A vanished root must invalidate, not silently shrink the fingerprint to 'everything else'."""
    baseline = _make_input(paths, "MSCONS_AHB.xml")
    with_root = fingerprint("recipe", [baseline], paths=paths)
    without_root = fingerprint("recipe", [baseline], paths=replace(paths, source_root=paths.repo_root / "src" / "gone"))
    other_missing_root = fingerprint(
        "recipe", [baseline], paths=replace(paths, source_root=paths.repo_root / "src" / "also-gone")
    )

    assert without_root != with_root, "losing the source root must change the key"
    assert without_root != other_missing_root, (
        "two different missing roots must not collapse to the same key -- otherwise a renamed "
        "package directory would leave every pre-rename entry looking valid forever"
    )


def test_missing_lock_file_changes_the_key(paths: CachePaths) -> None:
    baseline = _make_input(paths, "MSCONS_AHB.xml")
    with_lock = fingerprint("recipe", [baseline], paths=paths)
    without_lock = fingerprint("recipe", [baseline], paths=replace(paths, lock_path=paths.repo_root / "gone.lock"))
    assert with_lock != without_lock


def test_default_paths_describe_the_real_repository() -> None:
    """
    Guards the failure mode that no other test can see: DEFAULT_PATHS pointing at nothing.

    If the package or test directory is ever moved and these constants are not updated, the code
    fingerprint silently stops covering the moved tree. That is PR #321's defect via a path mistake.
    """
    assert DEFAULT_PATHS.source_root.is_dir(), f"{DEFAULT_PATHS.source_root} does not exist"
    assert DEFAULT_PATHS.unittests_root.is_dir(), f"{DEFAULT_PATHS.unittests_root} does not exist"
    assert DEFAULT_PATHS.lock_path.is_file(), f"{DEFAULT_PATHS.lock_path} does not exist"
    # pyproject.toml rather than .git: the suite must also pass from a source archive (a GitHub
    # "Download ZIP" checkout has no .git), where these paths are still perfectly correct.
    assert (DEFAULT_PATHS.repo_root / "pyproject.toml").is_file(), "repo_root should be the repository root"
    # the .sql view definitions are the reason the source root is hashed in full rather than by *.py
    assert list(DEFAULT_PATHS.source_root.rglob("*.sql")), "expected .sql view definitions under src/fundamend"
