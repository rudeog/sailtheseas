#
# Do initial player setup. Ask player for info
#
import random

import crew
import state
from names import NameGenerator, PlaceGenerator
from state import gs, GAME_NAME, MAP_WIDTH, MAP_HEIGHT
from map import Map
import phrase_gen
from util import as_int
from crew import NUM_ROLES


# this should generate the map, set up the rng's and the game master
# based on info we have either gotten from user or from save file
def base_setup():
    gs.name_gen = NameGenerator(gs.seed)
    gs.place_gen = PlaceGenerator(gs.seed)
    gs.rng_play = random.Random(gs.seed)
    # we should end up with the same name and place as was selected in determine seed
    gs.emperor = gs.name_gen.name("m", "e")
    gs.game_master = gs.name_gen.name("m", "w")
    gs.world_name = gs.place_gen.name('f')


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
    n = gs.input("What you want to name your ship? ")

    if n == '!':
        return False
    gs.ship.name = n
    gs.output("")
    gs.gm_output(phrase_gen.get_phrase(gs.ship.name, phrase_gen.ship_name_phrases))

    if not setup_crew():
        return False

    gs.player.add_remove_doubloons(10000)  # temporary
    gs.output("You are ready to start your adventures! Best of luck to you.")

    return True


def set_player_start_location():
    start_loc = gs.map.places[0]
    gs.ship.set_location(start_loc.location)
    # we will be docked at the port
    gs.player.set_state_landed()
    gs.ship.b.reset()
    gs.map.places[0].visited = True


def setup_crew() -> bool:
    gs.output("")
    gs.crew.seamen_count = state.DEFAULT_ABS_COUNT
    gs.gm_output(f"It's time to hire your {NUM_ROLES} main crew members. You may hire whomever you like: "
                 "friends, family members, etc.")
    for i in range(NUM_ROLES):
        if not hire_crewmember(i):
            return False

    gs.gm_output("This is what your main crew looks like.")

    while True:
        gs.output("")
        gs.crew.describe_named(True)

        v = gs.input(f"To change an entry, enter a number from 1 to {NUM_ROLES}. When done, enter 'done'. Enter ! to quit the game: ")
        gs.output("")
        if v.lower() == 'done':
            cc = 0
            for ii in range(NUM_ROLES):
                if gs.crew.get_by_idx(ii).name:
                    cc += 1
            if cc == NUM_ROLES:
                return True
            else:
                gs.gm_output(
                    "You have not yet assigned all the roles. Please do so.")
        elif v == '!':
            return False
        else:
            i = as_int(v, 0)
            if i < 1 or i > NUM_ROLES:
                gs.gm_output(f"Really, {gs.player.name}, is it that hard to enter a number between 1 and {NUM_ROLES}?")
            else:
                i -= 1

                if not hire_crewmember(i):
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


def do_crew_assign():
    named = False
    for i in range(NUM_ROLES):
        cr = gs.crew.get_by_idx(i)
        if not cr.name:
            named = True
            name = gs.name_gen.name('m', 'w')
            cr.name = name.first + " " + name.last

    if not named:
        gs.gm_output("It looks like you already have all positions filled. Just enter 'done' if you are satisfied.")
