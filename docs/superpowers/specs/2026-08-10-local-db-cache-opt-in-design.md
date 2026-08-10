# Opt-in local test database cache

**Date:** 2026-08-10
**Status:** Approved (design), pending implementation
**Depends on:** PR #321 (`refactor(tests): remove the SQLite database cache, keep xdist`)

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

`unittests/_db_cache.py` reads the environment variable `FUNDAMEND_TEST_DB_CACHE`. If it is unset or
empty, `cached_db(key, builder)` calls `builder()` and returns its result: no cache directory is
created, no lock is taken, no file is copied. The cache is not merely "off" — the code path does not
execute.

CI workflows are not changed and set nothing. A cached run therefore cannot produce a green CI
result. Enabling is a deliberate local act:

```bash
export FUNDAMEND_TEST_DB_CACHE=1
uv run pytest
```

### The cache key

`fingerprint(recipe, files)` hashes, in this order:

1. the recipe name (which build variant: raw tables only, with diff views, ...)
2. for each input file, sorted: its path, `gueltig_von`, `gueltig_bis` and its contents
3. the **code fingerprint** (below)

The code fingerprint is a hash over everything that determines what a built database contains:

- every `src/fundamend/**/*.py` file — builders, readers, view definitions
- `uv.lock` — pins `ahbicht` and `lark`, which fill `ahb_expressions`
- `unittests/conftest.py` — `_build_ahb_db_with_diff_view` decides which views a fixture's database
  receives

It is computed once per process and memoized; the cost is one hash over a few dozen small files per
test run.

`_CACHE_VERSION` is deliberately **not** reintroduced. The code fingerprint subsumes it: any change
to how a database is built already changes the key. There is no manual bump to remember and no
invariant a contributor can violate by forgetting something.

The known limit of this approach, accepted explicitly: the fingerprint covers the declared
environment, not the realised one. A different Python patch version or a differently-built native
wheel with an identical `uv.lock` produces the same key. This is acceptable because the cache is
local-only and a developer's environment is stable between runs; it would not be acceptable for a
cache shared across machines, which is why this design does not have one.

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
no two sessions share a database file.

The cache must never be able to break a test run. If the cache directory cannot be created or
written, or a cached file cannot be read, `cached_db` emits a warning and falls back to calling
`builder()`. Entries are never evicted automatically; reclaiming space means deleting the directory,
which is safe at any time.

## Tests

New tests in `unittests/test_db_cache.py`. All are fast and require no submodule.

| Test | Asserts |
|------|---------|
| disabled by default | with the env var unset, `builder` runs on every call and no cache directory is created |
| enabled, cold then warm | with the env var set, two requests for the same key call `builder` once and return equal database contents |
| fingerprint is stable | identical inputs produce an identical fingerprint |
| source change invalidates | modifying a file under a stubbed source root changes the fingerprint |
| lock file change invalidates | modifying the stubbed `uv.lock` changes the fingerprint |
| conftest change invalidates | modifying the stubbed `conftest.py` changes the fingerprint |
| input change invalidates | changing an input file's contents, path or validity dates changes the fingerprint |
| unwritable cache falls back | with the cache directory made unusable, the call still returns a working database |

The invalidation tests are the regression tests for the defect that motivated PR #321: they fail if
someone later narrows the key back to the input data.

To keep them fast and hermetic, the paths that feed the code fingerprint are injectable — the
production default points at the real `src/fundamend`, `uv.lock` and `unittests/conftest.py`, and the
tests pass temporary directories instead.

## Documentation

The README's testing section gains a short passage (target: ~8 lines) covering how to enable the
cache, that everything relevant invalidates automatically, and that CI never uses it. PR #321
replaced the old cache chapter with a note saying the databases are deliberately not cached; that
note is amended here to "not cached in CI, opt-in locally". Shipping the code without amending it
would leave the repository contradicting itself.

If the passage cannot be kept short, the design is wrong and should be reconsidered rather than
documented at length.

## Delivery

A stacked pull request: branch `local-db-cache-opt-in` off `remove-test-db-cache`, with the PR based
on `remove-test-db-cache` so reviewers see only the incremental diff.

Because the repository is squash-merge-only, `a952c6e` will not become an ancestor of `main` when
#321 merges. After that merge the stacked branch needs
`git rebase --onto main remove-test-db-cache local-db-cache-opt-in` and a force-push with lease;
GitHub's automatic retarget alone would show a doubled diff.
