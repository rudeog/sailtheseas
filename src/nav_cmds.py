from command import Command, RunType
from turn import pass_time
from state import gs
from util import list_valid_directions, is_direction_valid, Direction, direction_from_two_coords, as_int, fancy_time


def register_nav_cmds():
    # not really a nav command but...
    gs.cmdsys.register(Command("rest", rest_cmd,
                               "Rest for a watch."))

    gs.cmdsys.register(Command("nav", navigate_cmd,
                               "Navigate to an island specified by its numeric id."))

    gs.cmdsys.register(Command("dir", direction_cmd,
                               "Set your ship to sail in a specific direction (sets bearing)."))

    gs.cmdsys.register(Command("s", sail_cmd,
                               "Sail your ship. This assumes you are navigating to a location or have set your bearing."))

    gs.cmdsys.register(Command("m", map_cmd,
                               "Display a local map with nearby islands."))

    gs.cmdsys.register(Command("world", world_cmd,
                               "Display a world map."))

    gs.cmdsys.register(Command("islands", list_islands_cmd,
                               "Display details of all known islands."))
    gs.cmdsys.register(Command("nearby", list_islands_nearby_cmd,
                               "Display details of nearby islands."))


def rest_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output(
            "This command will allow the crew to rest for a period of six hours (one watch). If sailing, "
            "your ship will be anchored. Your crew will still consume resources when resting.")
        return
    gs.output(f"{gs.crew.boatswain}: I've ordered the crew to do nothing until {fancy_time(gs.player.current_time()+1)}, captain.")
    pass_time(True)


def navigate_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            return True
        return False
    if rt == RunType.HELP or not toks:
        gs.output(
            "To use this command you must know the id of the island you want to navigate to. Use commands such as "
            "'m' or 'islands' to get valid island id's. Note that you can only navigate to an island if it is visible on a "
            "map. That is to say that you have either previously been to it's coordinates, or it is within your local vicinity.")
        return

    integer_number = as_int(toks[0])
    if integer_number < 0:
        gs.gm_output("Invalid location id. You must specify a number.")
        return

    place = gs.map.get_place_by_index(integer_number)
    if place and not place.visited:
        if not gs.map.is_nearby(gs.ship.location, place.location):
            place = None

    if not place:
        gs.output(f"{gs.crew.navigator}: We have not visited there, and I have no knowledge of how to get there from here.")
        return

    # reset regardless at this point
    gs.ship.b.reset()
    if gs.ship.distance_to_location(place.location) == 0:
        gs.output(f"{gs.crew.navigator}: We are already there, captain.")
        return
    gs.output(f"{gs.crew.navigator}: {gs.ship.name} is set to sail to {place.island.name}")
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
            "the 's' command, you will sail in that direction, assuming you have not reached the end of the earth.")
        return
    old_dir = None
    if gs.ship.b.is_direction():
        old_dir = gs.ship.b.as_target_or_direction()
    gs.ship.b.reset()  # not navigating
    new_dir = Direction(toks[0])
    gs.ship.b.set_direction(new_dir)

    if old_dir and (old_dir != new_dir):
        gs.output(f"{gs.crew.navigator}: {gs.ship.name} has changed direction from {old_dir} to {new_dir}.")
    else:
        gs.output(f"{gs.crew.navigator}: {gs.ship.name} is set to sail {new_dir}!")


def map_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True

    if rt == RunType.HELP:
        gs.output("This map shows the area around your ship. If that area includes islands, "
                  "they are displayed with their name.")
        return

    # render local area with names
    gs.output(gs.map.render_local(gs.ship.location, gs.wrap_width), nowrap=True)


def world_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True

    if rt == RunType.HELP:
        gs.output("This displays a map of the entire world. The map will includes islands which "
                  "you have knowledge of (they are in coordinates you have visited.) It will "
                  "also show where you have traveled. It will not show nearby islands unless you have knowledge of them.")
        return

    gs.output(gs.map.render_all_visited(gs.ship.location, gs.wrap_width), nowrap=True)


def sail_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            return True
        return False
    if rt == RunType.HELP or not gs.ship.b.is_set():
        gs.output(
            f"{gs.crew.boatswain}: Captain, I have not received any instructions from {gs.crew.navigator}.")
        gs.gm_output("You must first set your direction, or navigate using the 'dir' or 'nav' command.")
        return

    # all we need to do is pass the time, it will take care of the rest
    pass_time(False)

def list_islands_nearby_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True

    if rt == RunType.HELP:
        gs.output("This displays a list of nearby islands with their id, distance and direction")
        return
    gs.output(f"{gs.crew.navigator}: Here are details about nearby islands.")
    _list_islands(True)

def list_islands_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output("This displays a list of all known islands in the world with their id, distance and direction")
        return
    gs.output(f"{gs.crew.navigator}: Here are details about all the islands we know about in {gs.world_name}.")
    _list_islands(False)

def _list_islands(local_only: bool):
    recent = gs.player.get_last_visited()  # list
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
            if p.island.explored:
                exp = f" - {p.island.explored}% explored"
            else:
                exp = ""
            gs.output(f"{str(p.index).rjust(3)} {p.island.name} ({p.island.summary()}) - {dist} miles {dir}{exp}")
