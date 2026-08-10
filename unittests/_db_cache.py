"""
Opt-in, local-only cache for the SQLite databases the tests build from the AHB/MIG XML corpus.

Building one of these databases is slow (XML parsing plus ``ahbicht`` expression evaluation) and the
suite triggers dozens of builds, so developers can cache the finished ``.sqlite`` files on disk.

Two properties make this safe, and both are load-bearing:

1. **It is off unless you ask for it.** Set ``FUNDAMEND_TEST_DB_CACHE=1`` to enable it. Without that,
   :func:`cached_db` simply calls the builder -- no directory, no lock, no copy. CI sets nothing, so
   a cached run cannot produce a green CI result.
2. **The key covers the code, not just the data.** :func:`fingerprint` hashes the builder sources
   (every file under ``src/fundamend``, including the ``.sql`` view definitions that are read at
   runtime), ``uv.lock`` and the test sources, on top of the input XML. Any change to how a database
   is built therefore changes the key on its own.

Property 2 is why there is no ``_CACHE_VERSION`` constant to bump by hand. An earlier version of this
module keyed entries on the input XML alone, which meant a change to a reader or a view definition
was served a database built by the *previous* version of the code, and the suite went green without
having seen the change. See PR #321 for the removal and PR #323 for this design.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import warnings
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from filelock import FileLock

_ENV_VAR = "FUNDAMEND_TEST_DB_CACHE"
_ENABLING_VALUES = frozenset({"1", "true", "yes"})

_REPO_ROOT = Path(__file__).parent.parent

# Directories that never influence a built database, so hashing them would only cost time and
# invalidate entries for no reason.
_IGNORED_DIRECTORIES = frozenset({"__pycache__", "__snapshots__", "example_files"})

# Type of the file lists accepted by fundamend's DB builders.
_AhbFile = Path | tuple[Path, date, date | None] | tuple[Path, None, None]


@dataclass(frozen=True)
class CachePaths:
    """
    Every filesystem location this module touches, in one injectable (and hashable) bundle.

    Production code uses :data:`DEFAULT_PATHS`; the tests point these at temporary directories so
    they neither read nor write a developer's real cache.
    """

    repo_root: Path
    source_root: Path
    lock_path: Path
    unittests_root: Path
    cache_dir: Path


DEFAULT_PATHS = CachePaths(
    repo_root=_REPO_ROOT,
    source_root=_REPO_ROOT / "src" / "fundamend",
    lock_path=_REPO_ROOT / "uv.lock",
    unittests_root=_REPO_ROOT / "unittests",
    cache_dir=_REPO_ROOT / ".pytest_db_cache",
)

# Keyed on the paths bundle rather than computed once per process: the invalidation tests compute
# fingerprints from several different stubbed roots inside a single pytest process.
_CODE_FINGERPRINTS: dict[CachePaths, str] = {}


def is_enabled() -> bool:
    """Return whether the cache is switched on. Read on every call so tests can monkeypatch it."""
    return os.environ.get(_ENV_VAR, "").strip().lower() in _ENABLING_VALUES


def _relevant_files(root: Path, only_python: bool) -> Iterator[Path]:
    """Yield the files under ``root`` whose contents can influence a built database, sorted."""
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*")):
        relative_parts = path.relative_to(root).parts
        if any(part in _IGNORED_DIRECTORIES for part in relative_parts):
            continue
        if not path.is_file() or path.suffix == ".pyc":
            continue
        if only_python and path.suffix != ".py":
            continue
        yield path


def _code_fingerprint(paths: CachePaths) -> str:
    """
    Hash everything that determines what a built database contains, except its XML inputs.

    ``src/fundamend`` is hashed in full rather than by ``*.py``: the package ships six ``.sql`` files
    which :func:`fundamend.sqlmodels.internals._execute_bare_sql` reads from disk and executes into
    the database, and editing one of those is the most likely way to change a database's content.
    """
    memoized = _CODE_FINGERPRINTS.get(paths)
    if memoized is not None:
        return memoized
    hasher = hashlib.sha256()
    for label, root, only_python in (
        ("src", paths.source_root, False),
        ("unittests", paths.unittests_root, True),
    ):
        hasher.update(f"\0root:{label}\0".encode())
        for path in _relevant_files(root, only_python=only_python):
            hasher.update(path.relative_to(root).as_posix().encode())
            hasher.update(path.read_bytes())
    hasher.update(b"\0lock\0")
    if paths.lock_path.is_file():
        hasher.update(paths.lock_path.read_bytes())
    fingerprint_of_code = hasher.hexdigest()
    _CODE_FINGERPRINTS[paths] = fingerprint_of_code
    return fingerprint_of_code


def _normalized_path(path: Path, repo_root: Path) -> str:
    """
    Return ``path`` as a repo-relative POSIX string.

    Hashing the absolute path would tie the key to where the checkout happens to live and to the
    platform's path separator, so moving a checkout would silently discard the whole cache. The
    relative path still distinguishes two different files that happen to have identical contents.
    """
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:  # an input from outside the repository; not something the suite does today
        return path.resolve().as_posix()


def fingerprint(recipe: str, files: Iterable[_AhbFile], *, paths: CachePaths = DEFAULT_PATHS) -> str:
    """
    Return a short, stable hash identifying a database build.

    ``recipe`` names the build variant and must encode the builder flags (``drop_raw_tables``
    changes the resulting schema for otherwise identical inputs). ``files`` is the exact input set;
    both the paths and the contents are hashed, so the fingerprint is correct even if the submodule
    is checked out at a different commit or locally modified. The file order does not matter.
    """
    hasher = hashlib.sha256()
    hasher.update(recipe.encode())
    hasher.update(_code_fingerprint(paths).encode())
    normalized: list[tuple[str, str, str, Path]] = []
    for item in files:
        if isinstance(item, Path):
            path, von, bis = item, "", ""
        else:
            path = item[0]
            von = "" if item[1] is None else item[1].isoformat()
            bis = "" if item[2] is None else item[2].isoformat()
        normalized.append((_normalized_path(path, paths.repo_root), von, bis, path))
    for relative_path, von, bis, path in sorted(normalized, key=lambda entry: entry[:3]):
        hasher.update(relative_path.encode())
        hasher.update(von.encode())
        hasher.update(bis.encode())
        hasher.update(path.read_bytes())
    return hasher.hexdigest()[:32]


def cached_db(key: str, builder: Callable[[], Path], *, paths: CachePaths = DEFAULT_PATHS) -> Path:
    """
    Return a path to a ready-to-use SQLite database for ``key``, building it at most once.

    Without ``FUNDAMEND_TEST_DB_CACHE`` set this is a thin pass-through to ``builder``. With it set,
    a cache miss invokes ``builder`` exactly once across all pytest-xdist workers (the file lock) and
    publishes the result atomically, so an interrupted run can never leave a truncated entry behind
    for later runs to reuse. Every caller receives its own copy, so concurrent sessions never contend
    on one database file.

    The cache never gets a vote on whether the suite can run: any filesystem problem degrades to a
    direct build with a warning.
    """
    if not is_enabled():
        return builder()
    try:
        paths.cache_dir.mkdir(parents=True, exist_ok=True)
        cached = paths.cache_dir / f"{key}.sqlite"
        with FileLock(f"{cached}.lock"):
            if not cached.exists():
                built = builder()
                being_written = cached.with_suffix(".sqlite.building")
                shutil.copyfile(built, being_written)
                being_written.replace(cached)  # atomic publish; readers never see a partial file
        consumer_copy = Path(tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False).name)
        shutil.copyfile(cached, consumer_copy)
        return consumer_copy
    except OSError as error:
        warnings.warn(f"test database cache unusable ({error}); building directly", stacklevel=2)
        return builder()
