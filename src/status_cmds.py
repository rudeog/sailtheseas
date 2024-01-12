# command file for ship commands
from command import RunType, Command
from player import PlayerState
from state import gs


def register_status_cmds():
    gs.cmdsys.register(Command("status", "[sub]", show_status, "Show status"))
    gs.cmdsys.register(Command("cargo", "", show_cargo, "list cargo on vessel"))


def show_status(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output(
            "By default this shows a summary about you and your ship. You may optionally specify a sub-command"
            " to show specific summary info. Available sub-commands are: crew, ship, weather")
        return
    if not toks:
        gs.output(
            f"You are captain {gs.player.name} who hails from {gs.player.birthplace}.")
        gs.output(f"You are on day {gs.player.days} of your voyage, and "
                  f"have {gs.player.doubloons} doubloons.")

        # see if we are at a place
        place = gs.map.get_place_at_location(gs.player.ship.location)
        if place:
            gs.output(f"You are at {place.name}", False)
            if gs.player.state is PlayerState.DOCKED:
                if place.port: # should always be true in this case
                    port_name = " " + place.port.name
                else:
                    port_name = ""
                gs.output(f" and {gs.player.ship.name} is docked at{port_name}.")
            elif gs.player.state is PlayerState.EXPLORING:
                gs.output(f" and you are exploring the island.")
            elif gs.player.state is PlayerState.SAILING:
                gs.output(f" and {gs.player.ship.name} is close to shore.")
            else:
                gs.output(".")

        if gs.player.state is PlayerState.SAILING:
            t, v = gs.player.ship.bearing.get()
            if t==gs.player.ship.bearing.Type.DIRECTION:
                gs.output(f"{gs.player.ship.name} is heading to the {v}.")
            elif t==gs.player.ship.bearing.Type.TARGET:
                place = gs.map.get_place_at_location(v)
                if place:
                    gs.output(f"{gs.player.ship.name} is heading toward {place.name}.")
                else: # shouldnt happen
                    gs.output(f"{gs.player.ship.name} is heading to an undisclosed location.")

        return
    if toks[0] == 'crew':
        gs.output("The crew is mutinous!")
        return

    gs.output("That type of status is not available at this time.")


def show_cargo(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output(
            "Show what cargo your ship is carrying at this time. You may also examine or jettison cargo using this command.")
        return
    if not toks:
        if len(gs.player.ship.cargo) == 0:
            gs.output(f"{gs.player.ship.name} is not carrying any cargo at this time.")
        else:
            gs.output(f"{gs.player.ship.name} is currently carrying the following cargo:")
            i = 1
            for c in gs.player.ship.cargo:
                gs.output(f"{str(i).rjust(2)}) {c}")
                i = i + 1
