import random

import util
from state import gs
from map import Map
from util import ListSelector
from command import RunType

location_adj = ["Mysterious", "Ancient", "Eldritch", "Mystical", "Voodoo", "Holy", "Unholy", "Forgotten"]
location_name = ["Temple", "Ruins", "Altar", "Grotto", "Cavern", "Tombs", "Catacombs"]
quest_short = ["Find {arts} and bring them to {loc}",
               "Bring {arts} to their resting place at {loc}",
               "Locate {arts} and take them to {loc}",
               "Return {arts} to {loc} where they belong",
               "Restore {arts} to {loc}",
               ]
complete_short = [
    "You have found {arts} and courageously taken them to {loc}",
    "You have brought {arts} and laid them in their resting place at {loc}",
    "You have managed to locate {arts} and have taken them to {loc}",
    "You have returned {arts} to {loc} where they belong",
    "You have found {arts} and restored them to {loc}",
]

clue_short = ["I've heard that {artname} lies on an island somewhere {dirto} of here.",
              "It is said that on an island {dirto} of here, {artname} can be found.",
              "I heard from my brothers wifes uncle that {artname} is on an island to the {dirto}.",
              "It is well known in our village that {artname} is on an island {dirto} of here.",
              "When I was collecting water the other day, I overheard that {artname} can be found on an island to the {dirto}.",
              "Before my father died, he revealed to me that on an island to the {dirto} lies {artname}.",
              ]
art_adj = ["Crystal", "Golden", "Cursed", "Blessed", "Dark", "Arcane", "Ghostly", "Jeweled", "Sacrificial"]
art_name = ["Shard", "Sword", "Scroll", "Statuette", "Effigy", "Shrunken Head", "Shield", "Undergarment"]
art_desc = ["a remarkable", "a worn out", "a strange", "an ill-kept", "an unusual", "a common"]

_QT_TARGET = 1
_QT_ARTIFACT = 2
_QT_CLUE = 3


# quest items and quests are serialized?

# a quest item is either the target location, one of the artifacts, or a clue pointing to location or artifact
class QuestItem:
    def __init__(self, name, item_type, parent):
        # associated quest
        self.quest = parent
        # this will be the descriptive name
        self.name = name
        # this will indicate the type (one of the above constants)
        self.type = item_type
        # this will be the index of the map place where it exists
        # (each map location can't have more than one quest item)
        self.place_index = -1
        # will be set true when found
        self.found = False
        # if this is a clue, this will point to the underlying thing its a clue to
        self.clue_target = None
        # will be set to true when found
        self.found = False

    def is_clue(self):
        return self.type == _QT_CLUE

    def is_target(self):
        return self.type == _QT_TARGET

    def is_artifact(self):
        return self.type == _QT_ARTIFACT

    def get(self):
        return self.found

    def set(self, v):
        self.found = v


def _get_at(pi):
    w = gs.map.get_place_by_index(pi)
    c = util.coord_as_str(w.location)
    return f"{w.island.name} ({c})"


adj_items = ['located', 'found', 'discovered']


class Quest:
    def __init__(self):
        # set to true when completed
        self.completed = False
        self.completion_text = ""
        # full description of the quest
        self.description = None
        # these are clues
        self.clues: [QuestItem] = []
        # these are the artifacts
        self.artifacts: [QuestItem] = []
        # this will be the place to bring them
        self.target = None
        self.adj = 0

    def get(self):
        # we only need to keep track of whether found or completed
        cs = [c.get() for c in self.clues]
        a = [ai.get() for ai in self.artifacts]
        return {"com": self.completed, "tgt": self.target.get(), "clu": cs, "art": a}

    def set(self, d: dict):
        self.completed = d["com"]
        for i, v in enumerate(d["clu"]):
            self.clues[i].set(v)
        for i, v in enumerate(d["art"]):
            self.artifacts[i].set(v)

    def _adj(self):
        self.adj += 1
        return adj_items[self.adj % len(adj_items)]

    # this will return non empty string if this action caused the quest to complete.
    # place index is where its being checked from (where the player is)
    # in order to complete a quest, all items need to be found and the player needs to be at the target
    # returns a glorious message of completion if it caused a completion
    def check_completed(self, place_index):
        if self.completed:
            return ""  # already completed
        if place_index != self.target.place_index:
            return ""  # not at right location
        if not self.target.found:
            return ""  # havent found target (shouldnt happen here because we will have found it at this location)
        for a in self.artifacts:
            if not a.found:
                return ""
        # all items are found we are done!
        self.completed = True
        return self.completion_text

    def describe(self):
        fl = []
        r = self.description + "\n"
        if self.completed:
            r += f"{self.completion_text}\n"
            return r

        if self.target.found:
            r += f"You {self._adj()} {self.target.name} at {_get_at(self.target.place_index)}\n"
            fl.append(self.target)

        for cl in self.clues:
            tgt = cl.clue_target
            if tgt.found:
                if tgt not in fl:
                    r += f"You {self._adj()} {tgt.name} at {_get_at(tgt.place_index)}\n"
                    fl.append(tgt)
            else:
                if cl.found:
                    r += f"Clue found at {_get_at(cl.place_index)}: \"{cl.name}\"\n"
        return r


class QuestGenerator:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.ls_loc_adj = ListSelector(self.rng, location_adj)
        self.ls_loc_name = ListSelector(self.rng, location_name)
        self.ls_quest = ListSelector(self.rng, quest_short, complete_short)
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
            art = QuestItem(f"{idesc} {iadj} {iname}", _QT_ARTIFACT, quest)
            quest.artifacts.append(art)
            for j in range(clues_per_art):
                cl = QuestItem("", _QT_CLUE, quest)
                cl.clue_target = art
                quest.clues.append(cl)
        if num_arts > 1:
            art_group = f"the {num_to_text(num_arts)} {iadj} {iname}s"
        else:
            art_group = f"the {iadj} {iname}"

        qadj = self.ls_loc_adj.select()
        qname = self.ls_loc_name.select()
        qfinal = f"the {qadj} {qname}"
        d, t = self.ls_quest.select_with_partner()
        quest.description = d.format(arts=art_group, loc=qfinal)
        quest.completion_text = t.format(arts=art_group, loc=qfinal)

        quest.target = QuestItem(qfinal, _QT_TARGET, quest)
        for j in range(clues_per_art):
            cl = QuestItem("", _QT_CLUE, quest)
            cl.clue_target = quest.target
            quest.clues.append(cl)

        # we have the articles and their target location, and for each of these, we have
        # a number of clues
        total_items = (num_arts + 1) * (clues_per_art + 1)

        # build a list of random locations that have no clues, places or artifacts
        locations = []
        for p in map.places:
            if not p.island.quest_item:
                locations.append(p.index)

        if len(locations) < total_items:
            raise ValueError("insufficient remaining locations for quest items")
        self.rng.shuffle(locations)

        # place target
        quest.target.place_index = locations[0]
        map.get_place_by_index(locations[0]).island.quest_item = quest.target

        locations = locations[1:]
        # place artifacts
        for i in range(0, num_arts):
            quest.artifacts[i].place_index = locations[i]
            map.get_place_by_index(locations[i]).island.quest_item = quest.artifacts[i]
        locations = locations[num_arts:]
        #place clues
        for i in range(len(quest.clues)):
            quest.clues[i].place_index = locations[i]
            map.get_place_by_index(locations[i]).island.quest_item = quest.clues[i]

        # calculate clue descriptions
        clue_idx = 0
        for cl in quest.clues:
            clue_loc = map.get_place_by_index(cl.place_index)
            target = map.get_place_by_index(cl.clue_target.place_index)
            dir_to = util.direction_from_two_coords(clue_loc.location, target.location)
            if dir_to is None:  # same location (unlikely)
                clue = f"The {cl.clue_target.name} is on this very island!"
            else:
                clue = self.ls_clue.select().format(artname=cl.clue_target.name, dirto=dir_to)
            cl.name = clue

        return quest


def num_to_text(n):
    if 0 < n < 11:
        return ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'][n - 1]
    return f"{n}"


# todo move this elsewhere?
def cmd_quests(run_type, toks):
    if run_type is RunType.CHECK_AVAILABLE:
        return True
    if run_type is RunType.HELP:
        gs.output("This command shows the quests you must complete, and your progress toward each one. As you "
                  "explore, you will find things and clues that help you complete your quests. They are listed here.")

        return
    c = 1
    for q in gs.quests:
        gs.output(f"Quest {c}: {q.describe()}")
        c += 1
