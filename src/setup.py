#
# Do initial player setup. Ask player for info
#
import logging
import random

import crew
import state
from names import NameGenerator, PlaceGenerator
from place_descriptions import DescriptionGenerator
from state import gs, NUM_QUESTS, NUM_QUEST_CLUES, NUM_QUEST_ARTIFACTS
import phrase_gen
from stock import do_full_restock
from util import as_int
from crew import NUM_ROLES, pay_description
import quest

# this should generate the map, set up the rng's and the game master
# based on info we have either gotten from user or from save file
def base_setup():
    name_gen = NameGenerator(gs.seed)
    place_gen = PlaceGenerator(gs.seed)

    gs.rng_play = random.Random(gs.seed)
    gs.name_gen = NameGenerator(gs.seed+1)

    gs.desc_gen = DescriptionGenerator(gs.seed+2, gs.name_gen, place_gen)

    # we should end up with the same name and place as was selected in determine seed
    gs.emperor = name_gen.name("m", "e")
    gs.game_master = name_gen.name("m", "w")
    gs.world_name = place_gen.name('f')


def quest_setup():
    qg = quest.QuestGenerator(gs.seed)
    gs.quests = []
    for i in range(NUM_QUESTS):
        q = qg.generate(gs.map,NUM_QUEST_ARTIFACTS[i], NUM_QUEST_CLUES)
        gs.quests.append(q)

# This should find out what seed the user wants to use
def determine_seed() -> bool:
    start = 0
    while True:
        gs.output("Please select which world you will visit and who will be your Game Master:")
        for i in range(start, start + 10):
            temp_ng = NameGenerator(gs.seed + i)
            temp_pg = PlaceGenerator(gs.seed + i)
            emperor = temp_ng.name("m", "e")
            gm = temp_ng.name('m', 'w')
            world = temp_pg.name('f').name
            gs.output(f"{str(i).rjust(2)} {world} "
                      f"(Emperor: {emperor.last} "
                      f"GM: {gm})")
        while True:
            sel = gs.input("Enter a number or 'm' for more choices or ! to quit: ")
            if sel == '!':
                return False
            if sel.lower() == 'm':
                break
            nsel = as_int(sel)
            if nsel < 0:
                gs.output("That was an invalid choice")
            else:
                gs.seed = gs.seed + nsel
                return True

        start += 10


# this should only store what is asked
def player_setup() -> bool:
    gs.gm_output(
        f"Welcome to the world of {gs.world_name} which is ruled by emperor {gs.emperor}. I, {gs.game_master} will "
        "be your game master, and will facilitate "
        f"your adventures as you sail the seas of {gs.world_name}.")
    gs.output("Lets get started. At any time you may enter '!' to quit.")
    n = gs.input("What name will you be using? ")
    if n == '!':
        return False

    gs.player.name = n
    gs.output("")
    n = gs.gm_input(
        f"{phrase_gen.get_phrase(gs.player.name, phrase_gen.player_name_phrases)} where are you from? ")

    if n == '!':
        return False

    gs.player.birthplace = n
    gs.output("")
    gs.gm_output(phrase_gen.get_phrase(gs.player.birthplace, phrase_gen.places_phrases))
    n = gs.input("What do you want to name your ship? ")

    if n == '!':
        return False
    gs.ship.name = n
    gs.output("")
    gs.gm_output(phrase_gen.get_phrase(gs.ship.name, phrase_gen.ship_name_phrases))

    gs.player.add_remove_doubloons(state.DEFAULT_STARTING_DOUBLOONS)
    gs.gm_output(f"You will start the game with {state.DEFAULT_STARTING_DOUBLOONS} doubloons (D).")

    if not setup_crew():
        return False
    if not setup_abs():
        return False
    gs.output(f"{gs.crew.firstmate}: We need to stock our ship with necessary supplies for sailing. The crew needs "
              f"to be fed and watered. If we have grog on hand, it can be rationed. Medical supplies help to keep "
              f"the crew healthy. Materials are needed to do routine maintenance on the ship as well as repairs in "
              f"the event of damage. Ordnance is necessary if {gs.ship.name} gets into a battle at sea.")
    if gs.gm_confirm(f"You may fully stock your ship now, or you may customize how it is stocked using "
                     f"the 'restock' command. Do you want to fully stock {gs.ship.name} now?", cancel=False):
        spent = do_full_restock()
        if spent:
            gs.gm_output(f"You spent {spent}D to fully stock {gs.ship.name}.")
        else:
            gs.gm_output(f"Well, it looks like you don't have enough doubloons to fully stock the ship.")
    gs.output("")
    return True


def set_player_start_location():
    start_loc = gs.map.places[0]
    gs.ship.set_location(start_loc.location)
    # we will be docked at the port
    gs.player.set_state_landed()
    gs.ship.b.reset()
    gs.map.places[0].visited = True
    gs.map.places[0].island.visit_count = 1
    gs.player.add_to_visited(0)



def setup_crew() -> bool:
    gs.output("")
    gs.gm_output(
        f"It's time to fill the positions of the {NUM_ROLES} main crew members. You may choose whomever you like: "
        "friends, family members, etc.")
    for i in range(NUM_ROLES):
        if not hire_crewmember(i):
            return False

    gs.gm_output("This is what your main crew looks like.")

    while True:
        gs.output("")
        gs.crew.describe_named(True)

        i = gs.input_num(1, NUM_ROLES, "Enter a number modify an entry, or $ when finished")
        gs.output("")
        if i < 1:
            if gs.quitting:
                return False
            return True

        if not hire_crewmember(i - 1):
            return False


def hire_crewmember(i):
    cr = gs.crew.get_by_idx(i)
    gs.output(f"The {crew.roles[i]} - {crew.role_desc[i]}")
    n = gs.gm_input(f"Who are you hiring as {crew.roles[i]}: ")
    if n == '!':
        return False
    if n.strip() != '':
        gs.gm_output(phrase_gen.get_phrase(n, phrase_gen.crew_name_phrases))
        cr.name = n
    return True

def setup_abs():
    gs.output(f"{gs.crew.boatswain}: As boatswain of this ship, the crew is my responsibility. The ship needs a crew "
              f"of able-bodied seamen (ABS) to keep it sailing and in good working order. {crew.pay_description()} "
              f"You currently have {gs.player.doubloons}D. "
              "How many ABS will you hire?")
    while True:
        nc = gs.input_num(state.ABS_COUNT_NONFUNCTIONAL + 1, state.ABS_COUNT_MAX, nocancel=True)
        if gs.quitting:
            return False

        gs.crew.set_seamen_count(nc)
        gs.crew.update_pay_due()
        pd = gs.crew.pay_crew()
        gs.output(f"{gs.crew.boatswain}: We hired {nc} ABS and paid them "
                  f"up-front for {state.ABS_PAY_PERIOD} days at an amount of {pd}D.")
        return True

# create the initial set of cargo at each port
def init_trading_data():

    for loc in gs.map.places:
        if loc.island and loc.island.port and loc.island.port.trader:
            t = loc.island.port.trader
            logging.log('trade',f'initialize trading data for {loc.index}')
            t.update()