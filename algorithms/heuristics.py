from typing import Any, Tuple
from algorithms import utils
from algorithms.problems import MultiSurvivorProblem


def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def manhattanHeuristic(state, problem):
    """
    The Manhattan distance heuristic.
    """
    pos = state
    
    goal = getattr(problem, "goal", None)
    if goal is None:
        return 0
    return abs(pos[0] - goal[0]) + abs(pos[1]- goal[1])


def euclideanHeuristic(state, problem):
    """
    The Euclidean distance heuristic.
    """
    pos = state
    
    goal = getattr(problem, "goal", None)
    if goal is None:
        return 0
    dx = pos[0] - goal[0]
    dy = pos[1] - goal[1]
    return (dx**2 + dy**2) **0.5


def survivorHeuristic(state: Tuple[Tuple, Any], problem: MultiSurvivorProblem):
    """
    Your heuristic for the MultiSurvivorProblem.

    state: (position, survivors_grid)
    problem: MultiSurvivorProblem instance

    This must be admissible and preferably consistent.

    Hints:
    - Use problem.heuristicInfo to cache expensive computations
    - Go with some simple heuristics first, then build up to more complex ones
    - Consider: distance to nearest survivor + MST of remaining survivors
    - Balance heuristic strength vs. computation time (do experiments!)
    """
    pos, survivors_grid = state

    if hasattr(survivors_grid, "asList"):
        survivors = survivors_grid.asList()
    else:
        survivors = list(survivors_grid)

    if not survivors:
        return 0

    hinfo = problem.heuristicInfo
    dist_cache = hinfo.setdefault("dist_cache", {})  
    mst_cache  = hinfo.setdefault("mst_cache", {})    

    def cached_dist(a, b):
        key = (a, b) if a <= b else (b, a)
        d = dist_cache.get(key)
        if d is None:
            d = manhattanHeuristic(a, b)
            dist_cache[key] = d
        return d

    nearest = None
    for s in survivors:
        d = cached_dist(pos, s)
        if nearest is None or d < nearest:
            nearest = d

    points_key = frozenset(survivors)
    mst_cost = mst_cache.get(points_key)
    if mst_cost is None:
        if len(survivors) == 1:
            mst_cost = 0
        else:
            start = survivors[0]
            visited = set([start])

            pq = utils.PriorityQueue()
            for v in survivors[1:]:
                pq.push(v, cached_dist(start, v))

            mst_cost = 0
            while len(visited) < len(survivors):
                v = pq.pop()
                if v in visited:
                    continue

                best = None
                for u in visited:
                    d = cached_dist(u, v)
                    if best is None or d < best:
                        best = d
                mst_cost += best

                visited.add(v)

                for w in survivors:
                    if w in visited:
                        continue
                    best_w = None
                    for u in visited:
                        d = cached_dist(u, w)
                        if best_w is None or d < best_w:
                            best_w = d
                    pq.push(w, best_w)

        mst_cache[points_key] = mst_cost

    return nearest + mst_cost
