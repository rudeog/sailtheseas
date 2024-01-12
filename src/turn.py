# this deals with commands that cause time to flow.
# The commands that cause time to move are sailing, resting and exploring.
# other encounters such as trading, battling, etc do not.
from player import PlayerState
from util import add_pair, get_step_towards_destination
from state import gs

def pass_time():
    gs.player.days=gs.player.days+1
    sail()


def sail():
    # if we are sailing we need to move if possible

    if gs.player.state is PlayerState.SAILING and gs.player.ship.bearing.is_set():
        if gs.player.ship.travel_pct < 100:
            gs.player.ship.travel_pct += 50
        if gs.player.ship.travel_pct >= 100:
            gs.player.ship.travel_pct = 0
            k,v = gs.player.ship.bearing.get()

            if k == gs.player.ship.bearing.Type.DIRECTION:
                coords = v.to_coords()
            else:
                coords = get_step_towards_destination(gs.player.ship.location, v)
            new_coords = add_pair(gs.player.ship.location, coords)
            loc = gs.map.get_location(new_coords)
            if loc:
                gs.player.ship.location = new_coords
                loc.visited = True
            else:
                gs.output("You have reached the edge of the world.")
                gs.player.ship.bearing.reset()

            # if we are navigating and we reached our destination...
            if k == gs.player.ship.bearing.Type.TARGET and gs.player.ship.location == v:
                p = gs.map.get_place_at_location(gs.player.ship.location)
                if p:
                    d = p.name
                else:
                    d = "your destination"
                gs.output(f"You have reached {d}.")
                gs.player.ship.bearing.reset()