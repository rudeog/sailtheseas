# this is for doing manual tests
import base64
import pickle

import const
from player import Player
from quest import QuestGenerator
from ship import Ship
from status_cmds import show_status
from state import gs
from setup import base_setup
from command import RunType
import islands
import map
import random
import wind


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

def describe_island(i):
    gs.output(gs.map.places[i].island.describe())

def custom_island():
    g=islands.Generator(1,1)
    isl = g.generate_island(0,const.ISLAND_CIV_CITY, const.ISLAND_CLASS_FOREST)
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
'''
i = custom_island()
dump_trade_stuff_for_island(i)
i.port.trader.update()
dump_trade_stuff_for_island(i)
i.port.trader.update()
dump_trade_stuff_for_island(i)
'''

gs.map = map.Map(30, 30, gs.seed)
# describe_island(38)
#
# qg = QuestGenerator(4444)
# q = qg.generate(gs.map,1,2)
# print(q)
# q = qg.generate(gs.map,2,2)
# print(q)
# q = qg.generate(gs.map,3,2)
# print(q)

w = wind.Wind()
print(w)
w.init_random()
print(w)
w.init_random()
print(w)
w.init_random()
print(w)
w.init_random()
print(w)

print("changing...")
dist = {}
for c in range(0,40):
    w.change_random()
    s = f"{w}"
    print(s)

# if s in dist:
#     dist[s] = dist[s]+1
# else:
#     dist[s]=1
#
# print(dist)