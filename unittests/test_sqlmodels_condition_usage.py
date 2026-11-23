import logging
import shutil
import threading
import uuid
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlmodel import Session, create_engine, select
from syrupy.assertion import SnapshotAssertion

from fundamend.sqlmodels import condition_usage, create_ahbtabellen_view
from fundamend.sqlmodels.anwendungshandbuch import Paket
from fundamend.sqlmodels.condition_usage import (
    AhbConditionUsage,
    AhbConditionUsageLine,
    KeyType,
    _extract_keys_cached,
    create_ahb_condition_usage_view,
    create_and_fill_ahb_condition_usage_table,
    resolve_condition_keys,
)
from fundamend.sqlmodels.expression_view import create_and_fill_ahb_expression_table

from .conftest import cached_ahb_db, is_private_submodule_checked_out

_UTILTS = Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"
_AHB_FILES = [(_UTILTS, date(2023, 10, 1), date(2024, 4, 3))]


def test_direct() -> None:
    assert resolve_condition_keys("Muss [931] U [932]", {}) == [
        ("931", KeyType.CONDITION, ""),
        ("932", KeyType.CONDITION, ""),
    ]


def test_via_ub_and_direct_ub_row() -> None:
    rows = resolve_condition_keys("Muss [UB1]", {"UB1": "([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])"})
    assert ("UB1", KeyType.UB_CONDITION, "") in rows
    assert {k for k, _, v in rows if v == "UB1"} == {"931", "932", "933", "490", "491"}


def test_direct_and_indirect_on_same_line() -> None:
    rows = resolve_condition_keys("Muss [931] U [UB1]", {"UB1": "[931]"})
    assert ("931", KeyType.CONDITION, "") in rows
    assert ("931", KeyType.CONDITION, "UB1") in rows


def test_two_vias() -> None:
    rows = resolve_condition_keys("Muss [UB1] U [2P]", {"UB1": "[25]", "2P": "[25]"})
    assert ("25", KeyType.CONDITION, "UB1") in rows
    assert ("25", KeyType.CONDITION, "2P") in rows


def test_nested_keeps_outermost_via() -> None:
    rows = resolve_condition_keys("Muss [UB1]", {"UB1": "[3P]", "3P": "[25]"})
    assert ("3P", KeyType.PACKAGE, "UB1") in rows
    assert ("25", KeyType.CONDITION, "UB1") in rows
    assert ("25", KeyType.CONDITION, "3P") not in rows


def test_cycle_terminates() -> None:
    rows = resolve_condition_keys("Muss [UB1]", {"UB1": "[2P]", "2P": "[UB1] U [7]"})
    assert ("7", KeyType.CONDITION, "UB1") in rows
    assert ("2P", KeyType.PACKAGE, "UB1") in rows
    assert not any(key == via for key, _, via in rows)  # no self-row like (UB1, ub_condition, UB1)


def test_undefined_key_has_no_children() -> None:
    assert resolve_condition_keys("Muss [UB1]", {}) == [("UB1", KeyType.UB_CONDITION, "")]


def test_dash_definition_has_no_children() -> None:
    assert resolve_condition_keys("Muss [1P]", {"1P": "--"}) == [("1P", KeyType.PACKAGE, "")]


def test_unparseable_expression_raises() -> None:
    with pytest.raises(ValueError):
        resolve_condition_keys("Muss [[ U", {})


def test_result_is_sorted_and_distinct() -> None:
    rows = resolve_condition_keys("Muss [932] U [931] U [932] U [UB1]", {"UB1": "[932] U [931]"})
    assert rows == sorted(rows, key=lambda r: (r[0], r[1].value, r[2]))
    assert len(rows) == len(set(rows))


def _rows(db_path: Path) -> list[tuple[str, ...]]:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(bind=engine) as session:
        create_and_fill_ahb_condition_usage_table(session)
        usages = session.exec(select(AhbConditionUsage)).all()
        return sorted(
            (u.expression, u.condition_key, u.key_type.value, u.via, str(u.format), str(u.edifact_format_version))
            for u in usages
        )


def test_table_is_filled_and_deterministic() -> None:
    db_path = cached_ahb_db(_AHB_FILES, drop_raw_tables=False)
    first = _rows(db_path)
    assert all(
        not logging.getLogger(name).filters for name in ("ahbicht", "ahbicht.expressions", "ahbicht.expressions.foo")
    )  # filter removed
    assert first
    assert any(r[1] == "931" and r[3] == "UB1" for r in first)
    assert any(r[1] == "931" and r[3] == "" for r in first)
    with create_engine(f"sqlite:///{db_path}").connect() as connection:  # SQL consumers see the values, not the names
        stored = {r[0] for r in connection.execute(text("SELECT DISTINCT key_type FROM ahb_condition_usages"))}
    assert stored <= {"condition", "package", "ub_condition"} and "condition" in stored
    assert _rows(db_path) == first  # building again (on the same db) yields identical rows


def test_drop_raw_tables_raises() -> None:
    db_path = cached_ahb_db(_AHB_FILES, drop_raw_tables=True)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(bind=engine) as session:
        with pytest.raises(ValueError, match="drop_raw_tables=False"):
            create_and_fill_ahb_condition_usage_table(session)


def _view_session() -> Session:
    db_path = cached_ahb_db(_AHB_FILES, drop_raw_tables=False)
    engine = create_engine(f"sqlite:///{db_path}")
    session = Session(bind=engine)
    create_and_fill_ahb_expression_table(session)
    create_ahbtabellen_view(session)
    create_and_fill_ahb_condition_usage_table(session)
    create_ahb_condition_usage_view(session)
    return session


def test_view_requires_prerequisites(tmp_path: Path) -> None:
    db_path = tmp_path / "copy.sqlite"
    shutil.copy(cached_ahb_db(_AHB_FILES, drop_raw_tables=False), db_path)  # don't touch a potentially cached db
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(bind=engine) as session:
        with pytest.raises(ValueError, match="v_ahbtabellen"):  # not yet a view (at most an empty table)
            create_ahb_condition_usage_view(session)
        create_and_fill_ahb_expression_table(session)
        create_ahbtabellen_view(session)
        with pytest.raises(ValueError, match="ahb_condition_usages"):  # not filled yet
            create_ahb_condition_usage_view(session)


def test_two_definition_maps_give_different_children() -> None:
    expression = "Muss [UB1]"
    first = resolve_condition_keys(expression, {"UB1": "[25]"})
    second = resolve_condition_keys(expression, {"UB1": "[26]"})
    assert ("25", KeyType.CONDITION, "UB1") in first and ("26", KeyType.CONDITION, "UB1") not in first
    assert ("26", KeyType.CONDITION, "UB1") in second and ("25", KeyType.CONDITION, "UB1") not in second


def test_failing_definition_is_parsed_only_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def _failing_parse(text: str) -> tuple[tuple[str, KeyType], ...]:
        calls.append(text)
        raise SyntaxError("nope")

    _extract_keys_cached.cache_clear()
    monkeypatch.setattr(condition_usage, "_parse_keys", _failing_parse)
    try:
        for expression in ["Muss [1P]", "Muss [1P] U [2P]", "Muss [1P] O [3P]"]:
            with pytest.raises(ValueError):  # the expressions are unparseable with the patched parser
                resolve_condition_keys(expression, {"1P": "--"})
        assert sorted(calls) == ["Muss [1P]", "Muss [1P] O [3P]", "Muss [1P] U [2P]"]  # each text once
        calls.clear()
        _extract_keys_cached("--")
        _extract_keys_cached("--")
        assert calls == ["--"]
    finally:
        _extract_keys_cached.cache_clear()


def _copy_db(tmp_path: Path) -> Session:
    db_path = tmp_path / "copy.sqlite"
    shutil.copy(cached_ahb_db(_AHB_FILES, drop_raw_tables=False), db_path)
    return Session(bind=create_engine(f"sqlite:///{db_path}"))


def test_padded_statuses_still_show_up_in_view(tmp_path: Path) -> None:
    with _copy_db(tmp_path) as session:
        # line_ahb_status in ahb_hierarchy_materialized is trimmed already, only the raw *_ahb_status columns are not
        assert (
            session.execute(
                text("SELECT COUNT(*) FROM v_ahbtabellen WHERE line_ahb_status != TRIM(line_ahb_status)")
            ).scalar()
            == 0
        )
        session.execute(
            text(
                "UPDATE ahb_hierarchy_materialized SET dataelement_ahb_status = '  ' || dataelement_ahb_status || ' '"
                " WHERE dataelement_ahb_status IS NOT NULL"
            )
        )
        create_and_fill_ahb_expression_table(session)
        create_ahbtabellen_view(session)
        create_and_fill_ahb_condition_usage_table(session)
        create_ahb_condition_usage_view(session)
        usages = session.exec(select(AhbConditionUsage)).all()
        assert usages and all(u.expression == u.expression.strip() for u in usages)
        lines = session.exec(select(AhbConditionUsageLine).where(AhbConditionUsageLine.condition_key == "931")).all()
        assert any(line.via == "UB1" for line in lines) and any(line.via is None for line in lines)


def test_package_is_resolved_in_db(tmp_path: Path) -> None:
    with _copy_db(tmp_path) as session:
        ahb_pk, line_id = session.execute(
            text(
                "SELECT anwendungshandbuch_primary_key, id FROM ahb_hierarchy_materialized"
                " WHERE line_ahb_status = 'X [931] [500] ∧ [UB1]' LIMIT 1"
            )
        ).one()
        session.execute(
            text(
                "UPDATE ahb_hierarchy_materialized SET dataelement_ahb_status = 'Muss [9P]',"
                " line_ahb_status = 'Muss [9P]'"
                " WHERE id = :id"
            ),
            {"id": line_id},
        )
        session.add(Paket(nummer="9P", text="[77] U [78]", anwendungshandbuch_primary_key=uuid.UUID(ahb_pk)))
        session.commit()
        create_and_fill_ahb_expression_table(session)
        create_ahbtabellen_view(session)
        create_and_fill_ahb_condition_usage_table(session)
        create_ahb_condition_usage_view(session)
        lines = session.exec(
            select(AhbConditionUsageLine).where(AhbConditionUsageLine.line_ahb_status == "Muss [9P]")
        ).all()
        assert {(line.condition_key, line.key_type, line.via) for line in lines} == {
            ("9P", KeyType.PACKAGE, None),
            ("77", KeyType.CONDITION, "9P"),
            ("78", KeyType.CONDITION, "9P"),
        }


def test_view_uses_lookup_index() -> None:
    with _view_session() as session:
        url = session.get_bind().engine.url
    # a fresh engine and connection, like the consumer has (the pool would hand out the connection that ran the DDL
    # and a plan computed on that one can be stale)
    with create_engine(url).connect() as connection:
        for where in [
            "format_version = 'FV2310' AND condition_key = '931'",
            "format_version = 'FV2310' AND condition_key = '931' AND format = 'UTILTS'",
            "format_version = 'FV2310' AND condition_key = '931' AND pruefidentifikator = '25001'",
        ]:
            plan = " ".join(
                str(row[3])
                for row in connection.execute(
                    text(
                        f"EXPLAIN QUERY PLAN SELECT * FROM v_ahb_condition_usages WHERE {where}"
                        " ORDER BY pruefidentifikator, sort_path"
                    )
                )
            )
            assert "idx_ahb_condition_usages_lookup" in plan, plan
            assert "SCAN" not in plan, plan
            # a temp b-tree for the final ORDER BY over the (small) result set is fine; scans are not


def test_view_direct_and_via() -> None:
    with _view_session() as session:
        lines = session.exec(select(AhbConditionUsageLine).where(AhbConditionUsageLine.condition_key == "931")).all()
        assert any(line.via == "UB1" for line in lines)
        assert any(line.via is None for line in lines)
        assert len({line.id for line in lines}) == len(lines)
        # a line that uses a key directly and via UB appears twice (once per via)
        by_line: dict[tuple[str, str], set[str | None]] = {}
        for line in lines:
            by_line.setdefault((line.pruefidentifikator, line.sort_path), set()).add(line.via)
        assert any(vias >= {None, "UB1"} for vias in by_line.values())


@pytest.mark.snapshot
def test_view_snapshot(snapshot: SnapshotAssertion) -> None:
    with _view_session() as session:
        stmt = (
            select(AhbConditionUsageLine)
            .where(AhbConditionUsageLine.pruefidentifikator == "25001", AhbConditionUsageLine.condition_key == "931")
            .order_by(AhbConditionUsageLine.sort_path, AhbConditionUsageLine.via)  # type: ignore[arg-type]
        )
        results = session.exec(stmt).all()
    raw_results = [r.model_dump(mode="json") for r in results]
    for raw_result in raw_results:
        for guid_column in ["id", "anwendungshandbuch_primary_key"]:
            raw_result.pop(guid_column, None)
    assert raw_results
    snapshot.assert_match(raw_results)


def test_create_condition_usages_from_submodule() -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    relevant_files = [(p, date(2025, 6, 6), None) for p in (private_submodule_root / "FV2504").rglob("**/*AHB*.xml")]
    db_path = cached_ahb_db(relevant_files, drop_raw_tables=False)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(bind=engine) as session:
        create_and_fill_ahb_expression_table(session)
        create_ahbtabellen_view(session)
        create_and_fill_ahb_condition_usage_table(session)
        create_ahb_condition_usage_view(session)
        assert session.exec(select(AhbConditionUsageLine).limit(1)).first() is not None


def test_nbsp_status_still_shows_up_in_view(tmp_path: Path) -> None:
    nbsp = "\u00a0"
    with _copy_db(tmp_path) as session:
        # sql trims only spaces, so a trailing NBSP stays in line_ahb_status; the fill must keep it, too
        session.execute(
            text(
                "UPDATE ahb_hierarchy_materialized SET dataelement_ahb_status = dataelement_ahb_status || :nbsp,"
                " line_ahb_status = line_ahb_status || :nbsp WHERE line_ahb_status = 'X [931] [500] ∧ [UB1]'"
            ),
            {"nbsp": nbsp},
        )
        create_and_fill_ahb_expression_table(session)
        create_ahbtabellen_view(session)
        create_and_fill_ahb_condition_usage_table(session)
        create_ahb_condition_usage_view(session)
        lines = session.exec(
            select(AhbConditionUsageLine).where(AhbConditionUsageLine.line_ahb_status == f"X [931] [500] ∧ [UB1]{nbsp}")
        ).all()
        assert lines


def test_log_filter_is_thread_local_and_removed() -> None:
    logger = logging.getLogger("ahbicht.expressions")
    seen: list[str] = []

    class _Collector(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            seen.append(record.getMessage())

    child_logger = logging.getLogger("ahbicht.expressions.foo")
    handler = _Collector(level=logging.DEBUG)
    logger.addHandler(handler)
    old_level = logger.level
    logger.setLevel(logging.DEBUG)

    def _log_from_other_thread() -> None:
        logger.warning("other thread")

    original_resolve = condition_usage.resolve_condition_keys

    def _resolve_and_log(expression: str, definitions: dict[str, str]) -> list[tuple[str, KeyType, str]]:
        logger.warning("filling thread")
        child_logger.warning("filling thread child")
        thread = threading.Thread(target=_log_from_other_thread)
        thread.start()
        thread.join()
        return original_resolve(expression, definitions)

    db_path = cached_ahb_db(_AHB_FILES, drop_raw_tables=False)
    try:
        with Session(bind=create_engine(f"sqlite:///{db_path}")) as session:
            with pytest.MonkeyPatch.context() as monkeypatch:
                monkeypatch.setattr(condition_usage, "resolve_condition_keys", _resolve_and_log)
                create_and_fill_ahb_condition_usage_table(session)
        assert "other thread" in seen
        assert "filling thread" not in seen
        assert "filling thread child" not in seen
        assert not logger.filters
        logger.warning("after")
        assert "after" in seen
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)


def test_cache_is_cleared_at_start_of_fill(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def _failing_parse(text_: str) -> tuple[tuple[str, KeyType], ...]:
        calls.append(text_)
        raise RuntimeError("transient")

    _extract_keys_cached.cache_clear()
    with monkeypatch.context() as patched:
        patched.setattr(condition_usage, "_parse_keys", _failing_parse)
        assert _extract_keys_cached("Muss [1]") is None  # a transient failure is cached now
    assert _extract_keys_cached.cache_info().currsize == 1
    db_path = cached_ahb_db(_AHB_FILES, drop_raw_tables=False)
    with Session(bind=create_engine(f"sqlite:///{db_path}")) as session:
        create_and_fill_ahb_condition_usage_table(session)
    assert calls == ["Muss [1]"]
    assert _extract_keys_cached("Muss [1]") is not None  # parsed afresh with the real parser
