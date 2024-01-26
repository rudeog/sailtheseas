# manage global game state. This is at the top level.
# also handles IO
import textwrap
import shutil

#
# Game level defaults
#
DEBUGGING = True
GAME_NAME = "Sail The Seas"
DEFAULT_SEED = 51047
MAP_WIDTH = 15
MAP_HEIGHT = 15


class GlobalState:
    """
    Represents the top level global object
    """
    def __init__(self):
        self.seed = DEFAULT_SEED
        self.player = None
        self.ship = None

        self.world_name = None

        self.map = None
        self.cmdsys = None
        self.name_gen = None
        self.place_gen = None
        self.game_master = None
        self.emperor = None
        self.num_commands = 0
        self.quitting = False
        self.debug_mode = DEBUGGING

        terminal_size = shutil.get_terminal_size(fallback=(120, 24))
        self.wrap_width = min(terminal_size.columns, 120)

    # output as though the gm is speaking
    def gm_output(self, output_text, newline: bool = True, nowrap: bool = False,
                  indented: bool = False, sub_indented: bool = False):
        self.output(f"{self.game_master.first}:", newline=False)
        self.output(" " + output_text, newline, nowrap, indented, sub_indented)

    def output(self, output_text, newline: bool = True, nowrap: bool = False,
               indented: bool = False, sub_indented: bool = False):
        if not nowrap:
            output_text = textwrap.fill(output_text, width=self.wrap_width,
                                        initial_indent='  ' if indented else '',
                                        subsequent_indent='  ' if sub_indented else '')
        print(output_text, end="\n" if newline else "")

    def gm_input(self, prompt):
        return self.input(f"{self.game_master.first}: {prompt}")

    def input(self, prompt):
        return input(prompt)

    def gm_confirm(self, prompt="Are you sure?", cancel=False):
        return self.confirm(f"{self.game_master.first}: {prompt}", cancel)

    def confirm(self, prompt="Are you sure?", cancel=False):
        valid = ['y', 'n']
        if cancel:
            valid.append('cancel')
        r = ''
        while r not in valid:
            r = self.input(f"{prompt} [{'/'.join(valid)}] ").lower()
        if r == 'y':
            return True
        if r == 'n':
            return False
        return None  # cancel

# a single global instance
gs = GlobalState()
