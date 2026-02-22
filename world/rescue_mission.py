from world.game import Game
from world.rescue_state import RescueState


class RescueMission:
    """
    These rules manage the control flow of the rescue mission.
    """

    def newMission(self, layout, rescueAgent, display, quiet=False, catchExceptions=False):
        """
        Create a new rescue mission.
        """
        agents = [rescueAgent]
        initState = RescueState()
        initState.initialize(layout)

        print("Survivors:", initState.getSurvivorsAsList())
        print("NumSurvivors:", initState.getNumSurvivors())

        mission = Game(agents, display, self, catchExceptions=catchExceptions)
        mission.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return mission

    def process(self, state, mission):
        """
        Checks to see whether it is time to end the mission.
        """
        if state.isWin():
            self.win(state, mission)
        if state.isLose():
            self.lose(state, mission)

    def win(self, state, mission):
        if not self.quiet:
            print("All survivors rescued! Cost: %d" % state.data.cumulativeCost)
        mission.gameOver = True

    def lose(self, state, mission):
        if not self.quiet:
            print("Mission failed! Cost: %d" % state.data.cumulativeCost)
        mission.gameOver = True

    def getProgress(self, mission):
        return float(mission.state.getNumSurvivors()) / self.initialState.getNumSurvivors()
