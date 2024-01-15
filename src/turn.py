# this deals with commands that cause time to flow.
# The commands that cause time to move are sailing, resting and exploring.
# other encounters such as trading, battling, etc do not.
from util import add_pair, get_step_towards_destination
from state import gs

def pass_time():
    gs.player.time_increment()
    sail()


def sail():
    # if we are sailing we need to move if possible

    if gs.player.is_sailing() and gs.ship.b.is_set():
        # figure out how many miles we will travel based on conditions, equipment and crew
        miles_available = 24 # assumes 4 knots
        # 60 miles is the distance of one square horizontal or vertical.
        # 85 miles is the diagonal distance
        # so 30 miles from left/right/up/down to center and 42 miles from diagonal
        # we only count diagonal miles when traveling TO center. It is more difficult for traveling away,
        # because if they shift directions while traveling from a diagonal to a non-diagonal. Therefore
        # when entering from diagonal we add these extra miles on. Normally it would be 42 miles from diagonal
        # to center, so we make it 54 miles = 30 + ( (42-30) * 2  )
        arrived = False  # will be set to true if we are navigating and reach our dest
        hit_edge = False  # will be set to true if we hit the edge of the world

        # there is an edge case where we are moving away from center but we are now navigating to that center.
        # eg we reached center, passed it, are on the same square and now have nav set to that square
        if gs.ship.b.is_target() and gs.ship.b.get() == gs.ship.location and not gs.ship.toward_center:
            gs.ship.toward_center = True
            # diagonal will be false here
            gs.ship.miles_traveled_in_square = 30 - gs.ship.miles_traveled_in_square

        while miles_available: # chew thru miles until we have exhausted them or reached a target
            dist_to_center = 30
            if gs.ship.diagonal_entry:
                dist_to_center = 54
            to_target = dist_to_center - gs.ship.miles_traveled_in_square
            if miles_available < to_target: # just advance toward center or edge
                gs.ship.miles_traveled_in_square += miles_available
                break
            else:  # we reached the center, or the edge of a square
                miles_available -= to_target
                gs.ship.miles_traveled_in_square = 0
                if gs.ship.toward_center:
                    # reached center, so start moving away from center next
                    gs.ship.toward_center = False
                    gs.ship.diagonal_entry = False
                    if gs.ship.b.is_target() and gs.ship.location == gs.ship.b.get():
                        # throw away rest of miles we are done navigating to target
                        arrived = True
                        break
                else:  # reached edge of square so move to next square
                    gs.ship.toward_center = True
                    # we move to a new square or hit the edge
                    if gs.ship.b.is_direction():
                        coords = gs.ship.b.get().to_coords()
                    else:
                        coords = get_step_towards_destination(gs.ship.location, gs.ship.b.get())
                    # if both are either 1 or -1 we are entering on a diagonal and must travel further
                    # to get to center of the new square
                    is_diagonal = (coords[0] and coords[1])
                    gs.ship.diagonal_entry = is_diagonal
                    new_coords = add_pair(gs.ship.location, coords)
                    loc = gs.map.get_location(new_coords)
                    if loc:
                        gs.ship.location = new_coords
                        loc.visited = True
                    else:
                        # hit edge so throw away rest of miles
                        hit_edge = True
                        break

        if hit_edge:
            gs.output("You have reached the edge of the world. Please choose a new direction or target.")
            gs.ship.b.reset() # stop navigating, the player must determine what to do next
            # and they must move back to center of square before going anywhere else

        # if we are navigating and we reached our destination...
        if arrived:
            p = gs.map.get_place_at_location(gs.ship.location)
            if p:
                d = p.name
            else:
                d = "your destination"
            gs.output(f"You have reached {d}.")
            gs.ship.b.reset()