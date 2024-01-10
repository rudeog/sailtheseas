# this deals with commands that cause time to flow.
# The commands that cause time to move are sailing, resting and exploring.
# other encounters such as trading, battling, etc do not.
from player import PlayerState
from util import add_pair, get_step_towards_destination
from state import gs

def pass_time():
    gs.player.days=gs.player.days+1
    # if we are sailing we need to move if possible
    if gs.player.state is PlayerState.SAILING and gs.player.ship.have_bearing():
        if gs.player.ship.travel_pct < 100:
            gs.player.ship.travel_pct += 50
        if gs.player.ship.travel_pct >= 100:
            gs.player.ship.travel_pct=0
            if gs.player.ship.direction:
                coords = gs.player.ship.direction.to_coords()
            else:
                coords = get_step_towards_destination(gs.player.ship.location,gs.player.ship.target)
            new_coords = add_pair(gs.player.ship.location, coords)
            loc = gs.map.get_location(new_coords)
            if loc:
                gs.player.ship.location = new_coords
                loc.visited = True
            else:
                gs.output("You have reached the edge of the world.")
                gs.player.ship.reset_bearing()

            # if we are navigating and we reached our destination...
            if not gs.player.ship.direction and gs.player.ship.location == gs.player.ship.target:
                p = gs.map.get_place_at_location(gs.player.ship.location)
                if p:
                    d = p.name
                else:
                    d = "your destination"
                gs.output(f"You have reached {d}.")
                gs.player.ship.reset_bearing()

