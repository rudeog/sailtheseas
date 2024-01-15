# manage global game state. This is at the top level.
# also handles IO
import textwrap
import shutil

DEBUGGING = True

class GlobalState:
    """
    Represents the top level global object
    """
    def __init__(self):
        # the name may determine the seed at some point?
        self.world_name = "Atlanticus"
        self.player = None
        self.ship = None
        self.map = None
        self.cmdsys = None
        self.num_commands = 0
        self.quitting = False
        self.debug_mode = DEBUGGING

        terminal_size = shutil.get_terminal_size(fallback=(120, 24))
        self.wrap_width = min(terminal_size.columns, 120)

    def output(self, output_text, newline: bool = True, nowrap: bool = False,
               indented: bool = False, sub_indented: bool = False):
        if not nowrap:
            output_text = textwrap.fill(output_text, width=self.wrap_width,
                                        initial_indent='  ' if indented else '',
                                        subsequent_indent='  ' if sub_indented else '')
        print(output_text, end="\n" if newline else "")

    def input(self, prompt):
        return input(prompt)

    def confirm(self, prompt="Are you sure?", cancel=False):
        valid = ['y', 'n']
        if cancel:
            valid.append('cancel')
        r = ''
        while r not in valid:
            r = input(f"{prompt} [{'/'.join(valid)}] ").lower()
        if r == 'y':
            return True
        if r == 'n':
            return False
        return None  # cancel


# a single global instance
gs = GlobalState()
