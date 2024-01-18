from command import Command, RunType
from turn import pass_time
from state import gs
from util import list_valid_directions, is_direction_valid, Direction, direction_from_two_coords


def register_nav_cmds():
    gs.cmdsys.register(Command("navigate", "[island id]", navigate_cmd,
                               "Navigate to an island specified by its numeric id."))
    gs.cmdsys.register_alias("nav", "navigate")

    gs.cmdsys.register(Command("direction", "[direction]", direction_cmd,
                               "Set your ship to sail in a specific direction."))
    gs.cmdsys.register_alias("dir", "direction")

    gs.cmdsys.register(Command("sail", "", sail_cmd,
                               "Sail your ship. This assumes you are navigating to a location or have set your bearing."))
    gs.cmdsys.register_alias("s", "sail")

    gs.cmdsys.register(Command("map", "[world]", map_cmd,
                               "Display either a local or world map."))

    gs.cmdsys.register(Command("islands", "[local]",list_islands_cmd,
                               "Display a list of islands along with their id."))


def navigate_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            return True
        return False
    if rt == RunType.HELP or not toks:
        gs.output(
            "To use this command you must know the id of the island you want to navigate to. Use a command such as "
            "'map' to get valid island id's. Note that you can only navigate to an island if it is visible on a "
            "map. That is to say that you have either been to it's coordinates, or it is within your local vicinity.")
        return
    try:
        integer_number = int(toks[0])
    except ValueError:
        gs.output("Invalid location id. You must specify a number.")
        return

    place = gs.map.get_place_by_index(integer_number)
    if not place or not place.visited:
        place = None
        # see if its within range (ie visible on short range map)
        pl = gs.map.get_all_nearby_places(gs.ship.location)
        for p in pl:
            if p.index == integer_number:
                place = p

    if not place:
        gs.output("You have not visited there, and wouldn't know how to get there from here.")
        return

    # reset regardless at this point
    gs.ship.b.reset()
    if gs.ship.distance_to_location(place.location) == 0:
        gs.output("You are already there.")
        return
    gs.output(f"{gs.ship.name} is set to sail to {place.name}")
    gs.ship.b.set_target(place.location)


def direction_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            return True
        return False
    if rt == RunType.HELP or not toks or not is_direction_valid(toks[0]):
        gs.output(
            "To use this command you must specify the direction that you want to point to. "
            f"Valid directions are {list_valid_directions()}. After you have set your direction, if you use "
            "the 'sail' command, you will sail in that direction, assuming you have not reached the end of the earth.")
        return
    old_dir = None
    if gs.ship.b.is_direction():
        old_dir = gs.ship.b.get()
    gs.ship.b.reset()  # not navigating
    new_dir = Direction(toks[0])
    gs.ship.b.set_direction(new_dir)

    if old_dir and (old_dir != new_dir):
        gs.output(f"{gs.ship.name} has changed direction from {old_dir} to {new_dir}")
    else:
        gs.output(f"{gs.ship.name} is set to sail {new_dir}")

def map_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            return True
        return False
    if rt == RunType.HELP or (toks and toks[0] != 'world'):
        gs.output(
            "Display a map. By default this map shows the are around your ship. If that area includes islands, "
            "they are displayed with their name. If you specify 'world', it will "
            "show a world map that includes islands which are in coordinates you have visited. "
            "The world map does not include island names.")
        return

    if toks:
        # show big map
        gs.output(gs.map.render_all_visited(gs.ship.location), nowrap=True)
        return

    # render local area with names
    gs.output(gs.map.render_local(gs.ship.location), nowrap=True)


def sail_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            return True
        return False
    if rt == RunType.HELP or not gs.ship.b.is_set():
        gs.output(
            "To use this command, you must first set your direction, or navigate using the direction or navigate command.")
        return

    # all we need to do is pass the time, it will take care of the rest
    pass_time()

def list_islands_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            return True
        return False
    if rt == RunType.HELP or (toks and toks[0] != "local"):
        gs.output(
            "List islands with their id, location and distance. Only islands that are within coordinates that "
            "your ship has visited, or are in your nearby coordinates are displayed. If 'local' is specified, then only "
            "islands in your nearby coordinates are displayed.")
        return
    if toks:
        local_only = True
    else:
        local_only = False

    np = gs.map.get_all_nearby_places(gs.ship.location)
    nearby = set()
    for n in np:
        nearby.add(n.index)

    for p in gs.map.places:
        if (p.visited and not local_only) or p.index in nearby:
            dist = gs.ship.distance_to_location(p.location)
            dir = direction_from_two_coords(gs.ship.location, p.location)
            if dir is None:
                dir = "away"
            gs.output(f"{str(p.index).rjust(3)} {p.name} - {dist} miles {dir}")





