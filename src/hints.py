from command import RunType
from state import gs

_hints = {
    "about": "Since you are just starting out, you will get hints whenever you do something new. Use the hint command to control them.",
    "basic": "You will interact with the game by entering commands. Some commands have subcommands which may be optional "
             "or required. If you need more information about a command, you may enter the command followed by the subcommand 'help', "
             "For example 'trade help' will show help on trading.",
    "trading": "Use the buy, sell and pawn commands to interact with the trading system.",
    "pawn": "If you are low on doubloons, and have cargo that is unwanted by a portmaster, you may still pawn it off using the pawn command.",
    "atsea": "You are now aboard ship. Some new commands are available, and some other commands may not be available anymore. "
        "The most important commands at sea are 'nav', 'dir', 'm' and 's'.",
    "sailing": "Every time you use the sail command, you will sail for one quarter of a day. Wind direction, along with other factors "
        "will determine how far you sail.",
    "arrived": "When you arrive at an island, you are still about ship. Use the 'land' command to disembark and go onto the island.",
    "lowsupp": "To keep your ship stocked with supplies, use the 'restock' command. To check current stocks use the 'stock' command.",
    "landed": "When you arrive at an island, you may save your progress using the 'save' command.",
}
# idx into above
HINT_ID_ABOUTHINTS = 0


class Hints:
    def __init__(self):
        self.active = set()
        self.reset()

    def set(self, d):
        self.active = set(d["active"])


    def get(self):
        return {
            "active": list(self.active),
        }
    def reset(self):
        self.active = set(_hints.keys())

    def clear(self):
        self.active = {}

    def show(self,hint_id):
        if hint_id in self.active:
            gs.output("[HINT: " + _hints[hint_id] + "]" )
            self.active.remove(hint_id)
        else:
            if hint_id not in _hints:
                raise KeyError(f"hint {hint_id} not in system")

def cmd_hints(run_type, toks):
    if run_type is RunType.CHECK_AVAILABLE:
        return True
    if run_type is RunType.HELP or not toks or toks[0] not in ['reset', 'off']:
        gs.output("The hint system provides hints for newbie players. After each hint has been displayed once, it is "
                  "turned off. This command allows you to turn off all hints, or turn them all on so they are shown again "
                  "as appropriate. Valid options are 'reset' and 'off'.\n"
                  "reset - Reset all hints so that they get redisplayed\n"
                  "off - turn off all hints")
        return
    if toks[0]=='reset':
        gs.hints.reset()
        gs.gm_output("I've reset the hint system. Hopefully you'll gain some wisdom from it.")
    else:
        gs.hints.clear()
        gs.gm_output("Oh, too clever for hints are you? Well I've turned them off, so there!")



