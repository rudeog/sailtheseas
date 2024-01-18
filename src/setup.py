#
# Do initial player setup. Ask player for info
#
from player import Player
from ship import Ship
from state import gs
import phrase_gen


# this should only store what is asked
def player_setup():
    gs.output(
        f"Welcome to {gs.world_name}. Lets get started. At any time you may enter '!' to quit.")
    n = gs.input("What name will you be using? ")
    if n == '!':
        return False

    gs.player.name = n

    n = gs.input(
        f"{phrase_gen.get_phrase(gs.player.name, phrase_gen.player_name_phrases)} where are you from? ")

    if n == '!':
        return False

    gs.player.birthplace = n
    print(phrase_gen.get_phrase(gs.player.birthplace, phrase_gen.places_phrases))
    n = input("What you want to name your ship? ")

    if n == '!':
        return False
    gs.ship.name = n
    print(phrase_gen.get_phrase(gs.ship.name, phrase_gen.ship_name_phrases))

    print("You are ready to start your adventures! Best of luck to you.")

    return True


def set_player_start_location():
    start_loc = gs.map.places[0]
    gs.ship.set_location(start_loc.location)
    # we will be docked at the port
    gs.player.set_state_docked()
    gs.ship.b.reset()
    gs.map.places[0].visited = True
