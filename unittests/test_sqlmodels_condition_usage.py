import shutil
from datetime import date
from pathlib import Path

import pytest
from lark.exceptions import LarkError
from sqlalchemy import text
from sqlmodel import Session, create_engine, select
from syrupy.assertion import SnapshotAssertion

from fundamend.sqlmodels import create_ahbtabellen_view
from fundamend.sqlmodels.condition_usage import (
    AhbConditionUsage,
    AhbConditionUsageLine,
    KeyType,
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


def test_undefined_key_has_no_children() -> None:
    assert resolve_condition_keys("Muss [UB1]", {}) == [("UB1", KeyType.UB_CONDITION, "")]


def test_dash_definition_has_no_children() -> None:
    assert resolve_condition_keys("Muss [1P]", {"1P": "--"}) == [("1P", KeyType.PACKAGE, "")]


def test_unparseable_expression_raises() -> None:
    with pytest.raises((SyntaxError, LarkError)):
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
    assert first
    assert any(r[1] == "931" and r[3] == "UB1" for r in first)
    assert any(r[1] == "931" and r[3] == "" for r in first)
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
        session.execute(text("DROP TABLE IF EXISTS v_ahbtabellen"))  # sqlmodel created it as a table first
        with pytest.raises(ValueError, match="v_ahbtabellen"):
            create_ahb_condition_usage_view(session)


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
