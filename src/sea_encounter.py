from state import NUM_PIRATES
from state import gs
#
#
#

def check_encounter():
    '''
    This will check to see if we have a sea encounter. if so, we go into the sea encounter
    loop which is modal and only ends with victory, defeat, evasion, or enemy evasion
    :return:
    '''

    roll = gs.rng_play.randint(1, 8)
    if roll == 8:
        gs.output(f"{gs.crew.lookout}: We have sighted a sea creature!")
    elif roll == 7:
        s = gs.rng_play.randint(0, NUM_PIRATES-1)
        tmp = gs.pirates[s:] + gs.pirates[:s]
        for p in tmp:
            if not p.completed:
                pirate_encounter(p)
                break

def pirate_encounter(p):
    counter=0
    gs.output(f"{gs.crew.lookout}: We have sighted {p.ship_name} belonging to {p.name}! (Condition {p.health}%)")
    while True:
        counter+=1
        gs.output(f"{gs.crew.firstmate}: We have {gs.stock.get_ordnance()} ordnance remaining.")
        gs.output(f"{gs.crew.carpenter}: The condition of {gs.ship.name} is at {gs.ship.condition}%.")
        gs.output(f"{gs.crew.boatswain}: We have {gs.crew.seamen_count} able bodied seamen.")

        gs.output(f"{gs.crew.gunner}: What will you do?")
        sel = gs.input_num(1,2,f"1) Do battle with {p.name}, 2) Attempt to flee",True,'',True)
        if sel == 2:
            if gs.rng_play.randint(0,2):
                gs.output(f"{gs.crew.gunner}: We have successfully fled from {p.name} and his crew.")
                break
            else:
                gs.output(f"{gs.crew.gunner}: We have failed to flee from {p.name}!")
        else:
            damage = 0
            if gs.stock.consume_ordnance():
                gs.gm_output(f"{gs.ship.name} fires a volley at the pirate ship.")
                damage = gs.rng_play.randint(10,20)
            else:
                gs.output(f"{gs.crew.firstmate}: We have no ordnance remaining!")
                gs.gm_output(f"{gs.ship.name} attempts to ram the pirate ship.")
                damage = gs.rng_play.randint(3,7)

            p.health -= damage
            if p.health <= 0:
                p.health = 0
                p.completed = True
                gs.output(f"{gs.crew.gunner}: We have destroyed {p.ship_name} and defeated {p.name}!")
                break
            else:
                gs.output(f"{gs.crew.gunner}: {p.ship_name} has been hit and taken {damage} damage! ({p.health} remaining.)")



        # pirates turn
        insult = gs.desc_gen.pirate_insult()
        gs.output(f"{p.name}: {insult}")
        gs.gm_output(f"{p.ship_name} fires a volley at your ship.")
        damage = gs.rng_play.randint(7,14)
        gs.ship.condition -= damage
        gs.output(f"{gs.crew.carpenter}: {gs.ship.name} has been hit and taken {damage} damage! ({gs.ship.condition} remaining.)")
        rr = gs.rng_play.randint(0,6)
        if rr==0:
            gs.output(f"{gs.crew.chaplain}: I pray for our souls!")
        elif rr == 1:
            gs.output(f"{gs.crew.boatswain}: All hands on deck!")
        elif rr == 2:
            gs.output(f"{gs.crew.carpenter}: Our timbers!")
        else:
            amt=gs.rng_play.randint(1,5)
            if gs.crew.seamen_count-amt >= 0:
                gs.output(f"{gs.crew.surgeon}: We have lost {amt} able-bodied seamen!")
                cur = gs.crew.seamen_count-amt
                gs.crew.set_seamen_count(max(cur,0))
        if gs.ship.condition <= 0:
            gs.ship.condition = 0
            gs.output(f"{gs.crew.lookout}: Captain, {gs.ship.name} is sinking!")
            gs.game_over=True
            break

