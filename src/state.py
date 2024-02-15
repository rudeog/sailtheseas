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

# "The largest merchant ships were the East Indiamen, in three broad classes, of 1200 tons, 800 tons, or 500 tons."
# 300 tons in pounds
DEFAULT_CARGO_CAPACITY = 300 * 2000

class GlobalState:
    """
    Represents the top level global object
    """
    def __init__(self):
        # this will be overriden to DEFAULT_SEED + n when the player selects a world
        self.seed = DEFAULT_SEED
        self.player = None
        self.ship = None
        self.crew = None

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
        if self.game_master:
            self.output(f"GM {self.game_master.first}:", newline=False)
        self.output(" " + output_text, newline, nowrap, indented, sub_indented)

    def output(self, output_text, newline: bool = True, nowrap: bool = False,
               indented: bool = False, sub_indented: bool = False):
        if not nowrap:
            output_text = textwrap.fill(output_text, width=self.wrap_width,
                                        initial_indent='  ' if indented else '',
                                        subsequent_indent='  ' if sub_indented else '')
        print(output_text, end="\n" if newline else "")

    def gm_input(self, prompt):
        if self.game_master:
            return self.input(f"GM {self.game_master.first}: {prompt}")
        return self.input(prompt)

    def input(self, prompt):
        while True:
            r = input(prompt)
            if r:
                break
            self.gm_output("You didn't enter anything!")
        return r

    def gm_confirm(self, prompt="Are you sure?", cancel=False):
        if self.game_master:
            return self.confirm(f"GM {self.game_master.first}: {prompt}", cancel)
        return self.confirm(prompt,cancel)

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
