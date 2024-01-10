#
# Do initial player setup. Ask player for info
#
import player
from state import gs
import phrase_gen


def player_setup():
    gs.player = player.Player()
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
    gs.player.ship.name = n
    print(phrase_gen.get_phrase(gs.player.ship.name, phrase_gen.ship_name_phrases))

    print("You are ready to start your adventures! Best of luck to you.")

    return True


def set_player_start_location():
    start_loc = gs.map.places[0]
    gs.player.ship.location = start_loc.location
    # we will be docked at the port
    gs.player.state = player.PlayerState.DOCKED
    gs.player.ship.reset_bearing()
    gs.map.places[0].visited = True
