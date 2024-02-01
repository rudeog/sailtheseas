import random
from names import PlaceGenerator, NameGenerator
import cargo
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

# island will be from uninhabited up to advanced.
# this integer also determines production levels
ISLAND_CIV_UNINHABITED = 0
ISLAND_CIV_TRIBAL = 1  # natives
ISLAND_CIV_OUTPOST = 2  # some western civilization, has port with basic trading
ISLAND_CIV_TOWN = 3  # has a port with basics, as well as some repair services
ISLAND_CIV_CITY = 4  # has port all the latest amenities, upgrades etc

civ_descriptions = ["Uninhabited", "Tribal", "Outpost", "Small Town", "Big City"]
civ_descriptions_conv = ["an uninhabited island", "has a tribal society", "has an outpost", "has a small town", "has a big city"]

# what each one produces
# gold is going to be special and should be produced in very small qty
production_table = { ISLAND_CLASS_NONE: [],
                     ISLAND_CLASS_TROPICAL: [cargo.CARGO_FOOD, cargo.CARGO_RUM],
                     ISLAND_CLASS_FARMING: [cargo.CARGO_LIVESTOCK],
                     ISLAND_CLASS_AGRI: [cargo.CARGO_GRAIN],
                     ISLAND_CLASS_FOREST: [cargo.CARGO_LUMBER],
                     ISLAND_CLASS_MINING: [cargo.CARGO_IRON, cargo.CARGO_GOLD],
                     ISLAND_CLASS_MFG: [cargo.CARGO_MFG],
                     ISLAND_CLASS_COMMERCE: []
                     }
# what each one consumes
# earlier in list means higher consumption
consumption_table = { ISLAND_CLASS_NONE: [],
                      ISLAND_CLASS_TROPICAL: [cargo.CARGO_MFG, cargo.CARGO_GRAIN, cargo.CARGO_IRON, cargo.CARGO_LIVESTOCK],
                      ISLAND_CLASS_FARMING: [cargo.CARGO_GRAIN, cargo.CARGO_MFG, cargo.CARGO_RUM, cargo.CARGO_LUMBER],
                      ISLAND_CLASS_AGRI: [cargo.CARGO_MFG, cargo.CARGO_IRON,cargo.CARGO_LUMBER, cargo.CARGO_RUM, cargo.CARGO_LIVESTOCK],
                      ISLAND_CLASS_FOREST: [cargo.CARGO_FOOD, cargo.CARGO_MFG, cargo.CARGO_LIVESTOCK, cargo.CARGO_GRAIN, cargo.CARGO_IRON],
                      ISLAND_CLASS_MINING: [cargo.CARGO_LUMBER, cargo.CARGO_FOOD, cargo.CARGO_RUM, cargo.CARGO_MFG],
                      ISLAND_CLASS_MFG: [cargo.CARGO_IRON, cargo.CARGO_LUMBER, cargo.CARGO_LIVESTOCK ],
                      ISLAND_CLASS_COMMERCE: [cargo.CARGO_FOOD, cargo.CARGO_RUM],
                    }

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

        # determine class based on civ type, and randomness
        # uninhabited islands and tribal obviously have no activity.
        # outposts and towns will get at least 1 and maybe 2 classes
        # city will always get 2
        # also determine whether the main ethnicity will be western or exotic.
        # this determines the ruler's ethnicity and possibly island name and port name and other personages

        place_ethnicity = "e"  # default to exotic
        ruler_ethnicity = "e"
        port_name_ethnicity = "e"
        if civ_type == ISLAND_CIV_UNINHABITED:
            # no production
            self.primary_class = ISLAND_CLASS_NONE
            self.secondary_class = ISLAND_CLASS_NONE
        elif civ_type == ISLAND_CIV_TRIBAL:
            # no production
            self.primary_class = ISLAND_CLASS_NONE
            self.secondary_class = ISLAND_CLASS_NONE
        if civ_type == ISLAND_CIV_OUTPOST:
            self.primary_class = choices_ex(
                [ISLAND_CLASS_TROPICAL, ISLAND_CLASS_FARMING, ISLAND_CLASS_AGRI, ISLAND_CLASS_FOREST],
                [1,2,1,1])
            self.secondary_class = choices_ex([ISLAND_CLASS_NONE, ISLAND_CLASS_TROPICAL, ISLAND_CLASS_FARMING,
                                               ISLAND_CLASS_AGRI, ISLAND_CLASS_FOREST],
                                              [3, 2, 1, 1, 1], [self.primary_class])
            ruler_ethnicity = choices_ex(["e","w"],[1,1])
            place_ethnicity = choices_ex(['e','w'],[1,1])
        elif civ_type == ISLAND_CIV_TOWN:
            self.primary_class = choices_ex(
                [ISLAND_CLASS_TROPICAL, ISLAND_CLASS_FARMING, ISLAND_CLASS_AGRI,
                 ISLAND_CLASS_FOREST, ISLAND_CLASS_MINING, ISLAND_CLASS_MFG],
                [1, 1, 1, 1, 3, 3])
            self.secondary_class = choices_ex(
                [ISLAND_CLASS_NONE, ISLAND_CLASS_TROPICAL, ISLAND_CLASS_FARMING, ISLAND_CLASS_AGRI,
                 ISLAND_CLASS_FOREST, ISLAND_CLASS_MINING, ISLAND_CLASS_MFG],
                [2, 2, 2, 2, 2, 1, 1], [self.primary_class])
            ruler_ethnicity = choices_ex(["e","w"],[1,1])
            place_ethnicity = choices_ex(['e','w'],[1,1])
            port_name_ethnicity = "w"

        elif civ_type == ISLAND_CIV_CITY:
            self.primary_class = choices_ex(
                [ISLAND_CLASS_MINING, ISLAND_CLASS_MFG, ISLAND_CLASS_COMMERCE],
                [1, 1, 3])
            if self.primary_class != ISLAND_CLASS_COMMERCE:
                # city will always have at least one commerce class
                self.secondary_class = ISLAND_CLASS_COMMERCE
            else:
                self.secondary_class = choices_ex(
                    [ISLAND_CLASS_AGRI, ISLAND_CLASS_FOREST, ISLAND_CLASS_MINING, ISLAND_CLASS_MFG],
                    [2, 2, 1, 1], [self.primary_class])
            ruler_ethnicity = "w"
            place_ethnicity = "w"
            port_name_ethnicity = "w"

        self.name = pg.name(place_ethnicity)
        if civ_type != ISLAND_CIV_UNINHABITED:
            self.ruler = ng.name("m", ruler_ethnicity)

        # index into our main map
        self.island_index = index

        self.civ_type = civ_type

        # anything except uninhabited and tribal get a port
        if civ_type >= ISLAND_CIV_OUTPOST:
            self.port = Port(civ_type, self.primary_class, self.secondary_class, ng, pg, port_name_ethnicity)
        else:
            self.port = None

    def summary(self):
        """
        Summary of island type and classes
        :return:
        """
        r = civ_descriptions[self.civ_type]
        if self.primary_class > ISLAND_CLASS_NONE:
            if self.secondary_class:
                r += f" - {class_descriptions[self.primary_class]}/{class_descriptions[self.secondary_class]}"
            else:
                r += f" - {class_descriptions[self.primary_class]}"
        return r

    def describe(self):
        descript = f"The island of {self.name} {civ_descriptions_conv[self.civ_type]} "
        if self.ruler:
            descript += f"which is ruled by {self.ruler}. "
        else:
            descript += f"and has no ruler. "

        if self.primary_class > ISLAND_CLASS_NONE:
            if self.secondary_class:
                descript += f"It engages primarily in {class_descriptions[self.primary_class].lower()} and to a lesser " + \
                    f"degree in {class_descriptions[self.secondary_class].lower()}. "
            else:
                descript += f"It engages in {class_descriptions[self.primary_class]}. "

        if self.port:
            descript += f"It has a port called {self.port.name} which is run by {self.port.port_master}."

        return descript


# handles the business of generating a trading port and updating
# price market values. why separate from port? we may have trading between ships, etc.
# commerce class will make bought items available for sale, therefore prices are affected
# other classes will "consume" bought items and produce based on class
class TradingPost:
    def __init__(self, island_civ, primary_class, secondary_class):

        self.secondary_class = secondary_class
        self.primary_class = primary_class
        self.island_civ = island_civ
        # selling
        self.on_hand: cargo.CargoCollection = cargo.CargoCollection()
        # buying - qty represents amount willing to buy
        self.want: cargo.CargoCollection = cargo.CargoCollection()

        self.update()



    def update(self):
        '''
        this will do an initial update as well as ongoing updates to prices and quantities. These should be
        updated daily eventually, but
        initially will probably update when the ship has arrived at another island after leaving this one
        Price will be based on supply/demand
        Qty produced will be based on island civ and other factors
        :return:
        '''

        # primary = 3x production, secondary = 2x production
        # we will add more factors here later

        pt = production_table[self.primary_class]
        for pi in pt:
            ct = cargo.cargo_types[pi]
            qty = ct.prod_coefficient * 3

            self.on_hand.add_remove(pi,qty)

        pt = production_table[self.secondary_class]
        for pi in pt:
            ct = cargo.cargo_types[pi]
            qty = ct.prod_coefficient * 2

            self.on_hand.add_remove(pi,qty)

        # set prices

        pt = production_table[self.primary_class]
        for pi in pt:
            ct = cargo.cargo_types[pi]
            price = ct.price_coefficient * 1
            self.on_hand.set_price(pi,price)

        pt = production_table[self.secondary_class]
        for pi in pt:
            ct = cargo.cargo_types[pi]
            price = ct.price_coefficient * 1

            self.on_hand.set_price(pi,price)



class Port:
    def __init__(self, civ_type, primary_class, secondary_class, ng: NameGenerator, pg: PlaceGenerator, ethnicity):

        if random.random() < .4:
            # use a name rather than a place
            port_name = "Port " + ng.name("",ethnicity).last
        else:
            port_name = str(pg.name(ethnicity)) + " Harbor"
        self.port_master = ng.name("m") # might be ethnic
        self.name = port_name
        self.civ_type = civ_type
        self.primary_class = primary_class
        self.secondary_class = secondary_class
        self.trader: TradingPost = TradingPost(civ_type, primary_class, secondary_class)


