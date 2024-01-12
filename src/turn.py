# this deals with commands that cause time to flow.
# The commands that cause time to move are sailing, resting and exploring.
# other encounters such as trading, battling, etc do not.
from util import add_pair, get_step_towards_destination
from state import gs

def pass_time():
    gs.player.day_increment()
    sail()


def sail():
    # if we are sailing we need to move if possible

    if gs.player.is_sailing() and gs.ship.b.is_set():
        if gs.ship.travel_pct < 100:
            gs.ship.travel_pct += 50
        if gs.ship.travel_pct >= 100:
            gs.ship.travel_pct = 0
            if gs.ship.b.is_direction():
                coords = gs.ship.b.get().to_coords()
            else:
                coords = get_step_towards_destination(gs.ship.location, gs.ship.b.get())
            new_coords = add_pair(gs.ship.location, coords)
            loc = gs.map.get_location(new_coords)
            if loc:
                gs.ship.location = new_coords
                loc.visited = True
            else:
                gs.output("You have reached the edge of the world.")
                gs.ship.b.reset()

            # if we are navigating and we reached our destination...
            if gs.ship.b.is_target() and gs.ship.location == gs.ship.b.get():
                p = gs.map.get_place_at_location(gs.ship.location)
                if p:
                    d = p.name
                else:
                    d = "your destination"
                gs.output(f"You have reached {d}.")
                gs.ship.b.reset()