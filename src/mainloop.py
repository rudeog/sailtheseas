from state import gs
from util import fancy_date

def get_prompt():
    if gs.num_commands < 3:  # initially show this as the prompt
        hint = "(? for help) "
    else:
        hint = ""

    return f"{hint}{fancy_date(gs.player.current_date())} at {gs.ship.location[0]}E "\
           f"{gs.ship.location[1]}S: {gs.player.get_state_str()}"


def run_loop():
    while not gs.quitting:
        inp = gs.input(f"{get_prompt()}> ")
        gs.num_commands = gs.num_commands + 1
        gs.output("")
        gs.cmdsys.process_input(inp)
