import mainloop
import basic_cmds
import state
import setup
from command import CommandSystem, RunType, Command
from help import cmd_info

gs = state.GlobalState()


# registered quit command
def cmd_quit(gs, run_type, toks):
    if run_type == RunType.CHECK_AVAILABLE:
        return True
    if run_type == RunType.HELP:
        gs.output("Sometimes you gotta quit. When you quit, your progress will be saved for next time.")
        return
    if gs.input("Are you sure? [y/n]").lower() == 'y':
        gs.quitting = True


if setup.do_setup(gs):
    basic_cmds.show_status(gs, [])
    command_system = CommandSystem(gs)
    command_system.register_basic(Command("quit", "Quit the game", cmd_quit,
                                          "This will end the game. Progress will be saved."))
    command_system.register_alias("!", "quit")
    command_system.register_basic(Command("info", "[topic]", cmd_info,
                                          "Display information about the game. Optionally specify an info topic to "
                                          "display that topic."))
    command_system.register_alias("i", "info")
    mainloop.run_loop(gs, command_system)
