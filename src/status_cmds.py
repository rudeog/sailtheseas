# command file for ship commands
from command import RunType, Command
from state import gs
from util import as_int


def register_status_cmds():
    gs.cmdsys.register(Command("status","info", show_status, "Show current status"))
    gs.cmdsys.register(Command("cargo","info", show_cargo, "List cargo on vessel"))
    gs.cmdsys.register(Command("describe", "info",describe_island_cmd, "Describe an island given it's ID."))
    gs.cmdsys.register(
        Command("stock", "info",describe_stock_cmd, "Show the stock of supplies that you are carrying: food, water, etc."))
    gs.cmdsys.register(Command("wind", "info",show_wind, "Show current wind conditions"))

def describe_stock_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output("This gives more details about what supplies you are carrying. "
                  "You may use the restock command to refresh these supplies.")
        return
    gs.output(f"{gs.crew.firstmate}: I've taken stock of what we have on board {gs.ship.name} and we have "
              "the following supplies:")
    gs.output(gs.stock.describe())


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
        if iid < 0:
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
    elif gs.map.is_nearby(gs.ship.location, p.location):
        gs.gm_output(
            f"This is all I can tell you about {p.island.name}: {p.island.summary()}. If you get closer to it, you "
            "can get a more detailed description.")

    else:
        gs.gm_output(
            f"Sorry, {gs.player.name} but you can only describe islands that you are very close to, or islands "
            "that you have been close to at some point.")

def show_wind(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return not gs.player.is_on_land()
    if rt == RunType.HELP:
        gs.output(
            "This shows wind conditions.")
        return

    gs.output(f"{gs.crew.lookout}: The wind is {gs.wind}, captain.\n")


def show_status(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output(
            "This shows all information about you, your ship and your voyage.")
        return
    if not toks:
        op = f"You are captain {gs.player.name} who hails from {gs.player.birthplace}. "
        op += f"You are in the world of {gs.world_name} which is ruled by emperor {gs.emperor.last}. "
        op += f"You are on day {gs.player.num_days_elapsed + 1} of your voyage. You "
        op += f"have {gs.player.doubloons} doubloons. "
        op += gs.ship.describe()
        op += "\n"

        # see if we are at a place
        place = gs.map.get_place_at_location(gs.ship.location)
        dist = gs.ship.distance_to_location(gs.ship.location)
        if place:
            if dist > 0:
                prox = "close to the shores of"
            else:
                prox = "at"

            # there should always be an island at a place
            op += f"You are {prox} {place.island.name}"
            if gs.player.is_on_land():
                if place.island.port:
                    op += f" and {gs.ship.name} is docked at {place.island.port.name}. "
                else:
                    op += f". You and your crew have disembarked, and are on shore. "
            else:
                op += ". "

        if gs.player.is_at_sea():
            if gs.ship.b.is_direction():
                op += f"{gs.ship.name} is heading to the {gs.ship.b.as_target_or_direction()}.\n"
            elif gs.ship.b.is_target():
                place = gs.map.get_place_at_location(gs.ship.b.as_target_or_direction())
                if place:
                    op += f"{gs.ship.name} is heading toward {place.island.name}.\n"
                else:  # shouldnt happen
                    op += "{gs.ship.name} is heading to an undisclosed location.\n"

            if gs.player.num_days_at_sea > 0:
                op += f"You have been at sea for {gs.player.num_days_at_sea} days.\n"

            # show weather conditions
            op += f"The wind is {gs.wind}.\n"
        op += "\n"
        gs.output(op)
        return


def show_cargo(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output(
            "Show what cargo your ship is carrying at this time. You may also examine or jettison cargo using this command.")
        return
    if not toks:
        if len(gs.ship.cargo) == 0:
            gs.output(f"{gs.crew.firstmate}: {gs.ship.name} is not carrying any cargo at this time.")
        else:
            gs.output(f"{gs.crew.firstmate}: {gs.ship.name} is currently carrying the following cargo:")
            for c in gs.ship.cargo:
                gs.output(f"[{c.type.code}] {c} (paid {c.price_per}D per unit)")
