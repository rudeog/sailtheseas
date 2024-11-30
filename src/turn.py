# this deals with commands that cause time to flow.
# The commands that cause time to move are sailing, resting and exploring.
# other encounters such as trading, battling, etc do not.
import ship
from state import gs
from explore import do_explore

def pass_time(resting: bool, exploring: bool=False):
    day_elapsed = gs.player.time_increment()

    # ship takes wear and tear, and also may get repaired
    # may also possibly sink at this point causing game over
    if not _ship_set_cond():
        return

    # if we are sailing and a day has elapsed
    if day_elapsed:


        if gs.player.is_sailing():

            # possibly change wind direction
            gs.wind.change_random()
            gs.output(f"{gs.crew.lookout}: The wind is {gs.wind}, captain.")
            if gs.wind.speed==0:
                gs.output(f"{gs.crew.navigator}: We need wind to sail our ship!")

            # feed and water the crew (when on land they can find their own damn food)
            _feed_crew()
            gs.stock.check_important_stock(False)



    # see if the crew needs to be paid (every n days)
    pd = gs.crew.update_pay_due()
    if pd:
        gs.output(f"{gs.crew.boatswain}: Our crew of able-bodied seamen needs to be paid for their services. You will not be able to "
                  f"purchase anything or hire anyone until they are paid. Amount owed {gs.crew.amt_due()}D.")


    # if we are sailing we need to move if possible
    if not resting and gs.player.is_sailing() and gs.ship.b.is_set():
        _sail()

    # if exploring we need to explore
    if not resting and exploring and gs.player.is_onland():
        place = gs.map.get_place_at_location(gs.ship.location)
        if place and place.island:  # should be true
            do_explore(place.island)

def _ship_set_cond() -> bool:

    gs.ship.condition -= 1 # normal wear each watch

    # the carpenter is able to repair up to 2% damage each watch right now while sailing, and 4% while on land
    if gs.player.is_sailing():
        repair_amt = 2
    else:
        repair_amt = 4

    want = min(repair_amt,100 - gs.ship.condition)
    repaired = gs.stock.consume_materials(want)
    if repaired == 0:
        gs.output(f"{gs.crew.carpenter}: Captain, we were unable to perform repairs on {gs.ship.name}. We have no materials!")
    else:
        gs.ship.condition += repaired
    # if we did major repairs, let the captain know
    if repaired > 2:
        gs.output(f"{gs.crew.carpenter}: Captain we were able to do major repairs on {gs.ship.name}.")
    elif repaired > 1:
        gs.output(f"{gs.crew.carpenter}: Captain we were able to perform some minor repairs on {gs.ship.name}.")

    if gs.ship.condition <= 0:
        gs.ship.condition = 0
        gs.output(f"{gs.crew.lookout}: Captain, {gs.ship.name} is sinking!")
        gs.game_over=True
        return False
    elif gs.ship.condition < 20:
        gs.output(f"{gs.crew.carpenter}: Our ship is in poor condition, captain!")
    return True

def _sail():
    # make sure we are not overburdened
    if gs.ship.cargo.total_weight() >  gs.ship.cargo_capacity:
        gs.output(f"{gs.crew.firstmate}: {gs.ship.name} is overburdened with cargo! We can't sail.")
        gs.hints.show("jettison")
        return

    # figure out how many miles we will travel based on conditions, equipment and crew
    knots = 4
    dir_moving = gs.ship.direction_moving()
    # its possible that the above will return None if we are navigating and in the target square. no way right now to
    # determine direction
    sc = gs.wind.calc_speed_coeff(dir_moving)
    knots = knots * sc
    miles_available = round(6 * knots) # assumes 6 miles per knot
    knots = round(knots,1)
    sail_result, miles_traveled = gs.ship.sail(miles_available)
    if miles_traveled:
        if dir_moving:
            w = f"toward the {dir_moving} "
        else:
            w = ""
        gs.output(f"{gs.crew.boatswain}: {gs.ship.name} sails {miles_traveled} miles" 
                  f" {w}at an average speed of {knots} knots.")
    else:
        gs.output(f"{gs.crew.navigator}: Captain, despite our best efforts, we made no progress.")

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
        p.island.visit_count += 1
        if p.island.visit_count == 1:
            gs.gm_output("Here is some more information I found about the island:")
            gs.output(p.island.describe())
        gs.hints.show("arrived")
        gs.ship.b.reset() # reset bearing
    elif sail_result == gs.ship.SAIL_RESULT_ENTERED_NEW_SQUARE:
        loc = gs.map.get_location(gs.ship.location)
        if not loc.visited:
            loc.visited = True

        pl = gs.map.get_place_at_location(gs.ship.location)
        if pl:
            dist = gs.ship.distance_to_location(gs.ship.location)
            gs.output(f"{gs.crew.lookout}: I have sighted the island of {pl.island.name}!")
            gs.output(f"{gs.crew.navigator}: The island is {dist} miles away, captain.")
    gs.hints.show("sailing")


def _feed_crew():
    '''
    Feed crew, this includes water and medicine
    :return:
    '''
    hits = 0  # these are applied against the health of the crew
    f = gs.stock.consume_fluids()
    if f == -1: # no water or grog
        hits = 2
        gs.output(f"{gs.crew.firstmate}: Captain, we have run out of water! The crew is thirsty!")
    elif f==0:  # had water, no grog, crew becomes sadder
        gs.output("crew member: How do they expect us to sail this ship with no grog!")
        gs.crew.change_disposition(-1)
    elif f==2: # 2 = high level grog, crew becomes happier
        gs.crew.change_disposition(1)

    if not gs.stock.consume_medicine():
        gs.output(f"Surgeon {gs.crew.surgeon}: Captain, I am informing you that we are out of medical supplies.")
        hits = max(hits, 1) # take a hit unless we already have some

    rats = gs.stock.consume_rations()
    if not rats: # no food available
        hits = max(hits, 1) # take a hit unless we already have some
        gs.output(f"{gs.crew.cook}: We have run out of food, captain!")

    # if we had no hits then our health can go up
    if not hits:
        gs.crew.increase_health()
    else:
        gs.crew.decrease_health(hits)

    if f==2 and hits==0 and gs.crew.disposition >= 10:
        # the crew had extra grog and enough food and are not in a negative attitude
        cheer_the_captain()

cheer_idx=0
def cheer_the_captain():
    global cheer_idx
    cheers = [
        f"Three cheers for captain {gs.player.name}!",
        f"Captain {gs.player.name} is a jolly good fellow!",
        f"I'm proud to serve aboard {gs.ship.name}!",
        f"I wonder if all folks from {gs.player.birthplace} are as fine as captain {gs.player.name}.",
        f"Here's a toast to captain {gs.player.name}!",
        f"Another great day aboard {gs.ship.name}!"
    ]
    gs.output(f"crew member: {cheers[cheer_idx]}")
    cheer_idx += 1
    if cheer_idx >= len(cheers):
        cheer_idx=0