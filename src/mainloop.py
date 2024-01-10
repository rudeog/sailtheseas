from state import gs


def get_prompt():
    if gs.num_commands < 5:  # initially show this as the prompt
        return "? for help"
    gs.player.state
    return f"{gs.player.game_date()}: {gs.player.get_state()}"


def run_loop():
    while not gs.quitting:
        inp = gs.input(f"{get_prompt()}> ")
        gs.num_commands = gs.num_commands + 1
        gs.cmdsys.process_input(inp)
