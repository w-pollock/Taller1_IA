from world.game import GameStateData
from world.rescue_rules import RescueRules


class RescueState:
    """
    A RescueState specifies the full state of the rescue mission:
    - Rescuer position
    - Survivors remaining
    - Terrain layout
    """

    def __init__(self, prevState=None):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState is not None:
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy(self):
        state = RescueState(self)
        state.data = self.data.deepCopy()
        return state

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        return hasattr(other, "data") and self.data == other.data

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        return hash(self.data)

    def __str__(self):
        return str(self.data)

    def initialize(self, layout):
        """
        Creates an initial mission state from a layout.
        """
        self.data.initialize(layout)

    def getLegalActions(self):
        """
        Returns the legal actions for the rescuer.
        """
        if self.isWin() or self.isLose():
            return []

        # Get legal moves based on walls
        return RescueRules.getLegalActions(self)

    def generateSuccessor(self, action):
        """
        Returns the successor state after the rescuer takes the action.
        """
        if self.isWin() or self.isLose():
            raise Exception("Can't generate a successor of a terminal state.")

        # Copy current state
        state = RescueState(self)

        # Apply action
        RescueRules.applyAction(state, action)

        # Update cumulative cost (terrain cost of the cell we moved to)
        x, y = state.getRescuerPosition()
        state.data.cumulativeCost += state.data.layout.getTerrainCost(x, y)

        return state

    def getRescuerState(self):
        """
        Returns an AgentState object for the rescuer.
        """
        return self.data.agentStates[0].copy()

    def getRescuerPosition(self):
        """
        Returns the (x, y) position of the rescuer.
        """
        return self.data.agentStates[0].getPosition()

    def getNumAgents(self):
        return len(self.data.agentStates)

    def getSurvivors(self):
        """
        Returns a Grid of boolean survivor indicators.

        Access via: survivors[x][y] == True means survivor at (x,y)
        """
        return self.data.survivors

    def getSurvivorsAsList(self):
        """
        Returns a list of (x, y) positions where survivors are located.
        """
        return self.data.survivors.asList()

    def getNumSurvivors(self):
        """
        Returns the number of remaining survivors.
        """
        return self.data.survivors.count()

    def getWalls(self):
        """
        Returns a Grid of boolean wall indicators.
        """
        return self.data.layout.walls

    def hasSurvivor(self, x, y):
        """
        Returns True if there's a survivor at (x, y).
        """
        return self.data.survivors[x][y]

    def hasWall(self, x, y):
        """
        Returns True if there's a wall at (x, y).
        """
        return self.data.layout.walls[x][y]

    def isLose(self):
        """
        Mission failed (not used in basic search).
        """
        return self.data._lose

    def isWin(self):
        """
        Mission complete (all survivors rescued).
        """
        return self.data._win

    def getTerrain(self, x, y):
        """
        Returns the terrain type at position (x, y).

        Terrain types:
        - ' ' or '.': Normal floor
        - '~': Water
        - '^': Rubble
        - '*': Fire
        """
        return self.data.layout.getTerrain(x, y)

    def getTerrainCost(self, x, y):
        """
        Returns the movement cost for position (x, y).

        Costs:
        - Normal floor: 1
        - Water: 2
        - Rubble: 3
        - Fire: 5
        """
        return self.data.layout.getTerrainCost(x, y)
