from algorithms.problems import SearchProblem
import algorithms.utils as utils
from world.game import Directions
from algorithms.heuristics import nullHeuristic
from algorithms.utils import Stack
from algorithms.utils import PriorityQueue


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
    frontera = Stack()
    visitados = []
    estado_ini = problem.getStartState()
    encontro = False 
    edge_from = {}
    goal = None
    lista_acciones = []
    
    frontera.push(estado_ini)
    
    if problem.isGoalState(estado_ini):
            return []
        
    while not (frontera.isEmpty()) and not encontro: 
        last = frontera.pop()
        if last not in visitados:
            if problem.isGoalState(last): 
                encontro = True
                goal = last
                
            sucesores = problem.getSuccessors(last)
            visitados.append(last) 
            
            for estado, accion, costo in sucesores:
                if estado not in visitados:
                    frontera.push(estado)
                    edge_from[estado] = (last, accion)
            
    if goal == None:
        return []
    
    while goal != estado_ini:
        padre, accion = edge_from[goal]
        lista_acciones.append(accion)
        goal = padre
          
    lista_acciones.reverse() 
    return lista_acciones


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

    frontera = PriorityQueue()
    visitados = []
    estado_ini = problem.getStartState()
    lista_acciones = []
    costo_a_nodo = {}
    edge_from = {}
    goal = None
    encontro = False
    
    costo_a_nodo[estado_ini] = 0
    frontera.push(estado_ini,0)
    if problem.isGoalState(estado_ini):
            return []
        
    while not frontera.isEmpty() and not encontro:
        last = frontera.pop()
        if last not in visitados:
            if problem.isGoalState(last): 
                encontro = True
                goal = last
                
            visitados.append(last)    
            sucesores = problem.getSuccessors(last)
            
            for estado, accion, costo in sucesores:
                costo_acumulado = costo + costo_a_nodo[last]
                if estado not in costo_a_nodo or costo_acumulado < costo_a_nodo[estado]:
                    costo_a_nodo[estado] = costo_acumulado
                    frontera.update(estado, costo_acumulado)
                    edge_from[estado] = (last, accion)
                    
    if goal == None:
        return []
    
    while goal != estado_ini:
        padre, accion = edge_from[goal]
        lista_acciones.append(accion)
        goal = padre
          
    lista_acciones.reverse() 
    return lista_acciones


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
