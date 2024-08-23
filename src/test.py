# this is for doing manual tests
import base64
import pickle

import const
from player import Player
from quest import QuestGenerator, QuestItem, Quest
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
    isl = g.generate_island(0, None, const.ISLAND_CIV_CITY, const.ISLAND_CLASS_FOREST)
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

gs.map = map.Map(30, 30, gs.seed, None)
# describe_island(38)
#

def get_loc(i):
    l=gs.map.get_place_by_index(i)
    return f"{l.location[0]}/{l.location[1]}"

def dump_q(q:Quest):
    print(f"Quest: {q.description}")
    print(f"  Target: {q.target.name} at {get_loc(q.target.place_index)}")
    for art in q.artifacts:
        print(f"  Artifact: {art.name} at {get_loc(art.place_index)}")
    for cl in q.clues:
        print(f"  Clue at {get_loc(cl.place_index)}: {cl.name}")
        art=cl.clue_target
        print(f"    points to {art.name} at {get_loc(art.place_index)}")
qg = QuestGenerator(4444)
#q1 = qg.generate(gs.map,1,2)
#print(q1)
#q2 = qg.generate(gs.map,2,2)
#print(q2)
q3 = qg.generate(gs.map,3,2)
print(q3)

#print(q3.describe())
q3.target.found=True
q3.clues[0].found=True
q3.clues[1].found=True
q3.artifacts[0].found=True
q3.artifacts[1].found=True
q3.artifacts[2].found=True
q3.clues[4].found=True
q3.clues[6].found=True
print("msg: " + q3.check_completed(q3.target.place_index))
print(q3.describe())

#dump_q(q1)
#dump_q(q2)
#dump_q(q3)