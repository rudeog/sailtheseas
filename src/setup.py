import state
import phrase_gen

def do_setup(player):
    print("Welcome to port Felchy. Lets get started. At any time you may enter 'q' to quit.")
    n = input("What name will you be using? ")

    if n.lower() == 'q':
        return False

    player.name = n

    n=input(f"{phrase_gen.get_phrase(player.name, phrase_gen.player_name_phrases)} where are you from? ")

    if n.lower() == 'q':
        return False

    player.birthplace = n
    print(phrase_gen.get_phrase(player.birthplace, phrase_gen.places_phrases))
    n=input("What you want to name your ship? ")

    if n.lower() == 'q':
        return False
    player.ship_name = n
    print(phrase_gen.get_phrase(player.ship_name, phrase_gen.ship_name_phrases))

    print("You are ready to start your voyage! Best of luck to you.")

    return True