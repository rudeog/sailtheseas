from mainloop import run_loop
from port_cmds import register_port_cmds
from status_cmds import register_status_cmds, show_status
from nav_cmds import register_nav_cmds
from state import gs
import setup
import map
from command import CommandSystem, RunType, Command
from help import register_info_cmds
from cargo import cargo_types

SEED = 51041
WIDTH = 10
HEIGHT = 10


# registered quit command
def cmd_quit(run_type, toks):
    if run_type == RunType.CHECK_AVAILABLE:
        return True
    if run_type == RunType.HELP:
        gs.output("Sometimes you gotta quit. When you quit, your progress will be saved for next time.")
        return
    gs.quitting = gs.confirm()


# Get player info, etc
if setup.player_setup():
    # figure out our seed
    # todo

    # generate the map
    gs.map = map.Map(WIDTH, HEIGHT, SEED)

    # set up the command interpreter
    gs.cmdsys = CommandSystem()

    gs.cmdsys.register_basic(Command("quit", "Quit the game", cmd_quit,
                                               "This will end the game. Progress will be saved."))
    gs.cmdsys.register_alias("!", "quit")

    # register other commands
    register_info_cmds()
    register_status_cmds()
    register_port_cmds()
    register_nav_cmds()

    # place player at 0 location
    setup.set_player_start_location()

    # show initial status
    show_status(RunType.RUN, [])

    # todo remove
    gs.ship.cargo.add_remove(cargo_types[0], 10)

    # start the play loop
    run_loop()
