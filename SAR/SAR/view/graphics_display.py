from view.graphics_utils import (
    refresh,
    formatColor,
    text,
    line,
    square,
    circle,
    remove_from_screen,
    begin_graphics,
    begin_graphics_scrollable,
    end_graphics,
    sleep,
    wait_for_keys,
    changeText,
    edit,
)
from world.game import Directions

# ========================================
# CHANGES TO LAYOUT
# ========================================

DEFAULT_GRID_SIZE = 30.0
INFO_PANE_HEIGHT = 52
INFO_PANE_PADDING = 12
MAX_WINDOW_WIDTH = 1400
MAX_WINDOW_HEIGHT = 900
VIEWPORT_MAX_WIDTH = 1280
VIEWPORT_MAX_HEIGHT = 720

# Environment (disaster area)
BACKGROUND_COLOR = formatColor(0.93, 0.93, 0.93)  # Light gray concrete floor
GRID_LINE_COLOR = formatColor(0.85, 0.85, 0.85)  # Subtle grid lines

# Walls/Buildings (concrete/debris)
WALL_FILL = formatColor(0.40, 0.40, 0.40)  # Dark gray concrete
WALL_OUTLINE = formatColor(0.20, 0.20, 0.20)  # Almost black outline
WALL_CRACK = formatColor(0.50, 0.35, 0.25)  # Brown damage marks

# Terrain (hazards)
WATER_BASE = formatColor(0.29, 0.56, 0.89)  # Clear blue water
WATER_WAVE = formatColor(0.50, 0.70, 0.95)  # Lighter blue waves
WATER_TEXT = formatColor(1.0, 1.0, 1.0)  # White cost label

RUBBLE_BASE = formatColor(0.54, 0.45, 0.33)  # Brown rubble
RUBBLE_ROCK = formatColor(0.65, 0.55, 0.40)  # Lighter rocks
RUBBLE_TEXT = formatColor(1.0, 1.0, 1.0)  # White cost label

FIRE_CORE = formatColor(1.0, 0.42, 0.21)  # Orange-red core
FIRE_GLOW = formatColor(0.97, 0.65, 0.30)  # Yellow-orange glow
FIRE_TEXT = formatColor(0.1, 0.1, 0.1)  # Dark cost label

# Critical Elements (survivors)
SURVIVOR_FILL = formatColor(1.0, 0.75, 0.0)  # Bright yellow-orange
SURVIVOR_OUTLINE = formatColor(0.85, 0.45, 0.0)  # Darker orange outline
SURVIVOR_TEXT = formatColor(0.1, 0.1, 0.1)  # Dark "SOS" text
RESCUED_FILL = formatColor(0.3, 0.8, 0.3)  # Green (rescued)
RESCUED_OUTLINE = formatColor(0.2, 0.6, 0.2)  # Darker green outline
RESCUED_TEXT = formatColor(0.1, 0.1, 0.1)  # Dark "OK" text

# Robot (professional rescue unit)
ROBOT_BODY = formatColor(0.25, 0.35, 0.50)  # Navy blue body
ROBOT_ACCENT = formatColor(0.35, 0.55, 0.75)  # Light blue accents
ROBOT_SENSOR = formatColor(0.0, 0.85, 0.30)  # Bright green sensors
ROBOT_OUTLINE = formatColor(0.1, 0.1, 0.1)  # Dark outline

# Info Pane
COST_COLOR = formatColor(0.2, 0.2, 0.2)  # Dark gray text
TITLE_COLOR = formatColor(0.3, 0.3, 0.3)  # Medium gray
SURVIVOR_COUNT_COLOR = formatColor(0.85, 0.45, 0.0)  # Orange (matches survivors)


# ========================================
# INFO PANE
# ========================================


class InfoPane:
    def __init__(self, layout, gridSize):
        self.gridSize = gridSize
        self.width = layout.width * gridSize
        self.base = (layout.height + 1) * gridSize

        # Responsive font sizing based on width
        if self.width < 300:
            self.fontSize = 14
            self.titleSize = 10
        elif self.width < 500:
            self.fontSize = 16
            self.titleSize = 11
        else:
            self.fontSize = 18
            self.titleSize = 12

        self.drawPane(layout)

    def toScreen(self, x, y):
        return (self.gridSize + x, self.base + y)

    def drawPane(self, layout):
        # Title - centered, with vertical padding
        titleX = self.width // 2
        self.titleText = text(
            self.toScreen(titleX, 4),
            TITLE_COLOR,
            "SAR MISSION",
            "Arial",
            self.titleSize,
            "bold",
            anchor="n",  # North anchor (centered at top)
        )

        # Cost - left side with padding
        self.costText = text(
            self.toScreen(INFO_PANE_PADDING, 24),
            COST_COLOR,
            "COST: 0",
            "Arial",
            self.fontSize,
            "bold",
            anchor="nw",
        )

        # Rescued count - right side with padding
        total_survivors = layout.totalSurvivors
        self.survivorText = text(
            self.toScreen(self.width - INFO_PANE_PADDING, 24),
            SURVIVOR_COUNT_COLOR,
            f"RESCUED: 0/{total_survivors}",
            "Arial",
            self.fontSize,
            "bold",
            anchor="ne",  # Northeast anchor (right-aligned)
        )

    def updateCost(self, cost):
        changeText(self.costText, f"COST: {cost}")

    def updateRescued(self, rescued, total):
        changeText(self.survivorText, f"RESCUED: {rescued}/{total}")


# ========================================
# MAIN GRAPHICS CLASS
# ========================================


class RescueGraphics:
    def __init__(self, zoom=1.0, frameTime=0.0, capture=False):
        self.zoom = zoom
        self.gridSize = DEFAULT_GRID_SIZE * zoom
        self.frameTime = frameTime
        self.capture = capture
        self._step_mode_message_shown = False

        self.gridLines = []
        self.terrainTiles = []
        self.terrainLabels = []
        self.survivorImages = None
        self.agentImages = []
        self.totalSurvivors = 0

    def initialize(self, state, isBlue=False):
        """
        Initialize display with mission state.
        """
        self.layout = state.layout
        self.width = self.layout.width
        self.height = self.layout.height
        self.totalSurvivors = self.layout.totalSurvivors

        # Use scroll when content exceeds viewport safe size; otherwise scale down so it fits
        screen_width = 2 * self.gridSize + (self.width - 1) * self.gridSize
        screen_height = 2 * self.gridSize + (self.height - 1) * self.gridSize + INFO_PANE_HEIGHT
        self._use_scroll = (
            screen_width > VIEWPORT_MAX_WIDTH or screen_height > VIEWPORT_MAX_HEIGHT
        )
        if self._use_scroll:
            # Keep full resolution; viewport will have scrollbars
            self._content_width = int(screen_width)
            self._content_height = int(screen_height)
        else:
            # Scale down to fit
            if screen_width > MAX_WINDOW_WIDTH or screen_height > MAX_WINDOW_HEIGHT:
                scale = min(MAX_WINDOW_WIDTH / screen_width, MAX_WINDOW_HEIGHT / screen_height)
                self.gridSize *= scale
                screen_width = 2 * self.gridSize + (self.width - 1) * self.gridSize
                screen_height = 2 * self.gridSize + (self.height - 1) * self.gridSize + INFO_PANE_HEIGHT
            self._content_width = int(screen_width)
            self._content_height = int(screen_height)

        self._make_window()
        self.infoPane = InfoPane(self.layout, self.gridSize)

        self._drawStatic(state)
        self._drawAgents(state)
        self.previousState = state

    def finish(self):
        end_graphics()

    # ========================================
    # WINDOW SETUP
    # ========================================

    def _make_window(self):
        """
        Create window with professional styling. Uses scroll when content is large.
        """
        if getattr(self, "_use_scroll", False):
            viewport_w = min(VIEWPORT_MAX_WIDTH, self._content_width)
            viewport_h = min(VIEWPORT_MAX_HEIGHT, self._content_height)
            begin_graphics_scrollable(
                viewport_w,
                viewport_h,
                self._content_width,
                self._content_height,
                BACKGROUND_COLOR,
                "SAR Mission Control",
            )
        else:
            begin_graphics(
                self._content_width,
                self._content_height,
                BACKGROUND_COLOR,
                "SAR Mission Control",
            )

    def to_screen(self, point):
        """
        Convert grid coordinates to screen coordinates.
        """
        x, y = point
        x = (x + 1) * self.gridSize
        y = (self.height - y) * self.gridSize
        return (x, y)

    # ========================================
    # STATIC ELEMENTS
    # ========================================

    def _drawStatic(self, state):
        """
        Draw all static elements (background, walls, terrain, survivors).
        """
        # 1. Background grid
        self._drawBackgroundGrid()

        # 2. Terrain
        self._drawTerrain(state)

        # 3. Walls
        self._drawWalls(state.layout.walls)

        # 4. Survivors
        self.survivorImages = self._drawSurvivors(state.survivors)

        refresh()

    def _drawBackgroundGrid(self):
        """
        Draw subtle grid lines for spatial reference.
        """
        for x in range(self.width + 1):
            x_screen = (x + 1) * self.gridSize
            line_obj = line(
                (x_screen, self.gridSize),
                (x_screen, (self.height + 1) * self.gridSize),
                GRID_LINE_COLOR,
                width=1,
            )
            self.gridLines.append(line_obj)

        for y in range(self.height + 1):
            y_screen = (self.height - y + 1) * self.gridSize
            line_obj = line(
                (self.gridSize, y_screen),
                ((self.width + 1) * self.gridSize, y_screen),
                GRID_LINE_COLOR,
                width=1,
            )
            self.gridLines.append(line_obj)

    def _drawWalls(self, wallMatrix):
        """
        Draw walls as simple solid blocks (NO rounding).
        Realistic building debris aesthetic.
        """
        for x in range(wallMatrix.width):
            for y in range(wallMatrix.height):
                if not wallMatrix[x][y]:
                    continue

                screen = self.to_screen((x, y))

                # Main wall block (dark gray)
                square(screen, 0.48 * self.gridSize, color=WALL_FILL, filled=1)

                # Outline for depth
                square(
                    screen, 0.48 * self.gridSize, color=WALL_OUTLINE, filled=0, behind=0
                )

    def _drawTerrain(self, state):
        """
        Draw terrain with realistic styling.
        """
        # Clear old terrain
        for obj in self.terrainTiles + self.terrainLabels:
            remove_from_screen(obj)
        self.terrainTiles = []
        self.terrainLabels = []

        layout = state.layout
        walls = layout.walls

        for x in range(walls.width):
            for y in range(walls.height):
                if walls[x][y]:
                    continue

                terrain_char = (
                    layout.getTerrain(x, y) if hasattr(layout, "getTerrain") else "."
                )

                if terrain_char == "~":
                    self._drawWater(x, y)
                elif terrain_char == "^":
                    self._drawRubble(x, y)
                elif terrain_char == "*":
                    self._drawFire(x, y)

    def _drawWater(self, x, y):
        """
        Draw water with wave pattern.
        """
        screen = self.to_screen((x, y))

        # Base water square
        tile = square(screen, 0.5 * self.gridSize, color=WATER_BASE, filled=1)
        self.terrainTiles.append(tile)

        # Wave lines (simple horizontal lines)
        wave1 = line(
            (screen[0] - 0.35 * self.gridSize, screen[1] - 0.15 * self.gridSize),
            (screen[0] + 0.35 * self.gridSize, screen[1] - 0.15 * self.gridSize),
            WATER_WAVE,
            width=2,
        )
        wave2 = line(
            (screen[0] - 0.35 * self.gridSize, screen[1] + 0.15 * self.gridSize),
            (screen[0] + 0.35 * self.gridSize, screen[1] + 0.15 * self.gridSize),
            WATER_WAVE,
            width=2,
        )
        self.terrainTiles.extend([wave1, wave2])

        # Cost label
        label = text(screen, WATER_TEXT, "2", "Arial", 14, "bold")
        self.terrainLabels.append(label)

    def _drawRubble(self, x, y):
        """
        Draw rubble with rock texture.
        """
        screen = self.to_screen((x, y))

        # Base rubble square
        tile = square(screen, 0.5 * self.gridSize, color=RUBBLE_BASE, filled=1)
        self.terrainTiles.append(tile)

        # Add small rocks for texture (4-6 small circles)
        import random

        random.seed(x * 1000 + y)  # Deterministic randomness
        for _ in range(5):
            rock_x = screen[0] + random.randint(-12, 12)
            rock_y = screen[1] + random.randint(-12, 12)
            rock_size = random.randint(2, 5)
            rock = circle((rock_x, rock_y), rock_size, RUBBLE_ROCK, RUBBLE_ROCK)
            self.terrainTiles.append(rock)

        # Cost label
        label = text(screen, RUBBLE_TEXT, "3", "Arial", 14, "bold")
        self.terrainLabels.append(label)

    def _drawFire(self, x, y):
        """
        Draw fire with glow effect.
        """
        screen = self.to_screen((x, y))

        # Outer glow
        glow = circle(screen, 0.45 * self.gridSize, FIRE_GLOW, FIRE_GLOW)
        self.terrainTiles.append(glow)

        # Inner core
        core = circle(screen, 0.30 * self.gridSize, FIRE_CORE, FIRE_CORE)
        self.terrainTiles.append(core)

        # Cost label (dark text for visibility on bright fire)
        label = text(screen, FIRE_TEXT, "5", "Arial", 16, "bold")
        self.terrainLabels.append(label)

    def _drawSurvivors(self, survivorsMatrix):
        """
        Draw survivors with high visibility (bright yellow/orange).
        """
        images = []
        for x, col in enumerate(survivorsMatrix):
            rowImgs = []
            images.append(rowImgs)
            for y, hasSurvivor in enumerate(col):
                if hasSurvivor:
                    screen = self.to_screen((x, y))

                    # Outer glow for attention
                    glow = circle(
                        screen, 0.32 * self.gridSize, SURVIVOR_OUTLINE, SURVIVOR_OUTLINE
                    )

                    # Inner bright circle
                    inner = circle(
                        screen, 0.26 * self.gridSize, SURVIVOR_FILL, SURVIVOR_FILL
                    )

                    # "SOS" text
                    label = text(screen, SURVIVOR_TEXT, "SOS", "Arial", 11, "bold")

                    rowImgs.append([glow, inner, label])
                else:
                    rowImgs.append(None)
        return images

    def _markRescued(self, cell):
        """
        Change survivor color to green when rescued (glow, inner circle, text to OK).
        """
        if cell is None or self.survivorImages is None:
            return
        x, y = cell
        if x >= len(self.survivorImages) or y >= len(self.survivorImages[x]):
            return
        img = self.survivorImages[x][y]
        if img is None:
            return
        # img is [glow, inner, label]
        glow, inner, label = img
        edit(glow, ("fill", RESCUED_OUTLINE), ("outline", RESCUED_OUTLINE))
        edit(inner, ("fill", RESCUED_FILL), ("outline", RESCUED_FILL))
        changeText(label, "OK")

    # ========================================
    # ROBOT AGENT
    # ========================================

    def _drawAgents(self, state):
        """
        Draw all agents (typically just one robot).
        """
        self.agentImages = []
        for _, agentState in enumerate(state.agentStates):
            parts = self._drawRobot(agentState)
            self.agentImages.append((agentState, parts))
        refresh()

    def _getPos(self, agentState):
        if agentState.configuration is None:
            return (-1000, -1000)
        return agentState.getPosition()

    def _getDir(self, agentState):
        if agentState.configuration is None:
            return Directions.STOP
        return agentState.configuration.getDirection()

    def _drawRobot(self, agentState):
        """
        Draw robot as professional rescue unit.
        Wrapper that extracts position/direction from agentState.
        """
        pos = self._getPos(agentState)
        dirn = self._getDir(agentState)
        return self._drawRobotAtPosition(pos, dirn)

    def _drawRobotAtPosition(self, pos, dirn):
        """
        Draw robot at specific position and direction.
        - Compact body with rounded corners
        - Directional sensor array
        - Status indicator
        """
        screen = self.to_screen(pos)
        parts = []

        # Main body (rounded square)
        body = square(screen, 0.36 * self.gridSize, color=ROBOT_BODY, filled=1)
        parts.append(body)

        # Body outline
        outline = square(
            screen, 0.36 * self.gridSize, color=ROBOT_OUTLINE, filled=0, behind=0
        )
        parts.append(outline)

        # Accent stripe
        accent = square(
            (screen[0] - 0.08 * self.gridSize, screen[1] - 0.08 * self.gridSize),
            0.18 * self.gridSize,
            color=ROBOT_ACCENT,
            filled=1,
        )
        parts.append(accent)

        # Directional sensors (3 dots pointing in movement direction)
        sensors = self._getSensorPositions(screen, dirn)
        for sx, sy in sensors:
            sensor = circle((sx, sy), 0.05 * self.gridSize, ROBOT_SENSOR, ROBOT_SENSOR)
            parts.append(sensor)

        # Status light (center top)
        status = circle(
            (screen[0], screen[1] - 0.24 * self.gridSize),
            0.04 * self.gridSize,
            ROBOT_SENSOR,
            ROBOT_SENSOR,
        )
        parts.append(status)

        return parts

    def _getSensorPositions(self, center, direction):
        """
        Calculate sensor positions based on robot direction.
        """
        cx, cy = center
        offset = 0.40 * self.gridSize
        side = 0.12 * self.gridSize

        if direction == Directions.NORTH:
            return [
                (cx, cy - offset),
                (cx - side, cy - offset * 0.75),
                (cx + side, cy - offset * 0.75),
            ]
        elif direction == Directions.SOUTH:
            return [
                (cx, cy + offset),
                (cx - side, cy + offset * 0.75),
                (cx + side, cy + offset * 0.75),
            ]
        elif direction == Directions.WEST:
            return [
                (cx - offset, cy),
                (cx - offset * 0.75, cy - side),
                (cx - offset * 0.75, cy + side),
            ]
        else:  # EAST
            return [
                (cx + offset, cy),
                (cx + offset * 0.75, cy - side),
                (cx + offset * 0.75, cy + side),
            ]

    def _moveRobot(self, pos, dirn, parts):
        """
        Move robot by redrawing (simple and clean).
        """
        # Remove old parts
        for p in parts:
            remove_from_screen(p)

        # Redraw at new position
        newParts = self._drawRobotAtPosition(pos, dirn)
        parts[:] = newParts  # Update list in place
        refresh()

    # ========================================
    # UPDATE LOOP
    # ========================================

    def update(self, newState):
        """
        Update display with new mission state.
        """
        agentIndex = getattr(newState, "_agentMoved", 0)
        if agentIndex is None:
            agentIndex = 0

        # Update robot position
        agentState = newState.agentStates[agentIndex]
        _, parts = self.agentImages[agentIndex]
        self._moveRobot(self._getPos(agentState), self._getDir(agentState), parts)
        self.agentImages[agentIndex] = (agentState, parts)

        # Update survivors (if one was rescued - change color instead of removing)
        if getattr(newState, "survivorsSaved", None) is not None:
            self._markRescued(newState.survivorsSaved)

        # Update info pane
        cost = getattr(newState, "cumulativeCost", 0)
        self.infoPane.updateCost(cost)
        rescued = getattr(newState, "rescuedCount", 0)
        self.infoPane.updateRescued(rescued, self.totalSurvivors)

        refresh()
        if self.frameTime < 0:
            if not self._step_mode_message_shown:
                print("STEP-BY-STEP MODE: press any key in the graphics window to advance.")
                self._step_mode_message_shown = True
            wait_for_keys()
        else:
            sleep(self.frameTime)


# ========================================
# UTILITY FUNCTIONS
# ========================================


def add(x, y):
    """Add two coordinate tuples."""
    return (x[0] + y[0], x[1] + y[1])
