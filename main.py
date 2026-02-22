import world.rescue_layout as rescue_layout
import sys
import time
import pickle
from optparse import OptionParser
from world.rescue_mission import RescueMission


def readCommand(argv):
    """
    Processes the command used to run main from the command line.
    """

    usageStr = """
    USAGE:      python main.py -p PROBLEM -f FUNCTION -l LAYOUT_FILE [options]
    EXAMPLE:    python main.py -p SimpleSurvivorProblem -f tinyHouseSearch -l tinyHouse
                    - starts a mission on the tinyHouse layout (1 survivor) with SimpleSurvivorProblem and tinyHouseSearch.
    """
    parser = OptionParser(usageStr, add_help_option=False)
    parser.add_option(
        "--help",
        action="help",
        help="Show this message and exit",
    )

    PROBLEM_CHOICES = (
        "SimpleSurvivorProblem",
        "MultiSurvivorProblem",
    )
    parser.add_option(
        "-p",
        "--problem",
        dest="problem",
        help="Problem type (required). One of: %s" % ", ".join(PROBLEM_CHOICES),
        metavar="PROBLEM",
    )
    parser.add_option(
        "-f",
        "--function",
        dest="function",
        help="Search function name (required). e.g. tinyHouseSearch, breadthFirstSearch, aStarSearch",
        metavar="FUNCTION",
    )
    parser.add_option(
        "-h",
        "--heuristic",
        dest="heuristic",
        help=default("Heuristic function name (for A*). e.g. nullHeuristic, manhattanHeuristic"),
        metavar="HEURISTIC",
        default="nullHeuristic",
    )
    parser.add_option(
        "-l",
        "--layout",
        dest="layout",
        help="Layout file to load (required)",
        metavar="LAYOUT_FILE",
    )
    parser.add_option(
        "-t",
        "--textGraphics",
        action="store_true",
        dest="textGraphics",
        help="Display output as text only",
        default=False,
    )
    parser.add_option(
        "-q",
        "--quietTextGraphics",
        action="store_true",
        dest="quietGraphics",
        help="Generate minimal output and no graphics",
        default=False,
    )
    parser.add_option(
        "-z",
        "--zoom",
        type="float",
        dest="zoom",
        help=default("Zoom the size of the graphics window"),
        default=1.0,
    )
    parser.add_option(
        "-r",
        "--recordActions",
        action="store_true",
        dest="record",
        help="Writes mission histories to a file",
        default=False,
    )
    parser.add_option(
        "-x",
        "--frameTime",
        dest="frameTime",
        type="float",
        help=default("Time to delay between frames; <0 means keyboard"),
        default=0.1,
    )
    parser.add_option(
        "-c",
        "--catchExceptions",
        action="store_true",
        dest="catchExceptions",
        help="Turns on exception handling during missions",
        default=False,
    )

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception("Command line input not understood: " + str(otherjunk))

    if not options.problem:
        parser.error("-p/--problem is required. Choose one of: %s" % ", ".join(PROBLEM_CHOICES))
    if options.problem not in PROBLEM_CHOICES:
        parser.error(
            "Invalid problem type '%s'. Choose one of: %s"
            % (options.problem, ", ".join(PROBLEM_CHOICES))
        )
    if not options.function:
        parser.error("-f/--function is required")
    if not options.layout:
        parser.error("-l/--layout is required")

    args = dict()

    # Choose a layout
    args["layout"] = rescue_layout.getLayout(options.layout)
    if args["layout"] is None:
        raise Exception("The layout " + options.layout + " cannot be found")

    print("AgentPositions:", args["layout"].agentPositions)
    print("Survivors:", args["layout"].survivors.asList())
    print("NumSurvivors:", len(args["layout"].survivors.asList()))

    # Choose a rescue agent
    rescuerType = loadAgent("SearchAgent")
    rescuer = rescuerType(
        fn=options.function,
        prob=options.problem,
        heuristic=options.heuristic,
    )
    args["rescuer"] = rescuer

    # Choose a display format
    if options.quietGraphics:
        import view.text_display as text_display

        args["display"] = text_display.NullGraphics()
    elif options.textGraphics:
        import view.text_display as text_display

        text_display.SLEEP_TIME = options.frameTime
        args["display"] = text_display.RescueGraphics()
    else:
        import view.graphics_display as graphics_display

        args["display"] = graphics_display.RescueGraphics(
            options.zoom, frameTime=options.frameTime
        )

    args["record"] = options.record
    args["catchExceptions"] = options.catchExceptions

    return args


def default(str_val):
    return str_val + " [Default: %default]"


def loadAgent(rescuer):
    """
    Looks through algorithms/agents.py for the right agent.
    """
    try:
        module = __import__("algorithms.agents", fromlist=[rescuer])
    except ImportError:
        raise Exception("The agents module could not be imported.")

    if rescuer in dir(module):
        return getattr(module, rescuer)

    raise Exception(
        "The agent " + rescuer + " is not specified in algorithms/agents.py."
    )


def runMission(layout, rescuer, display, record, catchExceptions=False):
    """
    Run rescue missions.
    """
    import __main__

    __main__.__dict__["_display"] = display

    rescueMission = RescueMission()

    episode = rescueMission.newMission(layout, rescuer, display, False, catchExceptions)
    episode.run()

    if record:
        fname = ("recorded-episode") + "-".join(
            [str(t) for t in time.localtime()[1:6]]
        )
        f = open(fname, "wb")
        components = {"layout": layout, "actions": episode.moveHistory}
        pickle.dump(components, f)
        f.close()

    return episode


if __name__ == "__main__":
    """
    The main function is called when main.py is run from the command line.
    """
    args = readCommand(sys.argv[1:])
    runMission(**args)
