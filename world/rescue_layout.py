from world.game import Grid
import os


class RescueLayout:
    """
    A RescueLayout manages the static information about the rescue area.
    """

    def __init__(self, layoutText):
        self.width = len(layoutText[0])
        self.height = len(layoutText)
        self.walls = Grid(self.width, self.height, False)
        self.survivors = Grid(self.width, self.height, False)

        self.agentPositions = []
        self.terrain = {}
        self.processLayoutText(layoutText)
        self.layoutText = layoutText
        self.totalSurvivors = len(self.survivors.asList())

    def isWall(self, pos):
        """
        Check if position is a wall.
        """
        x, col = pos
        return self.walls[x][col]

    def getTerrain(self, x, y):
        """
        Get the terrain character at position (x, y).
        Returns the terrain character or '.' for normal floor.
        """
        return self.terrain.get((x, y), ".")

    def getTerrainCost(self, x, y):
        """
        Get the movement cost for terrain at position (x, y).

        Terrain costs:
        - Normal floor (' ' or '.'): 1
        - Water ('~'): 2
        - Rubble ('^'): 3
        - Fire ('*'): 5
        """
        terrain_char = self.getTerrain(x, y)
        TERRAIN_COSTS = {
            ".": 1,  # Normal floor
            " ": 1,  # Empty space
            "~": 2,  # Water
            "^": 3,  # Rubble
            "*": 5,  # Fire
        }
        return TERRAIN_COSTS.get(terrain_char, 1)

    def __str__(self):
        return "\n".join(self.layoutText)

    def deepCopy(self):
        return RescueLayout(self.layoutText[:])

    def processLayoutText(self, layoutText):
        """
        Coordinates are flipped from the input format to the (x,y) convention here

        The shape of the rescue area. Each character represents a different type of object:
         % - Wall/Obstacle (impassable)
         S - Survivor (must be rescued)
         R - Rescuer (starting position)
         . - Normal floor (movement cost 1)
         ~ - Water (movement cost 2)
         ^ - Rubble (movement cost 3)
         * - Fire (movement cost 5)

        Other characters are treated as normal floor (cost 1).
        """
        maxY = self.height - 1
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = layoutText[maxY - y][x]
                self.processLayoutChar(x, y, layoutChar)
        self.agentPositions.sort()

    def processLayoutChar(self, x, y, layoutChar):
        """
        Process a single layout character and update the appropriate data structure.
        """
        # Walls
        if layoutChar == "%":
            self.walls[x][y] = True

        # Survivors
        elif layoutChar == "S":
            self.survivors[x][y] = True

        # Rescuer starting position
        elif layoutChar == "R":
            self.agentPositions.append((x, y))

        # Terrain types for variable movement costs
        elif layoutChar in ["~", "^", "*"]:
            self.terrain[(x, y)] = layoutChar

        # All other characters (including ' ') are treated as normal floor
        # They don't create walls, survivors, or special terrain


def getLayout(name):
    """
    Load a layout file by name.

    Searches recursively inside the layouts/ directory for a matching .lay file.
    """
    filename = name if name.endswith(".lay") else name + ".lay"
    for root, _dirs, files in os.walk("layouts"):
        if filename in files:
            return tryToLoad(os.path.join(root, filename))
    return None


def tryToLoad(fullname):
    """
    Attempt to load a layout from a file.
    Returns None if file doesn't exist.
    """
    if not os.path.exists(fullname):
        return None
    f = open(fullname)
    try:
        return RescueLayout([line.strip() for line in f])
    finally:
        f.close()
