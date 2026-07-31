"""
On-disk cache for the expensive SQLite databases the tests build from the AHB/MIG XML corpus.

The XML source lives in the pinned ``xml-migs-and-ahbs`` submodule and the database builders in
:mod:`fundamend.sqlmodels` are deterministic, so a given ``(input files, flags)`` combination always
produces an equivalent database. Building one is slow (XML parsing plus ``ahbicht`` expression
evaluation) and the suite triggers dozens of such builds, so we cache the finished ``.sqlite`` file
on disk keyed by a content hash of its inputs.

The cache is shared across pytest-xdist workers through the filesystem (guarded by a file lock so a
cold cache is built exactly once) and can additionally be persisted across CI runs via an
``actions/cache`` step keyed on the submodule commit -- see ``.github/workflows``.
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from collections.abc import Callable, Iterable
from datetime import date
from pathlib import Path

from filelock import FileLock

# Bump when the *way* a cached database is built changes (new views, different columns, ...), so
# that stale cache entries from an older builder are ignored instead of silently reused.
_CACHE_VERSION = "v1"

_CACHE_DIR = Path(__file__).parent.parent / ".pytest_db_cache"

# Type of the file lists accepted by fundamend's DB builders.
_AhbFile = Path | tuple[Path, date, date | None] | tuple[Path, None, None]


def fingerprint(recipe: str, files: Iterable[_AhbFile]) -> str:
    """
    Return a short, stable hash identifying a database build.

    ``recipe`` names the build variant (e.g. which views get added on top); ``files`` is the exact
    input set. Both the file *paths* and their *content* are hashed, so the fingerprint is correct
    even if the submodule is checked out at a different commit or locally modified. The file order
    does not matter -- inputs are sorted first.
    """
    hasher = hashlib.sha256()
    hasher.update(_CACHE_VERSION.encode())
    hasher.update(recipe.encode())
    normalized: list[tuple[str, str, str]] = []
    for item in files:
        if isinstance(item, Path):
            path, von, bis = item, "", ""
        else:
            path = item[0]
            von = "" if item[1] is None else item[1].isoformat()
            bis = "" if item[2] is None else item[2].isoformat()
        normalized.append((str(path), von, bis))
    for path_str, von, bis in sorted(normalized):
        hasher.update(path_str.encode())
        hasher.update(von.encode())
        hasher.update(bis.encode())
        hasher.update(Path(path_str).read_bytes())
    return hasher.hexdigest()[:32]


def cached_db(key: str, builder: Callable[[], Path]) -> Path:
    """
    Return a path to a ready-to-use SQLite database for ``key``, building it once and caching it.

    On a cache miss ``builder`` is invoked (exactly once across all xdist workers, thanks to the
    file lock) and its result is published into the cache. Every caller receives its *own* fresh
    copy of the cached file, so concurrent sessions never contend on a single database file.
    """
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = _CACHE_DIR / f"{key}.sqlite"
    with FileLock(f"{cached}.lock"):
        if not cached.exists():
            built = builder()
            tmp = cached.with_suffix(".sqlite.building")
            shutil.copyfile(built, tmp)
            tmp.replace(cached)  # atomic publish so readers never see a half-written file
    consumer_copy = Path(tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False).name)
    shutil.copyfile(cached, consumer_copy)
    return consumer_copy
