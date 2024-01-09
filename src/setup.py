#
# Do initial player setup. Ask player for info
#
import player
from state import global_state
import phrase_gen


def player_setup():
    global_state.player = player.Player()
    global_state.output(
        f"Welcome to {global_state.world_name}. Lets get started. At any time you may enter '!' to quit.")
    n = global_state.input("What name will you be using? ")
    if n == '!':
        return False

    global_state.player.name = n

    n = global_state.input(
        f"{phrase_gen.get_phrase(global_state.player.name, phrase_gen.player_name_phrases)} where are you from? ")

    if n == '!':
        return False

    global_state.player.birthplace = n
    print(phrase_gen.get_phrase(global_state.player.birthplace, phrase_gen.places_phrases))
    n = input("What you want to name your ship? ")

    if n == '!':
        return False
    global_state.player.ship.name = n
    print(phrase_gen.get_phrase(global_state.player.ship.name, phrase_gen.ship_name_phrases))

    print("You are ready to start your adventures! Best of luck to you.")

    return True
