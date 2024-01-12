from state import gs


def get_prompt():
    if gs.num_commands < 3:  # initially show this as the prompt
        hint = "(? for help) "
    else:
        hint = ""

    return f"{hint}{gs.player.game_date()} at {gs.player.ship.location[0]}E "\
           f"{gs.player.ship.location[1]}S: {gs.player.get_state()}"


def run_loop():
    while not gs.quitting:
        inp = gs.input(f"{get_prompt()}> ")
        gs.num_commands = gs.num_commands + 1
        gs.cmdsys.process_input(inp)
