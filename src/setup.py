#
# Do initial player setup. Ask player for info
#
from names import NameGenerator, PlaceGenerator
from state import gs, GAME_NAME, MAP_WIDTH, MAP_HEIGHT
from map import Map
import phrase_gen

# this should generate the map, set up the rng's and the game master
# based on info we have either gotten from user or from save file
def base_setup():
    gs.name_gen = NameGenerator(gs.seed)
    gs.place_gen = PlaceGenerator(gs.seed)
    # we should end up with the same name and place as was selected in determine seed
    gs.emperor = gs.name_gen.name("m","e")
    gs.game_master = gs.name_gen.name("m","w")
    gs.world_name = gs.place_gen.name('f')
    # generate the map
    gs.map = Map(MAP_WIDTH, MAP_HEIGHT, gs.seed)

    if gs.debug_mode:
        print("Islands:")
        for isl in gs.map.places:
            print(f"{isl.island.name} - {isl.island.summary()}")

# This should find out what seed the user wants to use
def determine_seed() -> bool:
    start = 0
    while True:
        gs.output("Please select which world you will visit and who will be your Game Master:")
        for i in range(start,start+10):
            temp_ng = NameGenerator(gs.seed+i)
            temp_pg = PlaceGenerator(gs.seed+i)
            emperor = temp_ng.name("m","e")
            gm = temp_ng.name('m','w')
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
            try:
                nsel = int(sel)
                gs.seed = gs.seed + nsel
                return True
            except ValueError:
                gs.output("That was an invalid choice")

        start += 10



# this should only store what is asked
def player_setup() -> bool:

    gs.gm_output(
        f"Welcome to the world of {gs.world_name}. I, {gs.game_master} will be your game master, and will facilitate "
        f"your adventures as you sail the seas. {gs.world_name} is ruled by emperor {gs.emperor}.")
    gs.output("Lets get started. At any time you may enter '!' to quit.")
    n = gs.input("What name will you be using? ")
    if n == '!':
        return False

    gs.player.name = n

    n = gs.gm_input(
        f"{phrase_gen.get_phrase(gs.player.name, phrase_gen.player_name_phrases)} where are you from? ")

    if n == '!':
        return False

    gs.player.birthplace = n
    gs.gm_output(phrase_gen.get_phrase(gs.player.birthplace, phrase_gen.places_phrases))
    n = gs.input("What you want to name your ship? ")

    if n == '!':
        return False
    gs.ship.name = n
    gs.gm_output(phrase_gen.get_phrase(gs.ship.name, phrase_gen.ship_name_phrases))

    gs.output("You are ready to start your adventures! Best of luck to you.")

    return True


def set_player_start_location():
    start_loc = gs.map.places[0]
    gs.ship.set_location(start_loc.location)
    # we will be docked at the port
    gs.player.set_state_docked()
    gs.ship.b.reset()
    gs.map.places[0].visited = True
