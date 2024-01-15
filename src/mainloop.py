from state import gs
from util import fancy_date, fancy_time

def get_prompt():
    if gs.num_commands < 3:  # initially show this as the prompt
        hint = "(? for help) "
    else:
        hint = ""

    p = f"{hint}{fancy_time(gs.player.current_time())} of {fancy_date(gs.player.current_date())} at {gs.ship.location[0]}E "\
           f"{gs.ship.location[1]}S: {gs.player.get_state_str()}"

    if gs.debug_mode:
        if gs.player.is_sailing():
            p = p + f"\n{'inward' if gs.ship.toward_center else 'outward'} {gs.ship.miles_traveled_in_square} miles"
            if gs.ship.diagonal_entry:
                p = p + " diagonal"
    return p

def run_loop():
    while not gs.quitting:
        inp = gs.input(f"{get_prompt()}> ")
        gs.num_commands = gs.num_commands + 1
        gs.output("")
        gs.cmdsys.process_input(inp)
