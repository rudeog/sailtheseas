from state import gs
from turn import pass_time

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
        pass_time()
        # eventually, various factors will influence the speed of exploration
        pctage = gs.rng_play.randint(5,15)
        island.explored += 10
        if island.explored > 100:
            island.explored = 100
        gs.gm_output(f"We have now explored {island.explored} percent of the island.")

