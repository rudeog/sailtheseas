#
# Do initial player setup. Ask player for info
#

from state import gs, GAME_NAME
import phrase_gen


# this should only store what is asked
def player_setup():
    gs.game_master = gs.name_gen.name("m","w")
    gs.world_name = gs.place_gen.name()
    gs.gm_output(
        f"Welcome to {GAME_NAME}. I, {gs.game_master} will be your game master, and will facilitate "
        f"your adventures as you sail the seas in the world of {gs.world_name}.")
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
