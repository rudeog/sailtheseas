import random

import util
from state import gs
from map import Map
from util import ListSelector

location_adj = ["Mysterious", "Ancient", "Eldritch", "Mystical", "Voodoo", "Holy", "Unholy", "Forgotten"]
location_name = ["Temple", "Ruins", "Altar", "Grotto", "Cavern", "Tombs", "Catacombs"]
quest_short = ["Find {arts} and bring them to {loc}",
               "Bring {arts} to their resting place at {loc}",
               "Locate {arts} and take them to {loc}",
               "Return {arts} to {loc} where they belong",
               "Restore {arts} to {loc}",
               ]

clue_short = ["I've heard that {artname} lies on an island somewhere {dirto} of here.",
              "It is said that on an island {dirto} from here, {artname} can be found.",
              "I heard from my brothers wifes uncle that {artname} is on an island to the {dirto}.",
              "It is well known in our village that {artname} is on an island {dirto} of here.",
              "When I was collecting water the other day, I overheard that {artname} can be found on an island to the {dirto}.",
              "Before my father died, he revealed to me that on an island to the {dirto} lies the {artname}.",
              ]
art_adj = ["Crystal", "Golden", "Cursed", "Blessed", "Dark", "Arcane", "Ghostly", "Jeweled", "Sacrificial"]
art_name = ["Shard", "Sword", "Scroll", "Statuette", "Effigy", "Shrunken Head", "Shield", "Undergarment"]
art_desc = ["a remarkable", "a worn out", "a strange", "an ill-kept", "an unusual", "a common"]


class QuestItem:
    def __init__(self, name, is_artifact):
        self.name = name
        # if true and its found, it stays with the player, otherwise its the target location
        self.is_artifact = is_artifact

        # this will be the x/y location on the map of where it exists
        self.location = None
        # will be set true when found
        self.found = False


class ClueItem:
    def __init__(self, clue, loc):
        self.clue = clue
        self.revealed = False
        self.location = loc


class Quest:
    def __init__(self):
        # full description of the quest
        self.description = None
        # these will be the artifacts that need finding
        self.artifacts: [QuestItem] = []
        # this will be the place to bring them
        self.target: QuestItem = None


class QuestGenerator:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.ls_loc_adj = ListSelector(self.rng, location_adj)
        self.ls_loc_name = ListSelector(self.rng, location_name)
        self.ls_quest = ListSelector(self.rng, quest_short)
        self.ls_clue = ListSelector(self.rng, clue_short)
        self.ls_art = ListSelector(self.rng, art_name)
        self.ls_art_adj = ListSelector(self.rng, art_adj)

    def generate(self, map: Map, num_arts, clues_per_art):
        '''
        Generate a quest. num_arts must be 2 or more for description goodness
        :param map:
        :param num_arts:
        :return:
        '''
        quest = Quest()

        # need a new one each time to avoid dupes
        art_desc_gen = ListSelector(self.rng, art_desc)
        iname = self.ls_art.select()
        iadj = self.ls_art_adj.select()
        for i in range(num_arts):
            idesc = art_desc_gen.select()
            quest.artifacts.append(QuestItem(f"{idesc} {iadj} {iname}", True))
        art_group = f"the {num_arts} {iadj} {iname}s"
        qadj = self.ls_loc_adj.select()
        qname = self.ls_loc_name.select()
        qfinal = f"the {qadj} {qname}"
        quest.description = self.ls_quest.select().format(arts=art_group, loc=qfinal)
        quest.target = QuestItem(qfinal, False)
        print(quest.description)
        # place items and clues on map. Each item gets 2 clues

        for i in range((num_arts + 1) * (1 + clues_per_art)):
            # 0 for the art, 1..clues_per_art for the clue
            clidx = int(i % (1 + clues_per_art))

            # 0 for the loc, 1..n for the artifact
            artidx = int(i / (1 + clues_per_art))
            trial = 0
            pl = None
            while trial < 1000:  # try to get a non-quest or clue place first
                idx = self.rng.randint(0, map.num_places-1)
                pl = map.places[idx]
                if not pl.island.quest_clue and not pl.island.quest_item:
                    break

            if clidx == 0:  # the place or artifact
                if artidx == 0:  # place target
                    quest.target.location = pl.location
                    pl.island.quest_item = quest.target
                else:
                    quest.artifacts[artidx - 1].location = pl.location
                    pl.island.quest_item = quest.artifacts[artidx - 1]
            else:  # a clue
                if artidx == 0:  # place target
                    dirto = util.direction_from_two_coords(pl.location, quest.target.location)
                    artname = quest.target.name
                else:
                    dirto = util.direction_from_two_coords(pl.location, quest.artifacts[artidx - 1].location)
                    artname = quest.artifacts[artidx - 1].name

                if dirto == None:  # same location (unlikely)
                    clue = f"The {artname} is on this very island!"
                else:
                    clue = self.ls_clue.select().format(artname=artname, dirto=dirto)
                pl.island.quest_clue = ClueItem(clue, pl.location)


        return quest
