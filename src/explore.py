from state import gs
from util import choices_ex
import const
from cargo import CARGO_GOLD, CARGO_LUMBER, CARGO_LIVESTOCK

def _event_find_gold(island):
    o=gs.desc_gen.explore_island_gold(island)
    amt=choices_ex(gs.rng_play,[2,3,4,5],[6,4,3,1])
    gs.ship.cargo.add_remove(CARGO_GOLD, amt)
    gs.output(f"{o} You gain {amt} pounds of gold.")

def _event_find_money(island):
    o=gs.desc_gen.explore_island_doubloons(island)
    amt=choices_ex(gs.rng_play,[100,200,300,400],[6,4,3,1])
    gs.output(f"{o} You gain {amt} doubloons.")
    gs.player.add_remove_doubloons(amt)

def _event_inane(island):
    o=gs.desc_gen.explore_island_inane(island)
    gs.output(o)

def _event_lumber(island):
    o=gs.desc_gen.explore_island_lumber(island)
    amt=choices_ex(gs.rng_play,[50,100],[3,1])
    gs.output(f"{o} You gain {amt} tons of lumber.")
    gs.ship.cargo.add_remove(CARGO_LUMBER, amt)

def _event_livestock(island):
    o=gs.desc_gen.explore_island_livestock(island)
    amt=choices_ex(gs.rng_play,[20,50],[3,1])
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
    ExploreEvent(_event_inane,11),
    # gain gold
    ExploreEvent(_event_find_gold,1),
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
temp = [
    # inane:
    "Animal sighting",
    "Plant sighting",
    "Geological sighting",
    "Words with locals",

    # setbacks
    "Crew is killed by animal",
    "Crew eat poisonous plant and die",
    "Crew fall down pit/off cliff/into crevace/off mountain and die",
    "Crew defect to live with locals",
    "Ship is raided by bandits, loss of random cargo",
    "Ship is damaged by hooligans/weather, cost in D to repair ship",

    # bonuses gold
    "Find gold from pirates",
    "Find surface nuggets (gold)",
    "Pan for gold in a stream (gold)",
    # bonuses doubloons
    "Find doubloons from pirates",
    "Find abandoned shack with doubloons",
    # bonuses lumber, livestock
    "Find a fallen tree which is sawn into lumber",
    "Find antelope,wild sheep, feral hogs, cattle (livestock)",
]

# fixed explore events
fixed = [
    "You find a clue to where an artifact exists",
    "You find an artifact related to a quest",
    "You find a quest location",
    "You find a clue to where a quest location is",

]


def do_explore(island):

    if island.explored >= 100:
        gs.gm_output(f"It looks like you have already explored the entire island of {island.name}.")
        return


    # add some percentage to exploration
    # eventually, various factors will influence the speed of exploration
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
        else:
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
    return True
