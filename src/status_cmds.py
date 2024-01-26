# command file for ship commands
from command import RunType, Command
from state import gs


def register_status_cmds():
    gs.cmdsys.register(Command("status", "...", show_status, "Show status"))
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
        gs.output(f"You are captain {gs.player.name} who hails from {gs.player.birthplace}. "
            f"You are in the world of {gs.world_name} which is ruled by emperor {gs.emperor.last} and " 
            f"are on day {gs.player.num_days_elapsed()+1} of your voyage. You "
                  f"have {gs.player.doubloons} doubloons.")

        # see if we are at a place
        place = gs.map.get_place_at_location(gs.ship.location)
        if place:
            # there should always be an island at a place
            gs.output(f"You are at {place.island.name}", False)
            if gs.player.is_docked():
                if place.island.port: # should always be true in this case
                    port_name = " " + place.island.port.name
                else:
                    port_name = ""
                gs.output(f" and {gs.ship.name} is docked at{port_name}.")
            elif gs.player.is_exploring():
                gs.output(f" and you are exploring the island.")
            elif gs.player.is_sailing():
                gs.output(f" and {gs.ship.name} is close to shore.")
            else:
                gs.output(".")

        if gs.player.is_sailing():

            if gs.ship.b.is_direction():
                gs.output(f"{gs.ship.name} is heading to the {gs.ship.b.get()}.")
            elif gs.ship.b.is_target():
                place = gs.map.get_place_at_location(gs.ship.b.get())
                if place:
                    gs.output(f"{gs.ship.name} is heading toward {place.island.name}.")
                else: # shouldnt happen
                    gs.output(f"{gs.ship.name} is heading to an undisclosed location.")

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
        if len(gs.ship.cargo) == 0:
            gs.output(f"{gs.ship.name} is not carrying any cargo at this time.")
        else:
            gs.output(f"{gs.ship.name} is currently carrying the following cargo:")
            i = 1
            for c in gs.ship.cargo:
                gs.output(f"{str(i).rjust(2)}) {c}")
                i = i + 1
