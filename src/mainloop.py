import state
import ship_cmds
import port_cmds

def print_adv_help(player, toks):
    print("Available commands:")
    for k,v in commands.items():
        if len(v) < 4 or v[3] == player.location:
            if v[2] > 0:
                print(f"{k} - {v[1]}")

def print_basic_help(player, toks):
    print("Basic commands:")
    for k,v in commands.items():
        if v[2] < 2:
            print(f"{k} - {v[1]}")

def ask_quit(player, toks):
    if input("Are you sure? [y/n]").lower() == 'y':
        player.quitting=True

# 0 = basic, 1 = both, 2 = advanced
commands = {
    "?": [print_basic_help,"basic help (what you are looking at)",0],
    "q": [ask_quit, "quit the game",0],
    "cmds": [print_adv_help,"list all available commands", 0],
    "status":[ship_cmds.show_status,"show current status",1],
    "cargo": [ship_cmds.list_cargo,"show the cargo of the ship",2],
    "buy": [port_cmds.buy_cargo,"buy cargo",2, "port"]
}


def get_prompt(player):
    if player.num_commands < 5:
        return "? for help"
    return f"{player.name}: Day {player.days}"

def process_input(player, cmd):
    toks = cmd.lower().split(' ')
    if toks[0] in commands:
        c = commands[toks[0]]
        if c[0]:
            c[0](player, toks[1:])
        return
    print("Command not understood. Enter ? for help")


def run_loop(player):
    while not player.quitting:
        inp=input(f"{get_prompt(player)}>")
        player.num_commands=player.num_commands+1
        process_input(player, inp)