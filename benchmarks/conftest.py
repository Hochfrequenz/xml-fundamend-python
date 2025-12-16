# Re-export fixtures from unittests for use in benchmarks
# The database creation happens in the fixture (module-scoped), not during benchmark timing.
# Only the SELECT queries inside benchmark() are timed.

from unittests.conftest import (
    is_private_submodule_checked_out,
    session_fv2410_fv2504_with_diff_view,
    session_fv2510_fv2604_mscons_with_diff_view,
)

__all__ = [
    "is_private_submodule_checked_out",
    "session_fv2410_fv2504_with_diff_view",
    "session_fv2510_fv2604_mscons_with_diff_view",
]
