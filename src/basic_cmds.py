# command file for ship commands

def list_cargo(gs, toks):
    for item in gs.player.cargo:
        print(item)

def show_status(gs, toks):
    print(f"Captain {gs.player.name} who hails from {gs.player.birthplace} is on day {gs.player.days} of their voyage."
          f"The {gs.player.ship_name} is in fine condition")
    print("Sunny skies and windy winds, etc, etc.")