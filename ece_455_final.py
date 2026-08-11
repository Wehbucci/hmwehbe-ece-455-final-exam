import sys
from decimal import Decimal
from math import gcd
from typing import NamedTuple

TICKS_PER_UNIT = 1000


class Task(NamedTuple):
    execution: Decimal | int
    period: Decimal | int
    deadline: Decimal | int


def parse_workload(path):
    """Read a workload file into a list of Tasks, indexed in file order."""
    tasks = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Decimal, not float
            execution, period, deadline = (Decimal(v) for v in line.split(","))
            tasks.append(Task(execution, period, deadline))
    return tasks


def to_ticks(tasks):
    """Rescale tasks onto an exact integer time axis, reduced by their common gcd."""
    scaled = [
        Task(*(int((v * TICKS_PER_UNIT).to_integral_value()) for v in task))
        for task in tasks
    ]

    divisor = 0
    for task in scaled:
        for value in task:
            divisor = gcd(divisor, value)
    if divisor > 1:
        scaled = [Task(*(v // divisor for v in task)) for task in scaled]
    return scaled


def main():
    to_ticks(parse_workload(sys.argv[1]))


if __name__ == "__main__":
    main()
