# command file for ship commands
from command import RunType, Command
from state import global_state


def register_status_cmds():
    global_state.cmdsys.register(Command("status", "[sub]", show_status, "Show status"))
    global_state.cmdsys.register(Command("cargo","list cargo on vessel",show_cargo, ""))

def show_status(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        global_state.output(
            "By default this shows a summary about you and your ship. You may optionally specify a sub-command"
            " to show specific summary info. Available sub-commands are: crew, ship, weather")
        return
    if not toks:
        global_state.output(
            f"You are captain {global_state.player.name} who hails from {global_state.player.birthplace}.")
        global_state.output(f"You are on day {global_state.player.days} of your voyage.")
        global_state.output(f"You have {global_state.player.doubloons} doubloons.")
        global_state.output(
            f"The vessel which sails under the name '{global_state.player.ship.name}' is in fine condition.")
        global_state.output(f"You are at {global_state.map.places[0].name}")
        return
    if toks[0] == 'crew':
        global_state.output("The crew is mutinous!")
        return

    global_state.output("That type of status is not available at this time.")


def show_cargo(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        global_state.output(
            "Show what cargo your ship is carrying at this time. You may also examine or jettison cargo using this command.")
        return
    if not toks:
        if len(global_state.player.ship.cargo) == 0:
            global_state.output(f"{global_state.player.ship.name} is not carrying any cargo at this time.")
        else:
            global_state.output(f"{global_state.player.ship.name} is currently carrying the following cargo:")
            i = 1
            for c in global_state.player.ship.cargo:
                global_state.output(f"{str(i).rjust(2)}) {c}")
                i = i + 1
