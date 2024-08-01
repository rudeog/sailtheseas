from state import gs
from turn import pass_time
from util import choices_ex
import const

# these are randomly generated explore events
explore_events = [
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
    else:
        pass_time(False)
        # eventually, various factors will influence the speed of exploration
        pctage = gs.rng_play.randint(25,35)
        island.explored += pctage
        quest_find=choices_ex(gs.rng_play, [True, False], [5,4])
        if island.explored >= 100:
            island.explored = 100
            quest_find=True # if we haven't found it by now, we must find it

        if island.quest_item and not island.quest_item.found and quest_find:
            island.quest_item.found=True
            if island.quest_item.is_clue():
                if island.civ_type != const.ISLAND_CIV_UNINHABITED:
                    n = gs.name_gen.name("",island.ethnicity)
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
                if msg: # the quest is completed
                    gs.gm_output(msg)


        gs.gm_output(f"We have now explored {island.explored} percent of the island.")

