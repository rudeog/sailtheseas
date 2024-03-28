from mainloop import run_loop
from port_cmds import register_port_cmds
from names import NameGenerator, PlaceGenerator
from status_cmds import register_status_cmds, show_status
from nav_cmds import register_nav_cmds
from crew_cmds import register_crew_cmds
from state import gs, MAP_WIDTH, MAP_HEIGHT, GAME_VERSION, GAME_NAME
import setup
import map
from command import CommandSystem, RunType, Command
from help import register_info_cmds
from save import save_file_exists, load_game, save_game, load_trading_and_visited_data
from player import Player
from ship import Ship
from crew import Crew
from stock import Stock


# registered quit command
def cmd_quit(run_type, toks):
    if run_type is RunType.CHECK_AVAILABLE:
        return True
    if run_type is RunType.HELP:
        gs.output("Sometimes you gotta quit. Be sure to save your game at an island before quitting.")
        return
    gs.quitting = True

# todo move this somewhere
def init_trading_data():
    for loc in gs.map.places:
        if loc.island and loc.island.port and loc.island.port.trader:
            t = loc.island.port.trader
            t.update()





##################################################################



# initialize our global obj (due to circular refs issue)
gs.player = Player()
gs.ship = Ship()
gs.crew = Crew()
gs.stock = Stock()

gs.output(f"{GAME_NAME} v{GAME_VERSION}")

# see if a save game exists
cont = True
game_loaded = False
loaded_game_info=None
if save_file_exists():
    p = gs.confirm("Found a saved game. Do you want to load it?", True)
    if p is None:
        exit(0)
    if p:
        loaded_game_info, err = load_game()
        if err:
            gs.output(f"Error loading game: {err}")
            cont = gs.confirm("Start a new game instead?",True)
        else:
            game_loaded = True

if cont and not game_loaded:
    cont = setup.determine_seed()

if cont:
    setup.base_setup()
    # generate the map
    gs.map = map.Map(MAP_WIDTH, MAP_HEIGHT, gs.seed)

    if not game_loaded:
        cont = setup.player_setup()

if cont:
    # set up the command interpreter
    gs.cmdsys = CommandSystem()

    gs.cmdsys.register(Command("!",  cmd_quit,
                               "Quit the game."))

    # register other commands
    register_info_cmds()
    register_status_cmds()
    register_port_cmds()
    register_nav_cmds()
    register_crew_cmds()

    if game_loaded:
        #load trading data now that map is present
        cont = load_trading_and_visited_data(loaded_game_info)

    else:
        # place player at 0 location
        setup.set_player_start_location()
        # initialize trading data
        init_trading_data()

if cont:
    # show initial status
    show_status(RunType.RUN, [])


    # start the play loop
    run_loop()




