import sys
from collections import deque
from decimal import Decimal
from fractions import Fraction
from math import gcd, lcm
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


def priority_order(tasks):
    """Task indices from highest to lowest... RM priority: shortest period first, ties by index."""
    return sorted(range(len(tasks)), key=lambda i: (tasks[i].period, i))


def hyperperiod(tasks):
    return lcm(*(task.period for task in tasks))

#Calculate total utilization of the tasks
def utilization(tasks):
    return sum(Fraction(task.execution, task.period) for task in tasks)

def response_time(task, higher_priority):
    """Response time analysis for a task given higher priority tasks."""
    response = task.execution
    while True:
        updated = task.execution + sum(
            -(-response // other.period) * other.execution for other in higher_priority
        )
        if updated > task.deadline:
            return None
        if updated == response:
            return response
        response = updated


def definitely_infeasible(tasks):
    """Check if the task set is definitely infeasible based on utilization and response time analysis."""
    if utilization(tasks) > 1:
        return True

    order = priority_order(tasks)
    for rank, i in enumerate(order):
        higher_priority = [tasks[j] for j in order[:rank]]
        if response_time(tasks[i], higher_priority) is None:
            return True
    return False

def main():
    tasks = to_ticks(parse_workload(sys.argv[1]))
    order = priority_order(tasks)
    horizon = hyperperiod(tasks)
    is_infeasible = definitely_infeasible(tasks)
    response_times = [
        response_time(tasks[i], [tasks[j] for j in order[:rank]])
        for rank, i in enumerate(order)
    ]


if __name__ == "__main__":
    main()