import state
import basic_cmds
import port_cmds
import command

def ask_quit(gs, toks):
    if input("Are you sure? [y/n]").lower() == 'y':
        gs.quitting=True

help_topics = {
    "about": ["about the game", "here it is"],
}

def get_prompt(gs):
    if gs.num_commands < 5: # initially show this as the prompt
        return "? for help"
    return f"{gs.player.name}: Day {gs.player.days}"

def run_loop(gs:state.GlobalState, cs: command.CommandSystem):
    while not gs.quitting:
        inp=gs.input(f"{get_prompt(gs)}> ")
        gs.num_commands=gs.num_commands+1
        cs.process_input(inp)

