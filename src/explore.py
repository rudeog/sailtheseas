from state import AVG_VALUE_EXPLORE_ITEM, gs
from util import choices_ex
import const
from cargo import cargo_types, CARGO_GOLD, CARGO_LUMBER, CARGO_LIVESTOCK, CARGO_FOOD

# the general rule is that if we find something of value it should be
# approximately valued at AVG_VALUE_EXPLORE_ITEM

def _get_range_for_cargo_type(ct):
    avg_units = int( AVG_VALUE_EXPLORE_ITEM / cargo_types[ct].price_coefficient)
    if avg_units <= 1: # probably gold
        return [1,2],[3,1]
    if avg_units == 2:
        return [1,2,3],[1,3,1]
    return [int(avg_units/2),avg_units,int(avg_units*2)],[1,3,1]


def _event_find_gold(island):
    o=gs.desc_gen.explore_island_gold(island)
    ranges = _get_range_for_cargo_type(CARGO_GOLD)
    amt=choices_ex(gs.rng_play,ranges[0],ranges[1])
    gs.ship.cargo.add_remove(CARGO_GOLD, amt)
    gs.output(f"{o} You gain {amt} pounds of gold.")

def _event_find_money(island):
    o=gs.desc_gen.explore_island_doubloons(island)
    amt=choices_ex(gs.rng_play,
                   [int(AVG_VALUE_EXPLORE_ITEM/2),AVG_VALUE_EXPLORE_ITEM,int(AVG_VALUE_EXPLORE_ITEM*2)],
                   [1,3,1])
    gs.output(f"{o} You gain {amt} doubloons.")
    gs.player.add_remove_doubloons(amt)

def _event_inane(island):
    o=gs.desc_gen.explore_island_inane(island)
    gs.output(o)

def _event_lumber(island):
    o=gs.desc_gen.explore_island_lumber(island)
    ranges = _get_range_for_cargo_type(CARGO_LUMBER)
    amt=choices_ex(gs.rng_play,ranges[0],ranges[1])
    gs.output(f"{o} You gain {amt} tons of lumber.")
    gs.ship.cargo.add_remove(CARGO_LUMBER, amt)

def _event_find_food(island):
    o=gs.desc_gen.explore_island_food(island)
    ranges = _get_range_for_cargo_type(CARGO_FOOD)
    amt=choices_ex(gs.rng_play,ranges[0],ranges[1])
    gs.output(f"{o} You gain {amt} barrels of preserved food.")
    gs.ship.cargo.add_remove(CARGO_FOOD, amt)

def _event_livestock(island):
    o=gs.desc_gen.explore_island_livestock(island)
    ranges = _get_range_for_cargo_type(CARGO_LIVESTOCK)
    amt=choices_ex(gs.rng_play,ranges[0],ranges[1])
    gs.output(f"{o} You gain {amt} head of livestock.")
    gs.ship.cargo.add_remove(CARGO_LIVESTOCK, amt)

def _event_loss_of_crew(island):
    o=gs.desc_gen.explore_island_crewloss(island)
    amt=choices_ex(gs.rng_play,[5,10],[3,1])
    gs.output(f"{o} You lose {amt} able-bodied seamen.")
    cur = gs.crew.seamen_count-amt
    gs.crew.set_seamen_count(max(cur,0))

def _event_ship_damage(island):
    o=gs.desc_gen.explore_island_shipdamage(island)
    gs.output(f"{o} TODO figure out ship damage.")


class ExploreEvent:
    def __init__(self, fn, like):
        # what to do
        self.fn = fn
        # how likely to occur
        self.likelihood = like


# these are randomly generated explore events
explore_events = [
    # inane events have no effect
    ExploreEvent(_event_inane,10),
    # gain gold
    ExploreEvent(_event_find_gold,1),
    # gain preserved food
    ExploreEvent(_event_find_food,3),
    # lose crew
    ExploreEvent(_event_loss_of_crew,2),
    # gain doubloons
    ExploreEvent(_event_find_money,2),
    # gain lumber
    ExploreEvent(_event_lumber,4),
    # gain livestock
    ExploreEvent(_event_livestock,5),
    # ship gets damaged
    ExploreEvent(_event_ship_damage,2),
    ]


    # setbacks
    #"Crew is killed by animal",
    #"Crew eat poisonous plant and die",
    #"Crew fall down pit/off cliff/into crevace/off mountain and die",
    #"Crew defect to live with locals",
    #"Ship is raided by bandits, loss of random cargo",
    #"Ship is damaged by hooligans/weather, cost in D to repair ship",



# fixed explore events
#
#    "You find a clue to where an artifact exists",
#    "You find an artifact related to a quest",
#    "You find a quest location",
#    "You find a clue to where a quest location is",
#



def do_explore(island):

    if island.explored >= 100:
        gs.gm_output(f"It looks like you have already explored the entire island of {island.name}.")
        return


    # add some percentage to exploration
    # eventually, various factors will influence the speed of exploration.
    # faster exploration means less items found
    pctage = gs.rng_play.randint(10, 25)

    island.explored += pctage
    if island.explored > 100:
        island.explored = 100

    # if there is a quest item here we will need to find it as one of our explorations
    if not do_quest_find(island):
        # find something else to do
        event = choices_ex(gs.rng_play, explore_events, [x.likelihood for x in explore_events])
        event.fn(island)


    gs.gm_output(f"We have now explored {island.explored} percent of the island.")

def do_quest_find(island):
    if not island.quest_item or island.quest_item.found:
        return False # nothing to do here

    # randomly decide whether we find it on this go round
    quest_find = choices_ex(gs.rng_play, [True, False], [5, 4])
    if island.explored >= 100:
        island.explored = 100
        quest_find = True  # if we haven't found it by now, we must find it

    if not quest_find:
        return False

    island.quest_item.found = True
    if island.quest_item.is_clue():
        if island.civ_type != const.ISLAND_CIV_UNINHABITED:
            n = gs.name_gen.name("", island.ethnicity)
            clue_pre = f"Local resident {n.first}:"
        else: # there are no people here, so its found in a bottle
            clue_pre = "Message found in a bottle:"
        gs.gm_output("It appears that you have found a clue!")
        gs.output(f"{clue_pre} {island.quest_item.name}")
    elif island.quest_item.is_artifact():
        gs.gm_output(f"You have found {island.quest_item.name}!")
    elif island.quest_item.is_target():
        gs.gm_output(f"You have found {island.quest_item.name}!")
        q = island.quest_item.quest
        msg = q.check_completed(island.island_index)
        if msg:  # the quest is completed
            gs.gm_output(msg)
    gs.hints.show("quest_item")
    return True
