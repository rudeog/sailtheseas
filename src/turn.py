# this deals with commands that cause time to flow.
# The commands that cause time to move are sailing, resting and exploring.
# other encounters such as trading, battling, etc do not.
from state import gs


def pass_time():
    gs.player.time_increment()
    # if we are sailing we need to move if possible
    if gs.player.is_sailing() and gs.ship.b.is_set():
        _sail()


def _sail():
    # figure out how many miles we will travel based on conditions, equipment and crew
    miles_available = 24  # assumes 4 knots
    sail_result, miles_traveled, other = gs.ship.sail(miles_available)
    if miles_traveled:
        gs.output(f"{gs.crew.boatswain}: {gs.ship.name} sails {miles_traveled} miles at an average speed of 4 knots.")
    if sail_result == gs.ship.SAIL_RESULT_EDGE_OF_WORLD:
        gs.output(f"{gs.crew.navigator}: I don't mean to put fear into you captain, but we have reached the "
                  "edge of the world. Please choose a new direction or target.")
        gs.ship.b.reset()  # stop navigating, the player must determine what to do next
        # and they must move back to center of square before going anywhere else

    # if we are navigating and we reached our destination...
    elif sail_result == gs.ship.SAIL_RESULT_ARRIVED:
        p = gs.map.get_place_at_location(gs.ship.location)
        if p:
            d = p.island.name
        else:
            d = "your destination"
        gs.output(f"{gs.crew.boatswain}: {gs.ship.name} has arrived at {d}.")
        gs.ship.b.reset()
    elif sail_result == gs.ship.SAIL_RESULT_ENTERED_NEW_SQUARE:
        pl = gs.map.get_place_at_location(gs.ship.location)
        if pl:
            dist = gs.ship.distance_to_location(gs.ship.location)
            gs.output(f"{gs.crew.lookout}: I have sighted the island of {pl.island.name}!")
            gs.output(f"{gs.crew.navigator}: The island is {dist} miles away, captain.")
            if other:  # first time here
                gs.gm_output("Here is some more information I found about the island:")
                gs.output(pl.island.describe())
