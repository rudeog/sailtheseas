# manage global game state. This is at the top level.
# also handles IO
import textwrap
import shutil
from datetime import datetime

import debug
from util import as_int

#
# Game level defaults
#
DEBUGGING = True
GAME_NAME = "Sail The Seas"
GAME_VERSION = "0.1"
DEFAULT_SEED = 51047
MAP_WIDTH = 15
MAP_HEIGHT = 15
# when our game starts
STARTING_DATE = date_constant = datetime(1716, 6, 1)

# "The largest merchant ships were the East Indiamen, in three broad classes, of 1200 tons, 800 tons, or 500 tons."
# 300 tons in pounds
DEFAULT_CARGO_CAPACITY = 300 * 2000
# full ship of able bodied seamen
ABS_COUNT_MAX = 100
# this number or lower and ship function is reduced
ABS_COUNT_REDUCED = 69
# this number or lower and ship function is impaired
ABS_COUNT_IMPAIRED = 39
# this or lower than this and the ship cant sail
ABS_COUNT_NONFUNCTIONAL = 9
# ABS monthly pay
ABS_PAY = 5
# pay period in days
ABS_PAY_PERIOD = 30

# if these are too high we might not be able to fit on map
NUM_QUESTS = 2
NUM_QUEST_CLUES = 2
NUM_QUEST_ARTIFACTS = (2,3,5)

DEFAULT_STARTING_DOUBLOONS = 10000

# max islands to keep on last visited list. When an island is
# bumped from this list its trading data is updated. Therefore given island X, a player must visit this many
# other islands before island X gets its trading data updated
MAX_LAST_VISITED = 3


class GlobalState:
    """
    Represents the top level global object
    """

    def __init__(self):
        # this will be overriden to DEFAULT_SEED + n when the player selects a world.
        # this should only be used for setting up
        self.seed = DEFAULT_SEED

        self.player = None
        self.ship = None
        self.crew = None
        self.stock = None
        self.hints = None

        self.world_name = None

        self.map = None
        self.quests = None
        self.cmdsys = None


        # the play rng is used to determine random game events which may differ
        # between games set in the same world, but should be the same if the player
        # does identical things in the same world. Same for name_gen
        self.rng_play = None
        self.name_gen = None

        self.game_master = None
        self.emperor = None
        self.wind = None
        # number of commands issued
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
            lines = output_text.split("\n")
            for line in lines:
                output_text = textwrap.fill(line, width=self.wrap_width,
                                            initial_indent='  ' if indented else '',
                                            subsequent_indent='  ' if sub_indented else '')
                print(output_text, end="\n" if newline else "")
        else:
            print(output_text, end="\n" if newline else "")

    def gm_input(self, prompt):
        if self.game_master:
            return self.input(f"GM {self.game_master.first}: {prompt}")
        return self.input(prompt)

    def input(self, prompt):
        r = debug.read_prompt()
        if r is None:
            while True:
                self.output(prompt, newline=False)
                r = input(" ")
                if r:
                    break
                self.gm_output("You didn't enter anything!")
        else: # output what came from the file
            self.output(f"{prompt} \"{r}\"")
        debug.write_prompt(r, prompt)
        return r.strip()

    def input_num(self, min_val, max_val, prompt="", nocancel=False, done_token='$', noquit=False):
        '''
        Prompts for integer input. Validates that its within range
        :param prompt: optional text before prompt
        :param min_val: min allowed value
        :param max_val: max allowed value
        :param nocancel: disallow exiting without choosing a number
        :param done_token: $ is always allowed, this is an alternative synonym
        :param noquit: the ! to quit option is not available here
        :return: the number entered or min_val-1 if canceled or quitting. if quitting, gs.quitting will be True
        '''

        if min_val > max_val:
            raise ValueError
        if prompt == "":
            prompt = "Enter a value"

        suff = f"[{int(min_val)}..{int(max_val)}"
        if not nocancel:
            if done_token=='$':
                suff += '/$=back'
            else:
                suff += "/"+done_token
        suff += "]"

        ctr=0
        reprimands = [
            f"{gs.player.name}, please pay attention.",
            f"Really, {gs.player.name}, is it that hard to follow instructions?",
        ]

        while True:
            sel = self.input(f"{prompt} {suff}: ")
            self.output("")
            if (sel in ('$', done_token)) and not nocancel:
                return min_val - 1
            if sel == '!' and not noquit:
                gs.quitting = True
                return min_val - 1

            nsel = as_int(sel, min_val - 1)
            if nsel < min_val or nsel > max_val:
                rep_idx = (ctr) % len(reprimands)
                self.gm_output(reprimands[rep_idx])
                gs.output("")
            else:
                return nsel
            ctr += 1

    def gm_confirm(self, prompt="Are you sure?", cancel=False):
        if self.game_master:
            return self.confirm(f"GM {self.game_master.first}: {prompt}", cancel)
        return self.confirm(prompt, cancel)

    def confirm(self, prompt="Are you sure?", cancel=False):
        valid = ['y', 'n']
        suff = ""
        if cancel:
            valid.append('$')
            suff = "/$=cancel"
        r = ''
        while r not in valid:
            r = self.input(f"{prompt} [y/n{suff}] ").lower()
        if r == 'y':
            return True
        if r == 'n':
            return False
        return None  # cancel


# a single global instance
gs = GlobalState()
