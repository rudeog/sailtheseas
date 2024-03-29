# this deals with commands that cause time to flow.
# The commands that cause time to move are sailing, resting and exploring.
# other encounters such as trading, battling, etc do not.
from state import gs


def pass_time():
    day_at_sea = gs.player.time_increment()

    # feed and water the crew if we are sailing and a day has elapsed
    if day_at_sea:
        _feed_crew()

    # see if the crew needs to be paid (every n days)
    pd = gs.crew.update_pay_due()
    if pd:
        gs.output(f"{gs.crew.boatswain}: Our crew of able-bodied seamen needs to be paid for their services. You will not be able to "
                  f"purchase anything or hire anyone until they are paid. Amount owed {gs.crew.amt_due()}D.")




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