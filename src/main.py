import argparse

import debug
from mainloop import run_loop
from port_cmds import register_port_cmds
from names import NameGenerator, PlaceGenerator
from wind import Wind
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
from hints import cmd_hints, Hints
from quest import cmd_quests


import logging

# registered quit command
def cmd_quit(run_type, toks):
    if run_type is RunType.CHECK_AVAILABLE:
        return True
    if run_type is RunType.HELP:
        gs.output("Sometimes you gotta quit. Be sure to save your game at an island before quitting.")
        return
    gs.quitting = True

##################################################################

# check for config options
parser = argparse.ArgumentParser(description="Parse command-line arguments")
parser.add_argument("-l", "--logfile", required=False, help="Send logging output to specified file")
parser.add_argument("-rp", "--read-prompt", required=False, help="Read commands from file")
parser.add_argument("-wp", "--write-prompt", required=False, help="Write commands to file")
parser.add_argument("-lf", "--log-filter", required=False, nargs="+", help="List of log targets to include")
parser.add_argument("-sf", "--show-log-filters", required=False, action="store_true",help="Show all log filters")
args = parser.parse_args()

# set up logging
if args.show_log_filters:
    logging.list_log_targets()
    exit(0)
if args.logfile:
    logging.init(args.logfile, args.log_filter)

if args.read_prompt and args.read_prompt==args.write_prompt:
    print("Can't have same file for prompt reading and writing right now.")
    exit(1)

if args.read_prompt:
    debug.open_prompt_reader(args.read_prompt)
if args.write_prompt:
    debug.open_prompt_writer(args.write_prompt)

# initialize our global obj (due to circular refs issue)
gs.player = Player()
gs.ship = Ship()
gs.crew = Crew()
gs.stock = Stock()
gs.wind = Wind()
gs.hints = Hints()

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
    gs.map = map.Map(MAP_WIDTH, MAP_HEIGHT, gs.seed, gs.desc_gen)
    # generate quests
    setup.quest_setup()


    if not game_loaded:
        cont = setup.player_setup()

if cont:
    # set up the command interpreter
    gs.cmdsys = CommandSystem()

    gs.cmdsys.register(Command("!",  cmd_quit,
                               "Quit the game."))
    gs.cmdsys.register(Command("hints", cmd_hints, "Reset or turn off all hints"))
    gs.cmdsys.register(Command("quests", cmd_quests, "Show information about quests"))

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
        setup.init_trading_data()
        # init wind
        gs.wind.init_random()

if cont:


    # show initial status
    show_status(RunType.RUN, [])

    # if we are at an island, describe it
    # give the initial island description
    p = gs.map.get_place_at_location(gs.ship.location)
    if p:
        gs.output(p.island.describe())

    gs.hints.show("about")
    gs.hints.show("basic")
    # start the play loop
    run_loop()


logging.cleanup()
debug.close_prompt()

