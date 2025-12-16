"""
Benchmarks for v_ahb_diff query performance.

These benchmarks measure SELECT query time only - database creation happens
in the module-scoped fixtures and is not included in the timing.

Run with: pytest benchmarks/ --benchmark-only
Save results: pytest benchmarks/ --benchmark-only --benchmark-json=results.json
"""

import pytest
from sqlmodel import Session, text

# FV2410 -> FV2504 benchmarks with representative pruefidentifikators
PRUEFIS_FV2410_FV2504 = ["55109", "13002", "25001"]


@pytest.mark.benchmark(group="v_ahb_diff_fv2410_fv2504")
@pytest.mark.parametrize("pruefi", PRUEFIS_FV2410_FV2504)
def test_diff_query_fv2410_fv2504(
    benchmark, session_fv2410_fv2504_with_diff_view: Session, pruefi: str
) -> None:
    """Benchmark diff query: FV2410 -> FV2504 with same pruefidentifikator."""
    query = text("""
        SELECT * FROM v_ahb_diff
        WHERE new_pruefidentifikator = :pruefi
          AND old_pruefidentifikator = :pruefi
          AND new_format_version = 'FV2504'
          AND old_format_version = 'FV2410'
        ORDER BY sort_path ASC
    """)

    def run_query():
        return list(session_fv2410_fv2504_with_diff_view.execute(query, {"pruefi": pruefi}))

    result = benchmark.pedantic(run_query, iterations=10, rounds=1)
    assert len(result) > 0, f"Query returned no results for pruefi {pruefi}"


@pytest.mark.benchmark(group="v_ahb_diff_fv2510_fv2604")
def test_diff_query_fv2510_fv2604_13009(
    benchmark, session_fv2510_fv2604_mscons_with_diff_view: Session
) -> None:
    """Benchmark diff query: FV2510 -> FV2604, pruefidentifikator 13009."""
    query = text("""
        SELECT * FROM v_ahb_diff
        WHERE new_pruefidentifikator = '13009'
          AND old_pruefidentifikator = '13009'
          AND new_format_version = 'FV2510'
          AND old_format_version = 'FV2604'
        ORDER BY sort_path ASC
    """)

    def run_query():
        return list(session_fv2510_fv2604_mscons_with_diff_view.execute(query, {"pruefi": "13009"}))

    result = benchmark.pedantic(run_query, iterations=10, rounds=1)
    assert len(result) > 0, "Query returned no results for pruefi 13009"
