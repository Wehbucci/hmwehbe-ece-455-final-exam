import sys
from decimal import Decimal
from typing import NamedTuple


class Task(NamedTuple):
    execution: Decimal
    period: Decimal
    deadline: Decimal


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


def main():
    parse_workload(sys.argv[1])


if __name__ == "__main__":
    main()
