from state import global_state
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

    def __init__(self, name, brief, fn, help_text):
        self.name = name  # name of command
        self.brief = brief  # brief description
        self.fn = fn  # function to run
        self.help_text = help_text  # help topic
        self.is_basic = False  # will not be printed in list of commands only shown in basic help
        self.aliases = []


class CommandSystem:
    def __init__(self):
        self.cmds: dict[str, Command] = {}
        self.aliases: dict[str, str] = {}

        self.register_basic(Command("commands", "", self._list_cmds,
                                    "Display a list of currently available commands. "
                                    "Some commands may be unavailable at certain times."))
        self.register_alias("c", "commands")
        self.register_basic(Command("help", "[command]", self._basic_help,
                                    "Display help for a specific command. "
                                    "For example '? status' will give help about the status command."))
        self.register_alias("?", "help")

    def process_input(self, input_text):
        """
        Process input text and invoke a function, or invoke the help system.
        This is the way input is gathered from the user during play
        :param input_text:
        :return:
        """
        toks = input_text.lower().split(' ')
        if toks[0] in self.aliases:
            cmd_to_run = self.aliases[toks[0]]
        else:
            cmd_to_run = toks[0]

        if cmd_to_run in self.cmds:  # first token is command name
            c = self.cmds[cmd_to_run]
            other_args = toks[1:]
            c.fn(RunType.RUN, other_args)
            return
        global_state.output("Command not understood. Enter ? for help")

    def register_basic(self, cmd: Command):
        cmd.is_basic = True
        self.register(cmd)

    def register(self, cmd: Command):
        """
        register a regular command with a function to run.
        the function accepts the global state as its first param etc
        :param cmd:
        :return:
        """
        self.cmds[cmd.name] = cmd

    def register_alias(self, alias, refers_to):
        """
        register an alias
        :param alias:
        :param refers_to:
        :return:
        """
        self.aliases[alias] = refers_to
        self.cmds[refers_to].aliases.append(alias)

    def _list_cmds(self, run_type: RunType, toks):
        if run_type == RunType.CHECK_AVAILABLE:
            return True
        if run_type == RunType.HELP:
            global_state.output("Will list all commands available now. Some commands may be unavailable at certain times.")
            return

        global_state.output("Available commands:")
        for k, v in self.cmds.items():
            if not v.is_basic:
                global_state.output(f"{v.name} {v.brief} - {v.help_text}", sub_indented=True)
                if v.aliases:
                    global_state.output(f"aliases: {', '.join(v.aliases)}", indented=True)

    def _basic_help(self, run_type: RunType, toks):
        if run_type == RunType.CHECK_AVAILABLE:
            return True
        if run_type == RunType.HELP:
            global_state.output("The help command may be used by itself, or followed by a topic or a command")
            return

        if not toks:  # no arg specified
            global_state.output("Help Overview:")
            for k, v in self.cmds.items():
                if v.is_basic:
                    global_state.output(f"{v.name} {v.brief} - {v.help_text}", sub_indented=True)
                    if v.aliases:
                        global_state.output(f"aliases: {', '.join(v.aliases)}", indented=True)
            return

        if toks[0] in self.aliases:
            cmd_help = self.aliases[toks[0]]
        else:
            cmd_help = toks[0]
        if cmd_help in self.cmds:
            # invoke help for a specific command
            c = self.cmds[cmd_help]
            c.fn(RunType.HELP, toks[1:])
