# this is for doing manual tests
from player import Player
from ship import Ship
from status_cmds import show_status
from state import gs
from setup import base_setup
from command import RunType
import islands


def initial_setup():
    # initialize our global obj (due to circular refs issue)
    gs.player = Player()
    gs.ship = Ship()

    # initialize needed stuff
    gs.player.name = "player name"
    gs.player.birthplace = "player birthplace"
    gs.player.add_remove_doubloons(1000)
    gs.ship.name = "ship name"

    base_setup()

def dump_islands():
    print("Islands:")
    for isl in gs.map.places:
        print(f"{isl.island.name} - {isl.island.summary()}")

def custom_island():
    g=islands.Generator(1,1)
    isl = g.generate_island(0,islands.ISLAND_CIV_CITY, islands.ISLAND_CLASS_FOREST)
    print(f"Generated '{isl.name}'")
    return isl

def dump_trade_stuff_for_island(isl):
    print(isl.summary())
    gs.output("Available items to buy")
    for avail in isl.port.trader.on_hand:
        gs.output(
            f"[{avail.type.code}] {avail.type.name} - {avail.quantity} {avail.type.units} - {avail.price_per}D ea.")

    gs.output("Want to buy")
    for wtb in isl.port.trader.want:
        gs.output(f"[{wtb.type.code}] {wtb.type.name} {wtb.quantity} {wtb.type.units} - {wtb.price_per}D ea.")

    return isl



# always needed
initial_setup()

#show_status(RunType.RUN, [])

#dump_islands()
i = custom_island()
dump_trade_stuff_for_island(i)
i.port.trader.update()
dump_trade_stuff_for_island(i)
i.port.trader.update()
dump_trade_stuff_for_island(i)