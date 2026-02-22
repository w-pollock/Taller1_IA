from world.game import Actions
from algorithms.utils import nearestPoint


class RescueRules:
    """
    These rules manage how the rescuer interacts with the environment.
    """

    RESCUER_SPEED = 1

    @staticmethod
    def getLegalActions(state):
        """
        Returns a list of possible actions.
        """
        return Actions.getPossibleActions(
            state.getRescuerState().configuration, state.data.layout.walls
        )

    @staticmethod
    def applyAction(state, action):
        """
        Edits the state to reflect the results of the action.
        """
        legal = RescueRules.getLegalActions(state)
        if action not in legal:
            raise Exception("Illegal action " + str(action))

        rescuerState = state.data.agentStates[0]

        # Update Configuration
        vector = Actions.directionToVector(action, RescueRules.RESCUER_SPEED)
        rescuerState.configuration = rescuerState.configuration.generateSuccessor(
            vector
        )

        # Rescue survivor if present
        next_pos = rescuerState.configuration.getPosition()
        nearest = nearestPoint(next_pos)
        if abs(nearest[0] - next_pos[0]) + abs(nearest[1] - next_pos[1]) <= 0.5:
            RescueRules.rescue(nearest, state)

    @staticmethod
    def rescue(position, state):
        """
        Rescue a survivor at the given position.
        """
        x, y = position

        # Rescue survivor if present
        if state.data.survivors[x][y]:
            state.data.rescuedCount += 1
            state.data.survivorsSaved = (x, y)
            state.data.survivors = state.data.survivors.copy()
            state.data.survivors[x][y] = False

            # Check if mission complete
            numSurvivors = state.getNumSurvivors()
            if numSurvivors == 0 and not state.data._lose:
                state.data._win = True
