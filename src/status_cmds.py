# command file for ship commands
from command import RunType, Command
from state import gs
from util import as_int

def register_status_cmds():
    gs.cmdsys.register(Command("status",  show_status, "Show status"))
    gs.cmdsys.register(Command("cargo",  show_cargo, "List cargo on vessel"))
    gs.cmdsys.register(Command("describe",  describe_island_cmd, "Describe an island given it's ID."))
    gs.cmdsys.register(Command("ship",  describe_ship_cmd, "Describe your ship"))


def describe_ship_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output("This gives more details about your ship.")
        return

    gs.ship.describe()


def describe_island_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output("island <number> - show information about an island with the given number."
                  "If you omit the number and are nearby or on an island, that island is described.", sub_indented=True)
        return

    iid = None
    if toks:
        iid = toks[0]
        iid = as_int(iid)
        if iid<0:
            gs.gm_output("You need to enter a valid island number.")

    else:
        pl = gs.map.get_place_at_location(gs.ship.location)
        if pl:
            iid = pl.index

    if iid is None:
        gs.gm_output("Unless you are near an island, you need to specify an island by it's number. "
                     "For example: 'describe 999'. Use 'nearby', 'islands' or 'm' commands to determine island numbers.")
        return

    p = gs.map.get_place_by_index(iid)
    if p and p.visited:
        gs.output(p.island.describe())
    else:
        gs.gm_output(f"Sorry, {gs.player.name} but you can only describe islands that you are very close to, or islands "
                     "that you have been close to at some point. ")


def show_status(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output(
            "This shows a summary about you and your voyage.")
        return
    if not toks:
        gs.output(f"You are captain {gs.player.name} who hails from {gs.player.birthplace}. "
                  f"You are in the world of {gs.world_name} which is ruled by emperor {gs.emperor.last} and "
                  f"are on day {gs.player.num_days_elapsed() + 1} of your voyage. You "
                  f"have {gs.player.doubloons} doubloons.")

        # see if we are at a place
        place = gs.map.get_place_at_location(gs.ship.location)
        if place:
            # there should always be an island at a place
            gs.output(f"You are at {place.island.name}", False)
            if gs.player.is_docked():
                if place.island.port:  # should always be true in this case
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
                else:  # shouldnt happen
                    gs.output(f"{gs.ship.name} is heading to an undisclosed location.")

        return

    gs.gm_output("That type of status is not available at this time.")


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
            for c in gs.ship.cargo:
                gs.output(f"[{c.type.code}] {c} (paid {c.price_per}D per unit)")

