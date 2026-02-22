import time
from algorithms.utils import nearestPoint

DRAW_EVERY = 1
SLEEP_TIME = 0
DISPLAY_MOVES = False
QUIET = False


class NullGraphics:
    """
    Null graphics for quiet mode (no visual output).
    Used when running with -q flag.
    """

    def initialize(self, state, isBlue=False):
        pass

    def update(self, state):
        pass

    def checkNullDisplay(self):
        return True

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        print(state)

    def updateDistributions(self, dist):
        pass

    def finish(self):
        pass


class RescueGraphics:
    """
    Text-based graphics for the Search and Rescue domain.
    Displays the rescue area in ASCII format with:
    - % for walls
    - R for rescuer
    - S for survivors
    - Terrain symbols (~, ^, *) for water, rubble, fire
    """

    def __init__(self, speed=None):
        if speed is not None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def initialize(self, state, isBlue=False):
        """
        Initialize the display with the initial rescue state.
        """
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state):
        """
        Update the display after each agent move.
        In SAR, we typically only have one agent (the rescuer).
        """
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        if self.agentCounter == 0:
            self.turn += 1
            if DISPLAY_MOVES:
                # Display rescuer position, cost, and rescued count
                try:
                    rescuer_pos = nearestPoint(state.agentStates[0].getPosition())
                    cost = getattr(state, "cumulativeCost", 0)
                    rescued = getattr(state, "rescuedCount", 0)
                    print(
                        "%4d) R: %-8s" % (self.turn, str(rescuer_pos)),
                        "| Cost: %-5d" % cost,
                        "| Rescued: %d" % rescued,
                    )
                except Exception:
                    # Fallback if rescue module not available
                    cost = getattr(state, "cumulativeCost", 0)
                    print(
                        "%4d) Turn %d | Cost: %d" % (self.turn, self.turn, cost)
                    )
            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                self.pause()
        if state._win or state._lose:
            self.draw(state)

    def pause(self):
        """
        Pause between display updates.
        """
        if SLEEP_TIME < 0:
            input("Press Enter to continue...")
        else:
            time.sleep(SLEEP_TIME)

    def draw(self, state):
        """
        Draw the current state to the console.
        Uses the state's __str__ method which displays:
        - Walls as %
        - Survivors as S
        - Rescuer position as R
        - Cost at the bottom
        """
        print(state)

    def finish(self):
        """
        Called when the mission ends.
        """
        pass
