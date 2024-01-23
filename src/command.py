from state import gs
from enum import Enum


class RunType(Enum):
    CHECK_AVAILABLE = 1
    HELP = 2
    RUN = 3


class Command:
    """
    A command is a word entered by the player followed by optional
    arguments. Commands can be registered with the command system.
    The function that is called will be passed these args:
    gs - game state
    run_type - this determines how the fn is being run:
        check_available - should return true if its available now
        help - should display its own help
        run - should execute
    toks -  a list of arguments to be passed

    """

    def __init__(self, name, cmdargs, fn, help_text):
        self.name = name  # name of command
        self.cmdargs = cmdargs  # help text for args
        self.fn = fn  # function to run
        self.help_text = help_text  # help topic


class CommandSystem:
    def __init__(self):
        self.cmds: dict[str, Command] = {}

    def process_input(self, input_text):
        """
        Process input text and invoke a function, or invoke the help system.
        This is the way input is gathered from the user during play
        :param input_text:
        :return:
        """
        toks = input_text.lower().split(' ')
        cmd_to_run = toks[0]
        if cmd_to_run == 'c' or cmd_to_run == 'help':
            self._list_cmds()
        else:
            if cmd_to_run in self.cmds:  # first token is command name
                c = self.cmds[cmd_to_run]
                other_args = toks[1:]
                if c.fn(RunType.CHECK_AVAILABLE, other_args):
                    if other_args and other_args[0]=='help':
                        c.fn(RunType.HELP, other_args[1:])
                    else:
                        c.fn(RunType.RUN, other_args)
                else:
                    gs.output("Command is unavailable at this time. Enter 'c' to see available commands.")
                return
            gs.output("Command not understood. Enter 'c' to see available commands.")


    def register(self, cmd: Command):
        """
        register a regular command with a function to run.
        the function accepts the global state as its first param etc
        :param cmd:
        :return:
        """
        self.cmds[cmd.name] = cmd


    def _list_cmds(self):
        gs.output(f"Available commands while {gs.player.get_state_str()}:")
        for k, v in self.cmds.items():
            if v.fn(RunType.CHECK_AVAILABLE, []):
                gs.output(f"{v.name} {'[' + v.cmdargs + '] ' if v.cmdargs else ''}- {v.help_text}", sub_indented=True)
        gs.output("You may enter a command followed by the word 'help' for more information about the command.")