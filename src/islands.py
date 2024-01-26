import random
from names import PlaceGenerator, NameGenerator
from cargo import CargoCollection
from util import choices_ex

# each island has a class of activities they do. They may have more than one
# does not participate in any activities
ISLAND_CLASS_NONE = 0
# suitable for growing fruit, etc. rum production
ISLAND_CLASS_TROPICAL = 1
# animal farming
ISLAND_CLASS_FARMING = 2
# crop farming
ISLAND_CLASS_AGRI = 3
# forestry
ISLAND_CLASS_FOREST = 4
# mining (gold, iron)
ISLAND_CLASS_MINING = 5
# manufacturing
ISLAND_CLASS_MFG = 6
# just trading etc. (loans?)
ISLAND_CLASS_COMMERCE = 7

class_descriptions = ["None", "Tropical Fruit", "Meat and Dairy", "Agriculture", "Forestry", "Mining", "Manufacturing",
                      "Commerce"]

# island will be from uninhabited up to advanced
ISLAND_CIV_UNINHABITED = 0
ISLAND_CIV_TRIBAL = 1  # natives
ISLAND_CIV_OUTPOST = 2  # some western civilization, has port with basic trading
ISLAND_CIV_TOWN = 3  # has a port with basics, as well as some repair services
ISLAND_CIV_CITY = 4  # has port all the latest amenities, upgrades etc

civ_descriptions = ["Uninhabited", "Tribal", "Outpost", "Small Town", "Big City"]


# generate actual islands in populated locations of the map
class Generator:
    def __init__(self, num_islands, name_seed):
        # figure our spread of island civilizations
        # 20 % uninhabited
        # 15 % tribal
        # 10 % outpost
        # 40 % town
        # 15 % city
        self.civ_distribution = [0] * 5
        self.num_islands = num_islands
        self.desired_distribution = [int(.20 * float(num_islands)), int(.15 * float(num_islands)),
                                     int(.10 * float(num_islands)), int(.40 * float(num_islands)),
                                     int(.15 * float(num_islands))]
        rem = num_islands - sum(self.desired_distribution)
        i = 0
        # distribute remaining ones round robin (due to rounding down above)
        while rem:
            self.desired_distribution[i] += 1
            rem -= 1
            i += 1
            if i > 4:
                i = 0

        self.pg = PlaceGenerator(name_seed)
        self.ng = NameGenerator(name_seed)

    def _gen_type(self):

        # shouldnt happen, but if we have filled all our distributions the rest are uninhabited
        if sum(self.civ_distribution) >= self.num_islands:
            return ISLAND_CIV_UNINHABITED

        while True:
            t = random.randint(0, 4)
            if self.civ_distribution[t] < self.desired_distribution[t]:
                self.civ_distribution[t] += 1
                return t

    def generate_island(self, idx, civ_type=-1):
        if civ_type == -1:
            civ_type = self._gen_type()
        else:
            self.civ_distribution[civ_type] += 1

        island = Island(idx, civ_type, self.ng, self.pg)
        return island


class Island:
    def __init__(self, index, civ_type, ng: NameGenerator, pg: PlaceGenerator):
        self.name = pg.name()
        self.primary_class = ISLAND_CLASS_NONE
        self.secondary_class = ISLAND_CLASS_NONE
        # determine class based on civ type, and randomness
        # uninhabited islands and tribal obviously have no activity


        if civ_type == ISLAND_CIV_OUTPOST:
            self.primary_class = choices_ex(
                [ISLAND_CLASS_TROPICAL, ISLAND_CLASS_FARMING, ISLAND_CLASS_AGRI, ISLAND_CLASS_FOREST],
                [1,2,1,1])
            self.secondary_class = choices_ex([ISLAND_CLASS_NONE, ISLAND_CLASS_TROPICAL, ISLAND_CLASS_FARMING,
                                               ISLAND_CLASS_AGRI, ISLAND_CLASS_FOREST],
                                              [3, 2, 1, 1, 1], [self.primary_class])
        elif civ_type == ISLAND_CIV_TOWN:
            self.primary_class = choices_ex(
                [ISLAND_CLASS_TROPICAL, ISLAND_CLASS_FARMING, ISLAND_CLASS_AGRI,
                 ISLAND_CLASS_FOREST, ISLAND_CLASS_MINING, ISLAND_CLASS_MFG],
                [1, 1, 1, 1, 3, 3])
            self.secondary_class = choices_ex(
                [ISLAND_CLASS_NONE, ISLAND_CLASS_TROPICAL, ISLAND_CLASS_FARMING, ISLAND_CLASS_AGRI,
                 ISLAND_CLASS_FOREST, ISLAND_CLASS_MINING, ISLAND_CLASS_MFG],
                [2, 2, 2, 2, 2, 1, 1], [self.primary_class])
        elif civ_type == ISLAND_CIV_CITY:
            self.primary_class = choices_ex(
                [ISLAND_CLASS_MINING, ISLAND_CLASS_MFG, ISLAND_CLASS_COMMERCE],
                [1, 1, 3])
            self.secondary_class = choices_ex(
                [ISLAND_CLASS_AGRI, ISLAND_CLASS_FOREST, ISLAND_CLASS_MINING, ISLAND_CLASS_MFG, ISLAND_CLASS_COMMERCE],
                [2, 2, 1, 1, 1], [self.primary_class])

        # index into our main map
        self.island_index = index
        self.civ_type = civ_type
        if civ_type >= ISLAND_CIV_OUTPOST:  # has port
            self.port = Port(civ_type, self.primary_class, ng, pg)
        else:
            self.port = None

    def summary(self):
        r = civ_descriptions[self.civ_type]
        if self.primary_class > ISLAND_CLASS_NONE:
            if self.secondary_class:
                r += f" - {class_descriptions[self.primary_class]}/{class_descriptions[self.secondary_class]}"
            else:
                r += f" - {class_descriptions[self.primary_class]}"
        return r


class Port:
    def __init__(self, civ_type, island_class, ng: NameGenerator, pg: PlaceGenerator):
        if random.random() < .4:
            # use a name rather than a place
            port_name = "Port " + ng.name().last
        else:
            port_name = str(pg.name()) + " Harbor"

        self.name = port_name
        self.civ_type = civ_type
        self.island_class = island_class
        self.trader: TradingPost = TradingPost(civ_type, island_class)


# handles the business of generating a trading port and updating
# price market values

class TradingPost:
    def __init__(self, island_civ, island_class):
        self.on_hand: CargoCollection = CargoCollection()
        # civ should be 2 or greater to even have a port
