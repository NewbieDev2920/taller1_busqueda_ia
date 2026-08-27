from typing import Tuple
from algorithms import utils
from algorithms.problems import SystemRepairProblem


def nullHeuristic(state, problem=None):
    return 0


def manhattanHeuristic(state, problem):
    position, hasKit, pendingSystems = state

    def distance(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not hasKit:
        return distance(position, problem.kitPosition)

    if pendingSystems:
        return min(
            distance(position, system)
            for system in pendingSystems
        )

    return distance(position, problem.controlPosition)


def euclideanHeuristic(state, problem):
    position, hasKit, pendingSystems = state

    def distance(a, b):
        return (
            (a[0] - b[0]) ** 2
            + (a[1] - b[1]) ** 2
        ) ** 0.5

    if not hasKit:
        return distance(position, problem.kitPosition)

    if pendingSystems:
        return min(
            distance(position, system)
            for system in pendingSystems
        )

    return distance(position, problem.controlPosition)


def systemRepairHeuristic(
    state: Tuple[Tuple, bool, Tuple],
    problem: SystemRepairProblem
):
    position, hasKit, pendingSystems = state

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def mstCost(points):
        points = tuple(sorted(set(points)))

        if len(points) <= 1:
            return 0

        key = ("mst", points)

        if key in problem.heuristicInfo:
            return problem.heuristicInfo[key]

        visited = {points[0]}
        unvisited = set(points[1:])
        total = 0

        while unvisited:
            bestCost = float("inf")
            bestPoint = None

            for u in visited:
                for v in unvisited:
                    cost = manhattan(u, v)

                    if cost < bestCost:
                        bestCost = cost
                        bestPoint = v

            total += bestCost
            visited.add(bestPoint)
            unvisited.remove(bestPoint)

        problem.heuristicInfo[key] = total
        return total

    if not hasKit:
        points = (
            problem.kitPosition,
            *pendingSystems,
            problem.controlPosition,
        )

        return (
            manhattan(position, problem.kitPosition)
            + mstCost(points)
        )

    points = (
        position,
        *pendingSystems,
        problem.controlPosition,
    )

    return mstCost(points)