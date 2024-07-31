
import const
import stock
from names import PlaceGenerator, NameGenerator
from place_descriptions import DescGen, IslandModel
from util import choices_ex
from port import Port

civ_descriptions_conv = ["is an uninhabited island", "has a tribal society", "has an outpost", "has a small town",
                         "has a big city"]



# generate actual islands in populated locations of the map
class Generator:
    def __init__(self, num_islands, name_seed, map_rng):
        """
        Create an island generator
        :param num_islands: Only used to determine distribution
        :param name_seed:
        """
        # figure our spread of island civilizations
        # 20 % uninhabited
        # 15 % tribal
        # 10 % outpost
        # 40 % town
        # 15 % city
        self.map_rng = map_rng
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
        self.desc_gen = DescGen(name_seed, self.ng, self.pg)

    def _gen_type(self):

        # shouldnt happen, but if we have filled all our distributions the rest are uninhabited
        if sum(self.civ_distribution) >= self.num_islands:
            return const.ISLAND_CIV_UNINHABITED

        while True:
            t = self.map_rng.randint(0, 4)
            if self.civ_distribution[t] < self.desired_distribution[t]:
                self.civ_distribution[t] += 1
                return t

    def generate_island(self, idx, civ_type=-1, pc=None, sc=None):
        '''
        Generate an island optionally specifying civ level and/or primary/secondary classes
        :param idx:
        :param civ_type:
        :param pc:
        :param sc:
        :return:
        '''
        if civ_type == -1:
            civ_type = self._gen_type()
        else:
            self.civ_distribution[civ_type] += 1
        if pc is None:
            pc, sc = self._assign_classes(civ_type)
        elif sc is None:
            sc = const.ISLAND_CLASS_NONE

        island = Island(idx, civ_type, self.ng, self.pg, pc, sc, self.map_rng)
        model = IslandModel(island)
        island.description = self.desc_gen.generate(model)
        return island

    def _assign_classes(self, civ_type):

        primary_class = const.ISLAND_CLASS_NONE
        secondary_class = const.ISLAND_CLASS_NONE

        if civ_type == const.ISLAND_CIV_OUTPOST:
            primary_class = choices_ex(self.map_rng,
                                       [const.ISLAND_CLASS_TROPICAL, const.ISLAND_CLASS_FARMING, const.ISLAND_CLASS_AGRI,
                                        const.ISLAND_CLASS_FOREST],
                                       [1, 2, 1, 1])
            secondary_class = choices_ex(self.map_rng, [const.ISLAND_CLASS_NONE, const.ISLAND_CLASS_TROPICAL, const.ISLAND_CLASS_FARMING,
                                                        const.ISLAND_CLASS_AGRI, const.ISLAND_CLASS_FOREST],
                                         [3, 2, 1, 1, 1], [primary_class])
        elif civ_type == const.ISLAND_CIV_TOWN:
            primary_class = choices_ex(self.map_rng,
                                       [const.ISLAND_CLASS_TROPICAL, const.ISLAND_CLASS_FARMING, const.ISLAND_CLASS_AGRI,
                                        const.ISLAND_CLASS_FOREST, const.ISLAND_CLASS_MINING, const.ISLAND_CLASS_MFG],
                                       [1, 1, 1, 1, 3, 3])
            secondary_class = choices_ex(self.map_rng,
                                         [const.ISLAND_CLASS_NONE, const.ISLAND_CLASS_TROPICAL, const.ISLAND_CLASS_FARMING,
                                          const.ISLAND_CLASS_AGRI,
                                          const.ISLAND_CLASS_FOREST, const.ISLAND_CLASS_MINING, const.ISLAND_CLASS_MFG],
                                         [2, 2, 2, 2, 2, 1, 1], [primary_class])
        elif civ_type == const.ISLAND_CIV_CITY:
            primary_class = choices_ex(self.map_rng,
                                       [const.ISLAND_CLASS_MINING, const.ISLAND_CLASS_MFG, const.ISLAND_CLASS_COMMERCE],
                                       [1, 1, 3])
            if primary_class != const.ISLAND_CLASS_COMMERCE:
                # city will always have at least one commerce class
                secondary_class = const.ISLAND_CLASS_COMMERCE
            else:
                secondary_class = choices_ex(self.map_rng,
                                             [const.ISLAND_CLASS_AGRI, const.ISLAND_CLASS_FOREST, const.ISLAND_CLASS_MINING,
                                              const.ISLAND_CLASS_MFG],
                                             [2, 2, 1, 1], [primary_class])

        return primary_class, secondary_class


class Island:
    def __init__(self, index, civ_type, ng: NameGenerator, pg: PlaceGenerator, pc, sc, map_rng):

        # determine class based on civ type, and randomness
        # uninhabited islands and tribal obviously have no activity.
        # outposts and towns will get at least 1 and maybe 2 classes
        # city will always get 2
        # also determine whether the main ethnicity will be western or exotic.
        # this determines the ruler's ethnicity and possibly island name and port name and other personages
        self.primary_class = pc
        self.secondary_class = sc
        self.explored = 0  # percentage explored
        self.visit_count = 0  # number of arrivals at island
        self.quest_item = None
        self.quest_clue = None

        # after generating the map, we come back in and add fixed encounters here.
        # these will always be encountered when exploring this island
        self.encounters = None

        place_ethnicity = "e"  # default to exotic
        ruler_ethnicity = "e"
        port_name_ethnicity = "e"

        if civ_type == const.ISLAND_CIV_OUTPOST:
            ruler_ethnicity = choices_ex(map_rng, ["e", "w"], [1, 1])
            place_ethnicity = choices_ex(map_rng, ['e', 'w'], [1, 1])
        elif civ_type == const.ISLAND_CIV_TOWN:
            ruler_ethnicity = choices_ex(map_rng, ["e", "w"], [1, 1])
            place_ethnicity = choices_ex(map_rng, ['e', 'w'], [1, 1])
            port_name_ethnicity = "w"
        elif civ_type == const.ISLAND_CIV_CITY:
            ruler_ethnicity = "w"
            place_ethnicity = "w"
            port_name_ethnicity = "w"

        self.name = pg.name(place_ethnicity)
        self.description = ""
        if civ_type != const.ISLAND_CIV_UNINHABITED:
            self.ruler = ng.name("m", ruler_ethnicity)
        else:
            self.ruler = None

        # index into our main map
        self.island_index = index

        self.civ_type = civ_type

        # anything except uninhabited and tribal get a port
        if civ_type >= const.ISLAND_CIV_OUTPOST:
            self.port = Port(civ_type, self.primary_class, self.secondary_class, ng, pg, port_name_ethnicity, map_rng)
        else:
            self.port = None

    def available_stock(self):
        """
        :return: a dict keyed by stock idx with the value being a description
            # uninhabited - water
            # tribal - adds food
            # outpost - adds grog
            # town - adds ship materials, ordnance
            # city - medicine
        """
        ret = {const.STOCK_WATER_IDX: f"Refill {stock.stock_name[const.STOCK_WATER_IDX]} from natural springs on the island"}
        if self.civ_type >= const.ISLAND_CIV_TRIBAL:
            ret[const.STOCK_FOOD_IDX] = f"Restock {stock.stock_name[const.STOCK_FOOD_IDX]} by buying from one of the local tribes"
        if self.civ_type >= const.ISLAND_CIV_OUTPOST:
            ret[const.STOCK_GROG_IDX] = f"Restock {stock.stock_name[const.STOCK_GROG_IDX]} from the locals residents"
            ret[const.STOCK_FOOD_IDX] = f"Restock {stock.stock_name[const.STOCK_FOOD_IDX]} from the local residents"
            ret[const.STOCK_WATER_IDX] = f"Refill {stock.stock_name[const.STOCK_WATER_IDX]} from one of the wells"
        if self.civ_type >= const.ISLAND_CIV_TOWN:
            ret[const.STOCK_GROG_IDX] = f"Restock {stock.stock_name[const.STOCK_GROG_IDX]} from the port"
            ret[const.STOCK_FOOD_IDX] = f"Restock {stock.stock_name[const.STOCK_FOOD_IDX]} from the port"
            ret[const.STOCK_WATER_IDX] = f"Refill {stock.stock_name[const.STOCK_WATER_IDX]} at the port"
            ret[const.STOCK_MATERIALS_IDX] = f"Resupply {stock.stock_name[const.STOCK_MATERIALS_IDX]} at the port"
            ret[const.STOCK_ORDNANCE_IDX] = f"Resupply {stock.stock_name[const.STOCK_ORDNANCE_IDX]} at the port"
        if self.civ_type >= const.ISLAND_CIV_CITY:
            ret[const.STOCK_MEDICINE_IDX] = f"Restock {stock.stock_name[const.STOCK_MEDICINE_IDX]} at the port"
        return ret

    def summary(self):
        """
        Summary of island type and classes
        :return:
        """
        r = const.civ_descriptions[self.civ_type]
        if self.primary_class > const.ISLAND_CLASS_NONE:
            if self.secondary_class:
                r += f" - {const.class_descriptions[self.primary_class]}/{const.class_descriptions[self.secondary_class]}"
            else:
                r += f" - {const.class_descriptions[self.primary_class]}"
        return r

    def describe(self):
        descript = f"The island of {self.name} {civ_descriptions_conv[self.civ_type]} "
        if self.ruler:
            descript += f"which is ruled by {self.ruler}."
        else:
            descript += f"and has no ruler."

        if self.primary_class > const.ISLAND_CLASS_NONE:
            if self.secondary_class:
                descript += f" It engages primarily in {const.class_descriptions[self.primary_class].lower()} and to a lesser " + \
                            f"degree in {const.class_descriptions[self.secondary_class].lower()}."
            else:
                descript += f" It engages in {const.class_descriptions[self.primary_class]}."

        if self.port:
            descript += f" It has a port called {self.port.name} which is run by {self.port.port_master}."

        descript += " " + self.description

        if self.visit_count:
            if self.visit_count > 1:
                visit_desc = f"You and your crew have visited {self.visit_count} times"
            else:
                visit_desc = "This is your first visit"

            if self.explored:
                explore_desc = f"You have explored {self.explored}% of the island."
            else:
                explore_desc = "You have not explored this island."

            descript += f" {visit_desc}. {explore_desc}"

        else:
            descript += f" You have not visited this island."
        return descript
