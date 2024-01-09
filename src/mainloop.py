from state import global_state


def get_prompt():
    if global_state.num_commands < 5:  # initially show this as the prompt
        return "? for help"
    return f"{global_state.player.name}: Day {global_state.player.days}"


def run_loop():
    while not global_state.quitting:
        inp = global_state.input(f"{get_prompt()}> ")
        global_state.num_commands = global_state.num_commands + 1
        global_state.cmdsys.process_input(inp)
