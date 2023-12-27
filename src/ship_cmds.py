
def list_cargo(player, toks):
    for item in player.cargo:
        print(item)

def show_status(player, toks):
    print(f"Captain {player.name} who hails from {player.birthplace} is on day {player.days} of their voyage."
          f"The {player.ship_name} is in fine condition")
    print("Sunny skies and windy winds, etc, etc.")