from mainloop import run_loop
from status_cmds import register_status_cmds, show_status
from state import global_state
import setup
import map
from command import CommandSystem, RunType, Command
from help import register_info_cmds
from cargo import cargo_types

SEED = 51043
WIDTH = 10
HEIGHT = 10


# registered quit command
def cmd_quit(run_type, toks):
    if run_type == RunType.CHECK_AVAILABLE:
        return True
    if run_type == RunType.HELP:
        global_state.output("Sometimes you gotta quit. When you quit, your progress will be saved for next time.")
        return
    global_state.quitting = global_state.confirm()


# Get player info, etc
if setup.player_setup():
    # figure out our seed
    # todo

    # generate the map
    global_state.map = map.Map(WIDTH, HEIGHT, SEED)

    # set up the command interpreter
    global_state.cmdsys = CommandSystem()

    global_state.cmdsys.register_basic(Command("quit", "Quit the game", cmd_quit,
                                               "This will end the game. Progress will be saved."))
    global_state.cmdsys.register_alias("!", "quit")

    # register other commands
    register_info_cmds()
    register_status_cmds()

    # show initial status
    show_status(RunType.RUN, [])

    # todo remove
    global_state.player.ship.cargo.add_remove(cargo_types[0], 10)

    # start the play loop
    run_loop()
