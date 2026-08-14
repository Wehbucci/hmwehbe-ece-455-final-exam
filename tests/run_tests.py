#used AI to create this test script. The AI was used to help me write the test script to run my code against the test cases.

"""Run ece_455_final.py against every case in tests/cases and compare stdout byte for byte.

Each case is a pair: <name>.txt is the workload, <name>.out is the exact expected
stdout. See PROVENANCE.txt for where the expected values came from.

    python3 tests/run_tests.py
"""

import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROGRAM = ROOT / "ece_455_final.py"
CASES = pathlib.Path(__file__).resolve().parent / "cases"


def run_case(workload):
    started = time.perf_counter()
    result = subprocess.run(
        [sys.executable, str(PROGRAM), str(workload)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result, time.perf_counter() - started


def main():
    workloads = sorted(CASES.glob("*.txt"))
    if not workloads:
        print("no cases found in %s" % CASES)
        return 1

    failures = []
    print("%-26s %-8s %8s  %s" % ("CASE", "RESULT", "TIME", "DETAIL"))
    print("-" * 72)

    for workload in workloads:
        expected = workload.with_suffix(".out").read_text()
        try:
            result, elapsed = run_case(workload)
        except subprocess.TimeoutExpired:
            failures.append(workload.stem)
            print("%-26s %-8s %8s  exceeded the 60s limit" % (workload.stem, "TIMEOUT", "-"))
            continue

        problems = []
        if result.stdout != expected:
            problems.append("stdout %r, expected %r" % (result.stdout, expected))
        if result.stderr:
            problems.append("stderr %r" % result.stderr[:120])
        if result.returncode != 0:
            problems.append("exit code %d" % result.returncode)

        if problems:
            failures.append(workload.stem)
        print("%-26s %-8s %7.2fs  %s" % (
            workload.stem,
            "FAIL" if problems else "pass",
            elapsed,
            "; ".join(problems),
        ))

    print("-" * 72)
    print("%d/%d passed" % (len(workloads) - len(failures), len(workloads)))
    if failures:
        print("failed: %s" % ", ".join(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
