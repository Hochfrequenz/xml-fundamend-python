# Opt-in local test database cache

**Date:** 2026-08-10
**Status:** Design reviewed (three rounds); awaiting sign-off before implementation
**Builds on:** PR #321 (`refactor(tests): remove the SQLite database cache, keep xdist`), merged as
`bab5b4f`

## Problem

Building the SQLite test databases from the `xml-migs-and-ahbs` submodule dominates the test
runtime. PR #317 solved this with an on-disk cache, but keyed each entry only on
`_CACHE_VERSION`, the recipe name and the input XML (paths, validity dates, contents). The key did
not cover the `fundamend` code that builds the database, nor the versions of the dependencies
involved. A change to a reader, a view definition or the expression evaluation therefore left the
key unchanged, and the suite asserted against a database built by the previous version of the code.
PR #321 removed that cache.

Local development still wants the speed. CI still wants to be pedantic: every run must exercise the
code under test, with no reuse of anything built by earlier code.

## Goals

- Fast, repeated local test runs for developers who ask for them.
- CI always builds every database from scratch, with no way to opt in by accident.
- No manual invalidation step. If a cached database could differ from a fresh build, the cache must
  miss on its own.
- The mechanism must be explainable in a few lines of README.

## Non-goals

- Sharing caches between machines, or persisting them across CI runs.
- Caching anything other than the built SQLite databases.
- Reducing the cold runtime of the suite. That is worth doing, but it is separate work (the
  duplicated FV2410+FV2504 build across the two diff-view modules is the obvious first candidate).

## Design

### Enabling

`unittests/_db_cache.py` reads the environment variable `FUNDAMEND_TEST_DB_CACHE`. The cache is
enabled only when its value is one of `1`, `true`, `yes` (case-insensitive); anything else,
including unset, empty, `0` and `false`, disables it. The variable is **evaluated on each
`cached_db()` call, not once at import**, so tests can flip it with `monkeypatch.setenv`. When disabled, `cached_db(key, builder)` calls
`builder()` and returns its result: no cache directory is created, no lock is taken, no file is
copied. The cache is not merely "off" — the code path does not execute.

CI workflows are not changed and set nothing. A cached run therefore cannot produce a green CI
result. Enabling is a deliberate local act:

```bash
export FUNDAMEND_TEST_DB_CACHE=1
uv run pytest
```

### The cache key

`fingerprint(recipe, files)` hashes, in this order:

1. the recipe name. This must continue to encode the builder flags as it did before removal —
   `cached_ahb_db` used `f"ahb_raw_drop{int(drop_raw_tables)}"` — because `drop_raw_tables` changes
   the resulting schema for otherwise identical inputs
2. for each input file, sorted: its path, `gueltig_von`, `gueltig_bis` and its contents. The path is
   normalised to a **repo-relative POSIX path** (`PurePath.relative_to(repo_root).as_posix()`) before
   hashing. The pre-removal implementation hashed `str(path)`, i.e. an absolute, OS-flavoured path,
   which makes the fingerprint depend on where the checkout happens to live and on the path
   separator. Normalising means moving or re-cloning a checkout does not throw away the whole cache,
   and two developers on different platforms compute the same key for the same file. The relative
   path is still part of the identity, so two distinct files with identical contents remain
   distinguishable. An input outside the repository root (not something the suite does today) falls
   back to the absolute POSIX path.
3. the **code fingerprint** (below)

The code fingerprint is a hash over everything that determines what a built database contains:

- **every file under `src/fundamend/`**, not just `*.py`. The package ships six `.sql` files
  (`materialize_ahb_view.sql`, `materialize_mig_view.sql`, `create_ahbtabellen_view.sql`,
  `create_ahb_formatversion_diff_view.sql`, `create_ahb_pruefi_diff_view.sql`,
  `create_mig_diff_view.sql`) which are read at runtime and executed straight into the database.
  Editing a view's SQL is the most likely way to change what a database contains, so a `*.py`-only
  glob would reproduce exactly the defect this design exists to prevent. `__pycache__` and `*.pyc`
  are excluded; everything else under the package directory is hashed by relative path and content.
- `uv.lock` — pins `ahbicht` and `lark`, which fill `ahb_expressions`. It also pins `ruff`, `mypy`
  and `pytest`, so a lint-tool bump invalidates every entry too. That is wasteful but never wrong,
  and it is the price of a rule that needs no exceptions list.
- **every `unittests/**/*.py`** (recursive; `__pycache__`, `__snapshots__` and `example_files`
  excluded), not only `conftest.py`.
  `_build_ahb_db_with_diff_view` lives in `conftest.py` today, but hashing the directory removes a
  silent failure mode: the day builder logic moves into a `unittests/_helpers.py` — or a
  `unittests/helpers/build.py` — a `conftest.py`-only or top-level-only rule would stop covering it
  and no test would fail. Recursing keeps the rule as airtight as the `src/fundamend/` one. The cost
  is a chattier cache — editing any test file invalidates local entries — which is cheap for a
  local-only cache.

The result is memoized **keyed on the paths object** (source root, lock path, unittests root, cache
directory), which is therefore a frozen dataclass so it can serve as a dict key. It is not memoized
once per process. A plain process-level memo would break the invalidation tests, which compute
fingerprints from several different stubbed roots within a single pytest process. In a normal run
the object is constant, so the hash is still computed only once: one pass over a few dozen small
files.

`_CACHE_VERSION` is deliberately **not** reintroduced. The code fingerprint subsumes it: any change
to how a database is built already changes the key. There is no manual bump to remember and no
invariant a contributor can violate by forgetting something.

The known limit of this approach, accepted explicitly: the fingerprint covers the declared
environment, not the realised one. A different Python patch version or a differently-built native
wheel with an identical `uv.lock` produces the same key. This is acceptable because the cache is
local-only and a developer's environment is stable between runs; it would not be acceptable for a
cache shared across machines, which is why this design does not have one.

A cached database is **equivalent to** a fresh build, not byte-identical with one: primary keys come
from `uuid.uuid4()` in the SQLModel tables and from `hex(randomblob(16))` in
`materialize_ahb_view.sql` and `materialize_mig_view.sql`. "Deterministic builders" holds only up to
those ids. No test may assert on freshly generated id values, and none does today — the existing
snapshot tests strip the guid columns before comparing.

### Scope of caching

All existing call sites route through the cache again: the `cached_ahb_db` / `cached_mig_db` helpers
in `unittests/conftest.py`, their 13 call sites across `test_ahb_formatversion_diff_view.py`,
`test_mig_views.py`, `test_sqlmodels_anwendungshandbuch.py` and
`test_sqlmodels_expressions_view.py`, plus the two module-scoped fixtures
(`session_fv2410_fv2504_with_diff_view`, `session_fv2510_fv2604_mscons_with_diff_view`).

Uniform coverage is chosen over a curated subset because the rule stays one sentence: every
submodule-scale build goes through the cache, and the cache is a no-op unless enabled. A partial
list would need maintaining and would invite the question "why is this one not cached?".

Cheap example-file tests and builder-error-path tests continue to build directly, as they do today.

### Storage and failure handling

Cache entries live in `.pytest_db_cache/` (gitignored again), one `<key>.sqlite` per entry. A
`FileLock` guards cold population so concurrent pytest-xdist workers build an entry exactly once;
`filelock` returns as a `tests` dependency. Each caller receives its own copy of the cached file, so
no two sessions share a database file. Those per-caller copies are `NamedTemporaryFile(delete=False)`
as before. Cleanup of them is **best-effort at most**: nothing deletes them, and on Windows in
particular the system temp directory is not reliably swept, so they accumulate until the OS or the
developer clears it. That is the pre-existing behaviour and this design does not change it, but it
should not be described as the OS reaping them. Each copy is roughly the size of one built database,
so a developer running the suite repeatedly with the cache on will want to clear their temp directory
occasionally. Adding lifecycle management is possible but out of scope here.

**The cache directory is part of the injectable paths object**, as a fourth field alongside the
source root, lock path and unittests root, defaulting to `<repo>/.pytest_db_cache`. Four of the
tests below need to control it — "no directory is created", the disabling values, the cold/warm
sequence, and the fallback case. Without injection those tests would read and write the developer's
real cache: the cold/warm test would pollute it, and "no directory is created" would fail on any
machine where an earlier opt-in run had left the directory behind.

For the same reason `cached_db()` takes the paths object as an optional keyword argument even though
it receives an already-computed key and never fingerprints anything: it needs the cache directory
from it. Callers that do not pass one get the production default.

Publication into the cache stays **atomic**, as it was before removal: the built database is copied
to a temporary name inside the cache directory and then `Path.replace()`d into place. A reader must
never be able to observe a half-written entry. This matters more than the lock does — the lock only
serialises concurrent xdist workers within one run, whereas an interrupted run (Ctrl-C, OOM kill)
would otherwise leave a truncated `.sqlite` behind that every later run happily reuses.

The cache must never be able to break a test run. If the cache directory cannot be created or
written, or a cached file cannot be read, `cached_db` emits a warning and falls back to calling
`builder()`. Entries are never evicted automatically; reclaiming space means deleting the directory,
which is safe at any time.

## Tests

New tests in `unittests/test_db_cache.py`. All are fast and require no submodule.

| Test | Asserts |
|------|---------|
| disabled by default | with the env var unset, `builder` runs on every call and no cache directory is created |
| `0`/`false` also disable | the documented disabling values behave like unset |
| enabled, cold then warm | with the env var set, two requests for the same key call `builder` once and return equal database contents |
| fingerprint is stable | identical inputs produce an identical fingerprint |
| `.py` change invalidates | two stubbed source roots differing only in a `.py` file produce different fingerprints |
| **`.sql` change invalidates** | two stubbed source roots differing only in a `.sql` file produce different fingerprints |
| lock file change invalidates | two stubbed `uv.lock` files differing in content produce different fingerprints |
| unittests change invalidates | two stubbed unittests roots differing only in one file produce different fingerprints |
| input change invalidates | changing an input file's contents, path or validity dates changes the fingerprint |
| recipe change invalidates | the same inputs under a different recipe (e.g. `drop_raw_tables`) produce a different fingerprint |
| unusable cache falls back | when the cache directory cannot be created, the call still returns a working database |

The invalidation tests are the regression tests for the defect that motivated PR #321: they fail if
someone later narrows the key back to the input data.

To keep them fast and hermetic, every path the module touches is injectable as one explicit
parameter object — source root, lock path, unittests root, cache directory — with a module-level
production default pointing at the real `src/fundamend`, `uv.lock`, `unittests/` and
`.pytest_db_cache/`. Tests pass temporary directories instead. `fingerprint()` and `cached_db()`
take it as an optional keyword argument, so the 13 call sites and both fixtures are unaffected.

The "unusable cache" test must be cross-platform: read-only directories do not reliably block writes
on Windows, which is a primary development platform here. The test therefore points the cache
directory at a path where a *file* already exists, so directory creation fails on every OS.

## Documentation

The README's testing section gains a short passage (target: ~8 lines) covering how to enable the
cache, that everything relevant invalidates automatically, and that CI never uses it. PR #321
replaced the old cache chapter with a note saying the databases are deliberately not cached; that
note is amended here to "not cached in CI, opt-in locally". Shipping the code without amending it
would leave the repository contradicting itself.

If the passage cannot be kept short, the design is wrong and should be reconsidered rather than
documented at length.

CI runs `codespell --ignore-words=domain-specific-terms.txt` over `README.md`. PR #321 removed four
German words from that list along with the old cache chapter; the new passage may need some of them
back. Check before pushing rather than spending a CI round-trip on it.

## Delivery

This work lives on branch `local-db-cache-opt-in`, opened as PR #323 with this document as its only
content so the design can be argued with before it is built. Implementation commits follow on the
same branch once the design is signed off.

The branch was originally stacked on `remove-test-db-cache`. That branch has since been squash-merged
as `bab5b4f`, and because the repository is squash-merge-only the pre-merge commits never became
ancestors of `main`; the branch was therefore rebased with
`git rebase --onto origin/main remove-test-db-cache local-db-cache-opt-in` followed by
`git push --force-with-lease origin local-db-cache-opt-in`. It now shows a clean single-file diff against `main`. This is recorded because the same
manoeuvre will be needed for any future branch stacked on an unmerged PR in this repository —
GitHub's automatic retarget on its own produces a doubled diff.
