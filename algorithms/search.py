from algorithms.problems import SearchProblem
import algorithms.utils as utils
from world.game import Directions
from algorithms.heuristics import nullHeuristic


def tinyHouseSearch(problem: SearchProblem):
    """
    Returns a sequence of moves that solves tinyHouse. For any other building, the
    sequence of moves will be incorrect, so only use this for tinyHouse.
    """
    s = Directions.SOUTH
    w = Directions.WEST
    return [s, s, w, s, w, w, s, w]


def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    # TODO: Add your code here
    utils.raiseNotDefined()


def breadthFirstSearch(problem: SearchProblem):
    """
    Search the shallowest nodes in the search tree first.
    """
    frontera = utils.Queue()
    start = problem.getStartState()
    
    frontera.push((start, []))
    visitado = {start}
    
    while not frontera.isEmpty():
        estado, acciones = frontera.pop()
        if problem.isGoalState(estado):
            return acciones
        
        for succ, action, _stepCost in problem.getSuccessors(estado):
            if succ not in visitado:
                visitado.add(succ)
                frontera.push((succ, acciones + [action]))
    return []


def uniformCostSearch(problem: SearchProblem):
    """
    Search the node of least total cost first.
    """

    # TODO: Add your code here
    utils.raiseNotDefined()


def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """
    frontera = utils.PriorityQueue()
    start = problem.getStartState()
    
    frontera.push((start, [], 0), heuristic(start, problem))
    best_cost = {start: 0}
    
    while not frontera.isEmpty():
        state, actions, curr_cost = frontera.pop()
        
        if curr_cost != best_cost.get(state, float("inf")):
            continue
        
        if problem.isGoalState(state):
            return actions
        
        for succ, action, stepCost in problem.getSuccessors(state):
            nuevo_cost = curr_cost + stepCost
            if nuevo_cost < best_cost.get(succ, float("inf")):
                best_cost[succ] = nuevo_cost
                prioridad = nuevo_cost + heuristic(succ, problem)
                frontera.push((succ, actions + [action], nuevo_cost), prioridad)
    return []


# Abbreviations (you can use them for the -f option in main.py)
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
