import state
import basic_cmds
import port_cmds

def print_adv_help(gs, toks):
    print("Available commands:")
    for k,v in commands.items():
        if len(v) < 4 or v[3] == gs.player.location:
            if v[2] > 0:
                print(f"{k} - {v[1]}")

def print_basic_help(gs, toks):
    if toks and toks[0] in help_topics:
        print(help_topics[toks[0]][1])
        return


    print("You play this game by issuing commands. Some commands are available all the time while other commands are only\n" +
          "available when you are in port, exploring, sailing, etc. Further help is available by using ? followed by a\n" +
          "command or a help topic. For example '? status' will give further help on the status command, or '? about' will\n" +
          "print the 'about' help topic.")
    print("Basic commands:")
    for k,v in commands.items():
        if v[2] < 2 and v[2] >= 0:
            print(f"{k} - {v[1]}")
    print("Help topics:")
    for k,v in help_topics.items():
        print(f"? {k} - {v[0]}")

def ask_quit(gs, toks):
    if input("Are you sure? [y/n]").lower() == 'y':
        gs.quitting=True

# 3rd element determines where this help item is printed:
# 0 = basic, 1 = both, 2 = advanced, -1 never
commands = {
    "?": [print_basic_help,"basic help",-1],
    "help": [print_basic_help,"alias for ?",-1],
    "quit": [ask_quit, "quit the game",0],
    "cmds": [print_adv_help,"list all currently available commands", 0],
    "status": [basic_cmds.show_status,"show current status",1],
    "cargo": [basic_cmds.list_cargo,"show the cargo of the ship",2],
    "buy": [port_cmds.buy_cargo,"buy cargo",2, "port"]
}

help_topics = {
    "about": ["about the game", "here it is"],
}

def get_prompt(gs):
    if gs.num_commands < 5: # initially show this as the prompt
        return "? for help"
    return f"{gs.player.name}: Day {gs.player.days}"

def process_input(gs, cmd):
    toks = cmd.lower().split(' ')
    if toks[0] in commands:
        c = commands[toks[0]]
        if c[0]:
            c[0](gs, toks[1:])
        return
    print("Command not understood. Enter ? for help")


def run_loop(gs):
    while not gs.quitting:
        inp=input(f"{get_prompt(gs)}>")
        gs.num_commands=gs.num_commands+1
        process_input(gs, inp)