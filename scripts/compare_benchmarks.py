#!/usr/bin/env python3
"""Compare benchmark results and report regressions."""
import argparse
import json
import sys
from pathlib import Path

REGRESSION_THRESHOLD = 0.20  # 20% slower = regression


def load_benchmarks(path: Path) -> dict[str, float]:
    """Load benchmark results and return dict of test name -> median time."""
    with open(path) as f:
        data = json.load(f)
    return {b["name"]: b["stats"]["median"] for b in data["benchmarks"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare benchmark results and report regressions.")
    parser.add_argument("baseline", type=Path, help="Path to baseline benchmark JSON file")
    parser.add_argument("current", type=Path, help="Path to current benchmark JSON file")
    args = parser.parse_args()

    baseline_path: Path = args.baseline
    current_path: Path = args.current

    if not baseline_path.exists():
        print("No baseline found, skipping comparison.")
        return 0

    try:
        baseline = load_benchmarks(baseline_path)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading baseline: {e}")
        return 0

    try:
        current = load_benchmarks(current_path)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading current results: {e}")
        return 1

    regressions: list[tuple[str, float]] = []
    print("\n## Benchmark Comparison\n")
    print("| Test | Baseline | Current | Change |")
    print("|------|----------|---------|--------|")

    for name in sorted(set(baseline.keys()) | set(current.keys())):
        if name not in current:
            print(f"| {name} | {baseline[name]*1000:.1f}ms | - | REMOVED |")
            continue

        current_time = current[name]

        if name not in baseline:
            print(f"| {name} | - | {current_time*1000:.1f}ms | NEW |")
            continue

        baseline_time = baseline[name]
        change = (current_time - baseline_time) / baseline_time

        if change > REGRESSION_THRESHOLD:
            status = "🔴"
        elif change < -0.05:
            status = "🟢"
        else:
            status = ""

        print(f"| {name} | {baseline_time*1000:.1f}ms | {current_time*1000:.1f}ms | {change:+.1%} {status} |")

        if change > REGRESSION_THRESHOLD:
            regressions.append((name, change))

    print()
    if regressions:
        print(f"❌ {len(regressions)} regression(s) detected (>{REGRESSION_THRESHOLD:.0%} slower)")
        for name, change in regressions:
            print(f"  - {name}: {change:+.1%}")
        return 1
    else:
        print("✅ No regressions detected")
        return 0


if __name__ == "__main__":
    sys.exit(main())
