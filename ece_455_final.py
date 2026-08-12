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


class Job:
    __slots__ = ("remaining", "deadline", "within_horizon")

    def __init__(self, remaining, deadline, within_horizon):
        self.remaining = remaining
        self.deadline = deadline
        self.within_horizon = within_horizon


def simulate(tasks):
    """Run preemptive RM over the first hyperperiod.

    Returns (True, preemption counts) if every job released in that window meets
    its deadline, otherwise (False, None).
    """
    order = priority_order(tasks)
    horizon = hyperperiod(tasks)

    pending = [deque() for _ in tasks]  # a task can have a backlog when D > P
    next_release = [0] * len(tasks)
    preemptions = [0] * len(tasks)
    outstanding = 0  # jobs released before the horizon that are still unfinished
    now = 0
    running = None

    while True:
        # Catch up on every release at or before now
        for i, task in enumerate(tasks):
            while next_release[i] <= now:
                release = next_release[i]
                job = Job(task.execution, release + task.deadline, release < horizon)
                pending[i].append(job)
                outstanding += job.within_horizon
                next_release[i] += task.period

        # Only jobs released inside the first hyperperiod count against feasibility
        for queue in pending:
            for job in queue:
                if job.within_horizon and now >= job.deadline:
                    return False, None

        current = next((i for i in order if pending[i]), None)
        if current is None:
            if now >= horizon and outstanding == 0:
                return True, preemptions
            now = min(next_release)  # idle, so skip to the next release
            running = None
            continue

        # The previous holder lost the CPU with work left, so it was preempted
        if running is not None and running != current and pending[running]:
            if now < horizon:
                preemptions[running] += 1
        running = current

        # Run until the job ends, its deadline passes, or anything is released
        job = pending[current][0]
        events = [now + job.remaining, job.deadline, *next_release]
        if now < horizon:
            events.append(horizon)
        step = min(event for event in events if event > now)

        job.remaining -= step - now
        now = step
        if job.remaining == 0:
            pending[current].popleft()
            outstanding -= job.within_horizon
            running = None
            if now >= horizon and outstanding == 0:
                return True, preemptions


def main():
    tasks = to_ticks(parse_workload(sys.argv[1]))
    if definitely_infeasible(tasks):
        feasible, preemptions = False, None
    else:
        feasible, preemptions = simulate(tasks)


if __name__ == "__main__":
    main()
