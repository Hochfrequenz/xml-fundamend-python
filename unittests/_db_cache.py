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

# Type of the file lists accepted by fundamend's DB builders (AHB and MIG alike).
_XmlInputFile = Path | tuple[Path, date, date | None] | tuple[Path, None, None]


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
        if not root.is_dir():
            # A root that does not exist must *change* the key, never silently shrink it. Without
            # this, renaming the package directory (or a typo in DEFAULT_PATHS) would reduce the
            # fingerprint to "everything else" and quietly stop invalidating on builder changes --
            # the PR #321 defect, reached through a path mistake instead of a narrow glob.
            hasher.update(b"\0MISSING\0")
            hasher.update(str(root).encode())
            continue
        for path in _relevant_files(root, only_python=only_python):
            contents = path.read_bytes()
            # Frame each entry with its length so that name and contents cannot run together:
            # "a.py" + b"bX" must not hash like "a.pyb" + b"X".
            hasher.update(f"\0{path.relative_to(root).as_posix()}\0{len(contents)}\0".encode())
            hasher.update(contents)
    hasher.update(b"\0lock\0")
    if paths.lock_path.is_file():
        lock_contents = paths.lock_path.read_bytes()
        hasher.update(f"\0{len(lock_contents)}\0".encode())
        hasher.update(lock_contents)
    else:
        hasher.update(b"\0MISSING\0")
        hasher.update(str(paths.lock_path).encode())
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


def fingerprint(recipe: str, files: Iterable[_XmlInputFile], *, paths: CachePaths = DEFAULT_PATHS) -> str:
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
        contents = path.read_bytes()
        # Length-framed for the same reason as in _code_fingerprint: von/bis are variable length
        # (empty or a 10-character ISO date), so unframed concatenation would be ambiguous.
        hasher.update(f"\0{relative_path}\0{von}\0{bis}\0{len(contents)}\0".encode())
        hasher.update(contents)
    return hasher.hexdigest()[:32]


def _warn_unusable(error: OSError) -> None:
    warnings.warn(f"test database cache unusable ({error}); building directly", stacklevel=3)


def _publish(built: Path, cached: Path) -> bool:
    """Copy ``built`` into the cache atomically; return whether that worked."""
    try:
        being_written = cached.with_suffix(".sqlite.building")
        shutil.copyfile(built, being_written)
        being_written.replace(cached)  # atomic publish; readers never see a partial file
        return True
    except OSError as error:
        _warn_unusable(error)
        return False


def _private_copy(cached: Path) -> Path | None:
    """Return the caller its own copy of a cached database, or ``None`` if that is not possible."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as handle:
            consumer_copy = Path(handle.name)
        shutil.copyfile(cached, consumer_copy)
        return consumer_copy
    except OSError as error:
        _warn_unusable(error)
        return None


def cached_db(key: str, builder: Callable[[], Path], *, paths: CachePaths = DEFAULT_PATHS) -> Path:
    """
    Return a path to a ready-to-use SQLite database for ``key``, building it at most once.

    Without ``FUNDAMEND_TEST_DB_CACHE`` set this is a thin pass-through to ``builder``. With it set,
    a cache miss invokes ``builder`` exactly once across all pytest-xdist workers (the file lock) and
    publishes the result atomically, so an interrupted run can never leave a truncated entry behind
    for later runs to reuse. Every caller receives its own copy, so concurrent sessions never contend
    on one database file.

    The cache never gets a vote on whether the suite can run: any filesystem problem degrades to a
    direct build with a warning. Failures raised by ``builder`` itself are *not* caught -- they are
    bugs in the code under test, and dressing them up as cache problems would send whoever is
    debugging them in the wrong direction.
    """
    if not is_enabled():
        return builder()
    cached = paths.cache_dir / f"{key}.sqlite"
    try:
        paths.cache_dir.mkdir(parents=True, exist_ok=True)
        file_lock = FileLock(f"{cached}.lock")
        file_lock.acquire()
    except OSError as error:
        _warn_unusable(error)
        return builder()
    try:
        if not cached.exists():
            built = builder()  # outside every OSError handler: builder failures must propagate
            _publish(built, cached)  # warns on failure; either way the freshly built file is good
            # Return the build itself rather than copying it back out of the cache: it is already a
            # private throwaway file, so copying would double the I/O on the slowest path and leave
            # the original behind in the temp directory for nothing.
            return built
        private_copy = _private_copy(cached)
    finally:
        file_lock.release()
    return private_copy if private_copy is not None else builder()
