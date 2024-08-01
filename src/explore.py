from state import gs
from util import choices_ex
import const
from cargo import CARGO_GOLD, CARGO_LUMBER, CARGO_LIVESTOCK

def _event_find_gold(island):
    gs.output("You find gold")
    gs.ship.cargo.add_remove(CARGO_GOLD, 10)

def _event_find_money(island):
    gs.output("You find money!")
    gs.player.add_remove_doubloons(100)

def _event_inane(island):
    gs.output("You see some birds n stuff")

def _event_lumber(island):
    gs.output("You find felled trees = lumber")
    gs.ship.cargo.add_remove(CARGO_LUMBER, 15)

def _event_livestock(island):
    gs.output("You find livestock")
    gs.ship.cargo.add_remove(CARGO_LIVESTOCK, 15)

def _event_loss_of_crew(island):
    gs.output("Some crew die")
    cur = gs.crew.seamen_count-10
    gs.crew.set_seamen_count(max(cur,0))

def _event_ship_damage(island):
    gs.output("While we were out exploring our ship was damaged")
    # TODO figure this out

class ExploreEvent:
    def __init__(self, fn, like):
        # what to do
        self.fn = fn
        # how likely to occur
        self.likelihood = like


# these are randomly generated explore events
explore_events = [
    ExploreEvent(_event_inane,7),
    ExploreEvent(_event_find_gold,1),
    ExploreEvent(_event_loss_of_crew,1),
    ExploreEvent(_event_find_money,1),
    ExploreEvent(_event_lumber,2),
    ExploreEvent(_event_livestock,2),
    ExploreEvent(_event_ship_damage,1),
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


    # eventually, various factors will influence the speed of exploration
    pctage = gs.rng_play.randint(20, 30)

    island.explored += pctage

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
