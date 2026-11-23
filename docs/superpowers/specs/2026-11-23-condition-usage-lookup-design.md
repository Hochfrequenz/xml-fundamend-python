# Condition usage lookup: where is `[931]` used? (design)

Date: 2026-11-23. Serves Hochfrequenz/ahb-tabellen#1002 (`search_bedingung_usage`). Spans three repos:
xml-fundamend-python (this repo, most of the work), xml-migs-and-ahbs (DB build), ahb-tabellen (MCP tool).

## Why

AI agents using the ahb-tabellen MCP need "in which Prüfidentifikatoren / segments / data elements / codes is
condition `[931]` used?", e.g. to judge the impact of a changed condition. A condition can be used directly
(`Muss [931]`) or only indirectly, through a package (`[2P]` = `[25] ⊻ [62]`) or a UB condition
(`[UB1]` = `([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])`). The user decided: **report direct and indirect use**,
each hit marked with how it is reached. Today the only option is a text search (`LIKE`) on the `bedingung` text
column of `v_ahbtabellen`, which also matches `[9310]` and misses indirect use.

History: the same lookup was first asked for inside EBDs (rebdhuhn#516); no EBD contains condition references, so
it lives here. Condition texts do not name specific EBDs either (only "im EBD" in general), so EBD references are not
part of this work.

## Goals

- Exact lookup by condition key per format version and format, including indirect use through packages and UB
  conditions, resolved transitively (nested definitions).
- Every hit tells whether it is direct or via which package/UB key the line references.
- Available as a table + view in the SQLite DB that fundamend builds, so ahb-tabellen (TypeScript, no Python at
  runtime) can answer it with a plain SQL query.
- MCP tool `search_bedingung_usage` in ahb-tabellen as specified in #1002.

## Non-goals

- No UI in ahb-tabellen, no comparison across format versions, no EBD references.
- No change to the existing `ahb_expressions` table or `v_ahbtabellen` (the known ambiguity of `node_texts` between
  UTILMD Strom and Gas, see the comment in `expression_view.py`, is a separate follow-up).
- No evaluation of conditions (that is ahbicht's job).

## Constraints

- Condition, package and UB numbers are only unique per (format version, **detailed format**). UTILMD Strom and Gas
  share the EDIFACT format `UTILMD` but can define the same number differently. The detailed format comes from
  efoli: `get_format_of_pruefidentifikator(pruefi)` returns `UTILMDS`, `UTILMDG`, `UTILMDW`, or the plain format.
  ahb-tabellen and the ahbicht API already use these names.
- Parsing uses ahbicht's `extract_categorized_keys` (already an optional dependency via `fundamend[sqlmodels,ahbicht]`).
- Package and UB definitions come from the tables `paket` and `ubbedingung`, so the DB must be built with
  `drop_raw_tables=False` (the xml-migs-and-ahbs script already does that). Raise a clear error otherwise.
- Output deterministic (the DB is diffed and snapshot-tested).
- Build time: one parse per distinct expression and per distinct definition text (~3600 expressions for two FVs);
  must not noticeably slow down the DB build.

## Approaches

- **Chosen: a key table in fundamend plus a view joined to the AHB lines; ahb-tabellen queries the view.** Exact,
  resolves indirect use with the parser that already exists, usable by every consumer of the DB.
- Regex over `line_ahb_status` in ahb-tabellen: rejected; it cannot resolve packages/UB conditions without a parser.
- Python helper over the pydantic models only: rejected; the TypeScript server cannot call it.

## Design

### Table `ahb_condition_usages` (SQLModel `AhbConditionUsage`, `fundamend/sqlmodels/condition_usage.py`)

One row per (AHB, expression, key, via):

| column | meaning |
|---|---|
| `id` | uuid primary key |
| `anwendungshandbuch_primary_key` | FK to `anwendungshandbuch`; the join key to the lines |
| `edifact_format_version` | e.g. `FV2610` |
| `format` | detailed format, e.g. `UTILMDS` (see Constraints) |
| `expression` | the stripped AHB status expression, e.g. `Muss [UB1]` |
| `condition_key` | the key without brackets: `931`, `UB1`, `2P` |
| `key_type` | what kind of key: one of `condition`, `package`, `ub_condition` |
| `via` | `None` if the key is written in the expression itself; otherwise the key **as written in the expression** through which it is reached (`UB1`, `2P`) |

- Rows for the package/UB key itself are direct rows (`condition_key = "UB1"`, `via = None`), so `UB1` can be
  looked up too.
- Nested definitions: a key reached via `[UB1]` → `[3P]` → `[25]` gets `via = "UB1"` (the outermost key from the
  expression). One row per distinct (key, via) per expression; the path beyond the first level is not stored.
- Unique constraint on (`anwendungshandbuch_primary_key`, `expression`, `condition_key`, `via`); indexes for the
  lookup (`edifact_format_version`, `format`, `condition_key`).
- The detailed format of an AHB is derived from its Prüfidentifikatoren. If they map to more than one detailed format,
  raise (that would break the uniqueness assumption).

### Resolution rules

- Parse each distinct expression once (cache across AHBs). Categories map to `key_type`: format/requirement
  constraint and hint keys → `condition`; package keys → `package`; time condition keys (`UB…`) → `ub_condition`.
- Definitions are looked up in the same AHB (`paket` / `ubbedingung` by `anwendungshandbuch_primary_key`), parsed the
  same way, recursively, with a visited set against cycles (a cycle is logged, not an error).
- A package/UB key without definition in that AHB: keep its direct row, log a warning, no children.
- A definition text that is not an expression (e.g. `--`) or does not parse: no children, logged.
- An expression that does not parse: no rows for it, logged (its error is already recorded in `ahb_expressions`).

### Functions (exported from `fundamend.sqlmodels`)

- `create_and_fill_ahb_condition_usage_table(session: Session) -> None`: builds the table from
  `ahb_hierarchy_materialized` (all four `*_ahb_status` columns, like `create_and_fill_ahb_expression_table`).
- `create_ahb_condition_usage_view(session: Session) -> None`: creates `v_ahb_condition_usages` = the lines of
  `v_ahbtabellen` joined on (`anwendungshandbuch_primary_key`, `line_ahb_status` = `expression`) with the usage table.
  Columns: all `v_ahbtabellen` columns that identify and describe a line (format version, detailed format,
  Prüfidentifikator, description, direction, segment group, segment, data element, qualifier, line name, line AHB
  status, sort path) plus `condition_key`, `key_type`, `via`. Requires `v_ahbtabellen` to exist (same pattern as the
  other views: SQL file + Python wrapper).

### xml-migs-and-ahbs

`load_ahbs_into_sqlitedb.py` calls both functions after `create_and_fill_ahb_expression_table` and
`create_ahbtabellen_view`; bump fundamend; new DB release.

### ahb-tabellen

- MCP tool `search_bedingung_usage` (read-only): `formatVersion` (required), `bedingung` (required; accepts `931`,
  `[931]`, `UB1`, `[2P]`), `format` (optional; `UTILMD` matches all of `UTILMDS/G/W`), `pruefi` (optional),
  `limit` (optional, default 200 lines).
- Result grouped by Prüfidentifikator (with description), each line: segment group/segment/data element/qualifier,
  line name, line AHB status, `via` (null = direct). Plus total counts, so a cut result says so. Tool description
  points to the ahbicht MCP for the condition text (as `bedingung-hint.ts` does).
- Repository query on `v_ahb_condition_usages`; DB bump to the new release.

## Tests

- fundamend, against the example XMLs (UTILTS has `[UB1]` with `[931]`, packages `[2P]` = `[25] ⊻ [62]`, `[1P]` = `--`):
  direct use; use via UB (`931` with `via = "UB1"`, plus the direct `UB1` row); use via package; nested
  definitions; cycle; undefined key; `--` definition; unparseable expression; two AHBs with the same number in
  different detailed formats stay apart; the multi-format AHB error; determinism (build twice, same rows).
- A snapshot of `v_ahb_condition_usages` for one Prüfidentifikator, like the existing view snapshots.
- ahb-tabellen: repository and tool tests (input normalization, format `UTILMD` vs `UTILMDS`, grouping, limit with
  total count, unknown condition → empty result, not an error).

## Rollout

fundamend PR + release → xml-migs-and-ahbs script + fundamend bump + DB release → ahb-tabellen DB bump + tool PR →
deploy. Driven in one go, as with the EBD chain.

## Left to the builder

Internal helper structure, logging wording, exact index set, SQL formatting, the TypeScript module layout in
ahb-tabellen (follow the existing `search_ahb_lines` tool).

## Decisions after the builder check (2026-11-23; these override the sections above where they differ)

1. **No detailed-format column.** fundamend has no detailed format (the `format` of an AHB comes from the XML tag
   `M_UTILMD`), and none is needed: the table is keyed by `anwendungshandbuch_primary_key`, which already keeps
   UTILMD Strom and Gas apart (one AHB each). `format` in the table and view is the plain format, like everywhere
   else. The detailed format is derived from the Prüfidentifikator where it is needed: in ahb-tabellen with
   `getFormatOfPruefidentifikator` from `@hochfrequenz/efoli` (the frontend already uses it in
   `pruefi-format.utils.ts`). The MCP `format` filter: a plain format (`UTILMD`) filters in SQL; a detailed format
   (`UTILMDS`) filters in SQL by its plain format and then by `getFormatOfPruefidentifikator(pruefi)`.
   This replaces `detailed_format` in the table above and drops the "AHB maps to several detailed formats" error.
2. **Prüfidentifikator.** The usage table is Prüfidentifikator-independent. Prüfidentifikator, its description, the
   `pruefi` filter and the grouping come from the `v_ahbtabellen` side of the view. The MCP `limit` and the total
   count are about lines (one line = one row of `v_ahbtabellen`). Each line lists all its usages of the key.
3. **Plain conditions are leaves.** Their texts are natural language. Only packages and UB conditions are resolved.
4. **Direct and indirect use on the same line.** Both are kept: one row per distinct `via`. The tool shows a line
   once, with all ways it reaches the key (e.g. `direct`, `via UB1`). In the table, direct use is stored as
   `via = ''` (not NULL), because SQLite does not enforce uniqueness for NULLs. The view exposes
   `NULLIF(via, '') AS via`, so consumers see `null` for direct use.
5. **Key spelling.** `condition_key` holds the keys exactly as `extract_categorized_keys` returns them, without
   brackets (verify the spelling of package and UB keys in a test). The MCP tool strips brackets and whitespace from
   its input before matching. No range or other normalization.
6. **The old `bedingung` text search** in `v_ahbtabellen` stays as it is (non-goal).
