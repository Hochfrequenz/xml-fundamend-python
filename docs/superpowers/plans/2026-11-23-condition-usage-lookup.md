# Condition usage lookup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** "Where is condition `[931]` used?" answered exactly, incl. use via packages and UB conditions: a table and
view in fundamend's SQLite DB, and the MCP tool `search_bedingung_usage` in ahb-tabellen.

**Architecture:** fundamend parses every distinct AHB expression with ahbicht, resolves package/UB keys through their
definitions in the same AHB, and writes one row per (AHB, expression, key, via) into `ahb_condition_usages`; the view
`v_ahb_condition_usages` joins these rows to the lines of `v_ahbtabellen`. ahb-tabellen (TypeScript) queries the view.

**Tech Stack:** Python, SQLModel/SQLite, ahbicht, efoli, pytest + syrupy (fundamend); TypeScript, Node, zod, MCP SDK,
jest, `@hochfrequenz/efoli` (ahb-tabellen).

**Spec:** `docs/superpowers/specs/2026-11-23-condition-usage-lookup-design.md` (its last section "Decisions after the
builder check" overrides earlier sections).

## Global Constraints

- Resolve direct and indirect use; packages and UB conditions transitively, with a visited set against cycles; plain
  conditions are leaves.
- Table keyed per AHB (`anwendungshandbuch_primary_key`); `format` is the plain format; **no** detailed-format column.
- Direct use is stored as `via = ''` (NOT NULL; part of the unique constraint); the view exposes `NULLIF(via, '')`.
- `condition_key` exactly as `extract_categorized_keys` returns it, without brackets.
- Deterministic output; one parse per distinct expression / definition text.
- Ruling (deviates from the spec's "exported from `fundamend.sqlmodels`"): like `expression_view`, the new module
  imports ahbicht (an optional extra), so it is **not** imported in `fundamend/sqlmodels/__init__.py`; users import
  from `fundamend.sqlmodels.condition_usage`. Exporting it would make ahbicht mandatory for all sqlmodels users.
- fundamend gates: `uv run pytest`, `uv run ruff check --select I .`, `uv run ruff format --check .`,
  `uv run pylint src/fundamend` (check the exact command in `.github/workflows/pythonlint.yml`),
  `uv run mypy --show-error-codes src/fundamend --strict`, same for `unittests`. Coverage stays ≥ 94 %.
  Setup: `uv sync --group dev --extra sqlmodels --extra ahbicht --extra cli`.
- ahb-tabellen gates: `npm test` (jest), `npm run lint`, and the type check / build the repo's CI runs.
- 8 GB RAM machine: never two heavy jobs (DB builds, full test suites) at the same time.
- Conventional commits; commits end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`; commit with
  `git -c user.name=konstantin -c user.email=konstantin.klein@hochfrequenz.de commit ...`. Do not push.

## Review Focus

1. A line whose expression uses the same key directly and via `[UB1]`: two rows, the view shows both, the tool shows
   the line once with both markers (Task 1 test + Task 3 test).
2. A key reachable via two different top-level keys (`[UB1]` and `[2P]`): one row per via (Task 1 test).
3. Input spelling in the tool: `931`, `[931]`, ` [ 931 ] `, `ub1`, `2p` must all match (Task 3 test: strip
   brackets and whitespace, uppercase letters).
4. A detailed format filter (`UTILMDS`) must not break `limit`/total: filter by Prüfidentifikator list in SQL, not
   after the query (Task 3 test).
5. Expressions with surrounding whitespace: matched against `line_ahb_status` exactly like `ahb_expressions` does
   (strip on both sides; Task 2 test).

---

### Task 1 (fundamend): table and resolution

**Files:**
- Create: `src/fundamend/sqlmodels/condition_usage.py`
- Test: `unittests/test_sqlmodels_condition_usage.py`

**Interfaces:**
- Produces:
  - `class KeyType(StrEnum)`: `CONDITION = "condition"`, `PACKAGE = "package"`, `UB_CONDITION = "ub_condition"`.
  - `class AhbConditionUsage(SQLModel, table=True)`, `__tablename__ = "ahb_condition_usages"`: `id: uuid.UUID` (pk,
    uuid4), `anwendungshandbuch_primary_key: uuid.UUID` (FK `anwendungshandbuch.primary_key`),
    `edifact_format_version: EdifactFormatVersion`, `format: EdifactFormat`, `expression: str`,
    `condition_key: str`, `key_type: KeyType`, `via: str` (default `""`). `UniqueConstraint(
    "anwendungshandbuch_primary_key", "expression", "condition_key", "via")`; indexes on
    (`edifact_format_version`, `format`, `condition_key`) and (`anwendungshandbuch_primary_key`, `expression`).
  - Pure helper `resolve_condition_keys(expression: str, definitions: Mapping[str, str]) -> list[tuple[str, KeyType,
    str]]` returning sorted, distinct `(condition_key, key_type, via)`; `definitions` maps package/UB keys of one AHB
    to their definition text. Raises the parser's exception for an unparseable `expression` (the caller logs and
    skips). Definition texts that do not parse (e.g. `--`) or keys without definition contribute no children (log).
    Internally cache parse results per text (`functools.lru_cache` on a module-level wrapper around
    `asyncio.run(extract_categorized_keys(text))`).
  - `create_and_fill_ahb_condition_usage_table(session: Session) -> None`: reads the distinct
    (format_version, format, stripped expression, anwendungshandbuch_primary_key) from the four `*_ahb_status`
    columns of `ahb_hierarchy_materialized` (same columns as `create_and_fill_ahb_expression_table`), loads `Paket`
    and `UbBedingung` per AHB, calls `resolve_condition_keys`, writes rows. Raises `ValueError` with a hint if
    `ahb_hierarchy_materialized` is empty, or if the `paket`/`ubbedingung` tables are missing (built with
    `drop_raw_tables=True`).

- [ ] **Step 1: Write failing tests** for `resolve_condition_keys` (pure, no DB). First check in a scratch call how
  `extract_categorized_keys` spells package and UB keys (`2P` vs `[2P]`, `UB1`) and use that spelling.

```python
def test_direct() -> None:
    assert resolve_condition_keys("Muss [931] U [932]", {}) == [
        ("931", KeyType.CONDITION, ""), ("932", KeyType.CONDITION, "")]

def test_via_ub_and_direct_ub_row() -> None:
    rows = resolve_condition_keys("Muss [UB1]", {"UB1": "([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])"})
    assert ("UB1", KeyType.UB_CONDITION, "") in rows
    assert {k for k, t, v in rows if v == "UB1"} == {"931", "932", "933", "490", "491"}

def test_direct_and_indirect_on_same_line() -> None:
    rows = resolve_condition_keys("Muss [931] U [UB1]", {"UB1": "[931]"})
    assert ("931", KeyType.CONDITION, "") in rows and ("931", KeyType.CONDITION, "UB1") in rows

def test_two_vias() -> None: ...         # "[UB1] U [2P]", both define [25] -> two rows for 25 (via UB1, via 2P)
def test_nested_keeps_outermost_via() -> None: ...  # UB1 -> [3P] -> [25]: rows (3P, package, UB1), (25, condition, UB1)
def test_cycle_terminates() -> None: ... # UB1 -> [2P], 2P -> [UB1]
def test_undefined_key_has_no_children() -> None: ...
def test_dash_definition_has_no_children() -> None: ...  # "1P": "--"
def test_unparseable_expression_raises() -> None: ...
def test_result_is_sorted_and_distinct() -> None: ...
```

  Plus DB tests with `cached_ahb_db(..., drop_raw_tables=False)` on
  `unittests/example_files/UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml` (after `create_ahb_view`-equivalent
  setup as in `test_sqlmodels_expressions_view.py`): the table is filled; some row has `condition_key == "931"` and
  `via == "UB1"`; building twice gives identical rows (ignoring `id`); `drop_raw_tables=True` raises the
  `ValueError`. Find the exact AHB setup steps from the existing expression view test.

- [ ] **Step 2: Run** `uv run pytest unittests/test_sqlmodels_condition_usage.py -v` — expected: FAIL (import error).
- [ ] **Step 3: Implement** per Interfaces.
- [ ] **Step 4: Run** the test file, then the gates — expected: all PASS.
- [ ] **Step 5: Commit** `feat: ahb_condition_usages table (direct and indirect use of conditions)`

### Task 2 (fundamend): view and README

**Files:**
- Create: `src/fundamend/sqlmodels/create_ahb_condition_usage_view.sql`
- Modify: `src/fundamend/sqlmodels/condition_usage.py` (view function + read model)
- Modify: `README.md` (short section next to the existing view docs)
- Test: `unittests/test_sqlmodels_condition_usage.py`, snapshot in `unittests/__snapshots__/`

**Interfaces:**
- Consumes: Task 1's table.
- Produces: `create_ahb_condition_usage_view(session: Session) -> None` creating `v_ahb_condition_usages` (follow
  `create_ahbtabellen_view` / its SQL file pattern, incl. the DROP TABLE/VIEW lines) and a read-only SQLModel
  `AhbConditionUsageLine` for it. Columns: `id` (stable, e.g. the `v_ahbtabellen` id combined with the usage id, or
  whatever the existing views use as primary key), `format_version`, `format`, `pruefidentifikator`, `description`,
  `direction`, `segmentgroup_key`, `segment_code`, `data_element`, `qualifier`, `line_name`, `line_ahb_status`,
  `sort_path`, `anwendungshandbuch_primary_key`, `condition_key`, `key_type`, `via` (`NULLIF(u.via, '')`).
  Join: `u.anwendungshandbuch_primary_key = l.anwendungshandbuch_primary_key AND u.expression =
  TRIM(l.line_ahb_status)` (check how `ahb_expressions` matches stripped expressions and do the same). Requires
  `v_ahbtabellen`; raise a clear error if it is missing.

- [ ] **Step 1: Failing tests:** on the UTILTS example: the view has a line with `condition_key == "931"` and
  `via == "UB1"`, and `via is None` for direct use; a line using a key directly and via UB appears twice in the view
  (once per via); a syrupy snapshot of the view rows for one Prüfidentifikator and `condition_key == "931"`, ordered
  by `sort_path, via` (drop uuid columns like the existing snapshot tests).
- [ ] **Step 2: Run**, expect FAIL. **Step 3: Implement.** **Step 4: Run** test file + gates, expect PASS (also the
  private-submodule test if the submodule is checked out locally; if it is, add a smoke test over all AHBs like
  `test_create_expressions_table_from_submodule_with_validity`, skipped without the submodule).
- [ ] **Step 5: README** — 10–15 lines: what the view answers, `via`, the two calls in order, import path, the
  `drop_raw_tables=False` requirement.
- [ ] **Step 6: Commit** `feat: v_ahb_condition_usages view`

### Task 3 (ahb-tabellen, independent of Tasks 1–2): MCP tool `search_bedingung_usage`

Runs in a separate worktree of ahb-tabellen, in parallel with Tasks 1–2. Tests use mocks/fixtures, not the real DB.

**Files (follow `search_ahb_lines`):**
- Modify: `src/server/mcp/tools.ts`, `src/server/mcp/services.ts`, the AHB service and repository
  (`src/server/service/ahb.service.ts`, `src/server/repository/ahb.ts`) or new files next to them if cleaner.
- Test: `src/server/mcp/server.spec.ts`, `src/server/repository/ahb.spec.ts` (or new spec files next to new code).

**Interfaces:**
- Tool `search_bedingung_usage`, read-only annotations like the others. Input (zod): `formatVersion: string`
  (required), `bedingung: string` (required), `format?: string`, `pruefi?: string`, `limit?: number` (int 1–1000,
  default 200).
- Normalization: strip whitespace and brackets; uppercase letter suffixes/prefixes (`ub1` → `UB1`, `2p` → `2P`);
  reject empty after normalization (validation error).
- Query on `v_ahb_condition_usages` filtered by `format_version`, `condition_key`, optional `pruefidentifikator`.
  `format`: if it is a plain format (`UTILMD`), filter `format = ?`; if it is a detailed format (`UTILMDS`,
  `UTILMDG`, `UTILMDW`; anything where `getFormatOfPruefidentifikator` semantics differ from the plain column),
  first select the distinct Prüfidentifikatoren of that format version and plain format, keep those for which
  `getFormatOfPruefidentifikator(p) === format` (from `@hochfrequenz/efoli`), and filter `pruefidentifikator IN
  (...)` in SQL. Count and limit therefore stay correct.
- Result: `{ formatVersion, bedingung, totalLines, returnedLines, truncated, pruefis: [{ pruefidentifikator,
  description, lines: [{ segmentgroupKey, segmentCode, dataElement, qualifier, lineName, lineAhbStatus, via:
  (string | null)[] }] }] }` — a line = one `v_ahbtabellen` line (same Prüfidentifikator + `sort_path`); `via` lists
  all ways it reaches the key (`null` = direct), sorted with `null` first. `limit` and `totalLines` count lines, not
  view rows. Order: Prüfidentifikator, then `sort_path`.
- Tool description: what it answers, that `via` marks use through a package/UB condition, plus the existing
  `BEDINGUNG_JUMP_HINT` for the condition text.

- [ ] **Step 1: Failing tests:** tool forwards validated input; normalization cases (Review Focus 3); grouping and
  `via` merging (a line with direct + via UB1 → one line, `via: [null, "UB1"]`); `limit` with `truncated` and
  `totalLines`; detailed format filter builds the `IN` list (Review Focus 4); unknown condition → empty result.
- [ ] **Step 2: Run** `npx jest <spec files>` — expected FAIL. **Step 3: Implement.** **Step 4: Run** `npm test`,
  `npm run lint`, type check — expected PASS.
- [ ] **Step 5: Commit** `feat(mcp): search_bedingung_usage — where is a condition used (direct and via packages/UB)`

### Rollout (orchestrator, after review; not a builder task)

fundamend PR → merge → release → xml-migs-and-ahbs: bump fundamend, call `create_and_fill_ahb_condition_usage_table`
and `create_ahb_condition_usage_view` after `create_ahbtabellen_view` in `load_ahbs_into_sqlitedb.py` (and the
AHB+MIG script if it builds the same views), DB release → ahb-tabellen: DB bump + Task 3 PR (rebased) → merge →
deploy → smoke test the tool against the real DB (e.g. `931` in FV2610 UTILMD) → comment on ahb-tabellen#1002.
