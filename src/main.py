from mainloop import run_loop
from port_cmds import register_port_cmds
from names import NameGenerator, PlaceGenerator
from status_cmds import register_status_cmds, show_status
from nav_cmds import register_nav_cmds
from state import gs, MAP_WIDTH, MAP_HEIGHT
import setup
import map
from command import CommandSystem, RunType, Command
from help import register_info_cmds
from cargo import cargo_types, CARGO_GRAIN
from save import save_file_exists, load_game, save_game
from player import Player
from ship import Ship


# registered quit command
def cmd_quit(run_type, toks):
    if run_type is RunType.CHECK_AVAILABLE:
        return True
    if run_type is RunType.HELP:
        gs.output("Sometimes you gotta quit. When you quit, your progress will be saved for next time.")
        return
    gs.quitting = gs.gm_confirm()
    if gs.quitting:
        err = save_game()
        if err:
            gs.gm_output(f"Error saving game: {err}")
            if not gs.confirm("Do you want to quit anyway?"):
                gs.quitting = False


##################################################################

# initialize our global obj (due to circular refs issue)
gs.player = Player()
gs.ship = Ship()

# see if a save game exists
cont = True
game_loaded = False
if save_file_exists():
    p = gs.confirm("Found a saved game. Do you want to load it?", True)
    if p is None:
        exit(0)
    if p:
        err = load_game()
        if err:
            gs.output(f"Error loading game: {err}")
            cont = False
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

    gs.cmdsys.register(Command("!", "Quit the game", cmd_quit,
                               "This will end the game."))

    # register other commands
    register_info_cmds()
    register_status_cmds()
    register_port_cmds()
    register_nav_cmds()

    # place player at 0 location
    setup.set_player_start_location()

    # show initial status
    show_status(RunType.RUN, [])


    # start the play loop
    run_loop()
