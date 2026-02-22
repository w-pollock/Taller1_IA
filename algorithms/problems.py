from algorithms import utils
from world.game import Directions, Actions
from world.rescue_state import RescueState


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        utils.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        utils.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        utils.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        utils.raiseNotDefined()


class SimpleSurvivorProblem(SearchProblem):
    """
    Find a single survivor with an emergency beacon. 
    
    State: (x, y) position. 
    Goal: survivor cell.
    Terrain costs apply by default.
    """

    def __init__(
        self,
        rescueState,
        costFn=None,
        goal=(1, 1),
        start=None,
        warn=True,
        visualize=True,
    ):
        """
        rescueState: RescueState
        costFn: function (x,y)->cost; if None, uses rescueState.getTerrainCost (terrain-aware)
        goal: fallback goal if survivor auto-detect isn't possible
        start: optional override for start position
        warn: print warnings if map doesn't match expectations
        visualize: enable visited bookkeeping for display/stats
        """

        self.walls = rescueState.getWalls()

        # Start state (rescuer position unless overridden)
        self.startState = rescueState.getRescuerPosition()
        if start is not None:
            self.startState = start

        # --- AUTO-DETECT GOAL FROM SURVIVORS ---
        survivors = rescueState.getSurvivorsAsList()

        if len(survivors) == 1:
            # This is a normal "beacon" case: exactly one survivor on map
            self.goal = survivors[0]
        else:
            # Fallback to provided goal (default (1,1))
            self.goal = goal
            if warn:
                if len(survivors) == 0:
                    print(
                        "Warning: no survivors found on the map; using goal=%s"
                        % (str(self.goal),)
                    )
                else:
                    print(
                        "Warning: %d survivors found; using goal=%s (consider a different problem type)"
                        % (len(survivors), str(self.goal))
                    )

        # Use terrain cost from rescue state so search cost matches game cumulative cost
        if costFn is None:
            costFn = lambda pos: rescueState.getTerrainCost(pos[0], pos[1])
        self.costFn = costFn
        self.visualize = visualize

        # Optional sanity warning: goal should contain a survivor in the single-survivor case
        # (If you put the survivor elsewhere or you're using a beacon-cell idea, you may want warn=False)
        if warn and len(survivors) == 1 and not rescueState.hasSurvivor(*self.goal):
            print(
                "Warning: expected survivor at goal=%s, but none found"
                % (str(self.goal),)
            )

        # For visualization/statistics
        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # For visualization: mark nodes as visited
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__

            if "_display" in dir(__main__):
                if "drawExpandedCells" in dir(__main__._display):
                    __main__._display.drawExpandedCells(self._visitedlist)

        return isGoal

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost.

        For a given state, this returns a list of triples:
        (successor, action, stepCost)

        This is where terrain costs come into play via costFn.
        """
        successors = []
        for action in [
            Directions.NORTH,
            Directions.SOUTH,
            Directions.EAST,
            Directions.WEST,
        ]:
            x, y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)

            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append((nextState, action, cost))

        # Bookkeeping for display
        self._expanded += 1
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.
        """
        if actions is None:
            return 999999

        x, y = self.getStartState()
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += self.costFn((x, y))
        return cost


class MultiSurvivorProblem(SearchProblem):
    """
    Find a path that rescues all survivors.

    State: (position, survivors_grid)
    - position: (x, y) tuple
    - survivors_grid: Grid of booleans (True = survivor present)

    Goal: All survivors rescued (survivors_grid.count() == 0)
    """

    def __init__(self, startingMissionState: RescueState):
        self.start = (
            startingMissionState.getRescuerPosition(),
            startingMissionState.getSurvivors(),
        )
        self.walls = startingMissionState.getWalls()
        self.startingMissionState = startingMissionState
        self._expanded = 0
        self.heuristicInfo = {}  # For caching heuristic computations

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and the terrain cost of the destination cell.
        """
        successors = []
        self._expanded += 1

        for direction in [
            Directions.NORTH,
            Directions.SOUTH,
            Directions.EAST,
            Directions.WEST,
        ]:
            x, y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)

            if not self.walls[nextx][nexty]:
                nextSurvivors = state[1].copy()
                nextSurvivors[nextx][nexty] = False  # Rescue survivor if present
                stepCost = self.startingMissionState.getTerrainCost(nextx, nexty)
                successors.append((((nextx, nexty), nextSurvivors), direction, stepCost))

        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.
        Uses terrain cost per cell (same as game cumulative cost).
        """
        x, y = self.getStartState()[0]
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += self.startingMissionState.getTerrainCost(x, y)
        return cost
