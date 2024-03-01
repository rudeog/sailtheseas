from util import serialize_obj, deserialize_obj
from state import gs

STOCK_FOOD_IDX = 0
STOCK_WATER_IDX = 1
STOCK_GROG_IDX = 2
STOCK_MEDICINE_IDX = 3
STOCK_MATERIALS_IDX = 4
STOCK_ORDNANCE_IDX = 5

# 5 units per day per abs = full ration
# 3 units per day is reduced ration
# 2 units per day is meager
STOCK_RATIONS_FULL = 5
STOCK_RATIONS_REDUCED = 3
STOCK_RATIONS_MEAGER = 2

# grog consumption rate
STOCK_GROG_HIGH = 2
STOCK_GROG_LOW = 1
STOCK_GROG_NONE = 0

stock_name = ['food', 'water', 'grog', 'medicine', 'ship materials', 'ordnance']


class StockItem:
    _serialized_attrs = ['idx', 'consumption_rate', 'qty', 'max_qty', 'price_coeff']

    def __init__(self, idx=None, def_cons=None, max_qty=None, price_coeff=None):
        self.idx = idx
        # normal daily consumption rate
        self.consumption_rate: int = def_cons
        # qty on hand
        self.qty: int = 0
        # max qty the ship can hold
        self.max_qty: int = max_qty
        # base cost per unit
        self.price_coeff: int = price_coeff

    def get(self):
        ret = serialize_obj(self)
        return ret

    def set(self, d: dict):
        deserialize_obj(self, d)


class Stock:

    def __init__(self):
        self.items = [
            # food is in units. each abs consumes one unit per day
            # a full complement of food should feed a full staffing of ABS for 7 days
            # 7 * 5 * 100 = 3500
            # can restock from preserved foods, grain, livestock
            StockItem(STOCK_FOOD_IDX, 5, 3500, 1),

            # water is consumed at a fixed rate of 1 unit per day per abs
            # assuming grog is not being given.
            # a full amount of water should last 4 days
            StockItem(STOCK_WATER_IDX, 1, 400, 0),

            # grog is an optional item. if given at 1 unit per day, crew is
            # kept from becoming dissatisfied. if given at 2 per day, crew
            # can gain happiness. if withheld, crew becomes dissatisfied
            # if grog is set at 0, water is consumed at 1 per day
            # can restock from rum and water
            StockItem(STOCK_GROG_IDX, 1, 700, 4),

            # medical supplies are consumed at 1 per day. after calamities, they are consumed more.
            # they may only be available at higher level islands
            StockItem(STOCK_MEDICINE_IDX, 1, 28, 100),

            # materials to fix the ship. the ship can become damaged due to storm, animals, battles.
            # it also has a natural wear and tear. 1 unit gets consumed normally per day.
            # generally available
            StockItem(STOCK_MATERIALS_IDX, 1, 20, 50),

            # cannon balls and powder. consumed during battles. each battle round consumes 1
            # unit.
            StockItem(STOCK_ORDNANCE_IDX, 0, 10, 70),
        ]

    def set(self, lst: list):
        self.items = [StockItem() for _ in range(len(lst))]
        for i, v in enumerate(lst):
            self.items[i].set(v)

    def get(self) -> list:
        ret = []
        for v in self.items:
            ret.append(v.get())
        return ret

    def describe(self):
        gs.output(f"{gs.crew.firstmate}: I've taken stock of what we have on board {gs.ship.name} and we have "
                  "the following supplies:")
        for v in self.items:
            pctage = int(100 * v.qty / v.max_qty)
            gs.output(f"  {stock_name[v.idx]} - {pctage}%")

    def consume_rations(self) -> bool:
        '''
        consume a daily amount of rations at the current rate.
        :return: False if we came up short, true otherwise
        '''
        item = self.items[STOCK_FOOD_IDX]
        to_consume = item.consumption_rate * gs.crew.seamen_count
        if item.qty < to_consume:
            item.qty = 0
            return False
        item.qty -= to_consume
        return True

    def set_rations(self, amt):
        """
        set the current rations
        :param amt: use one of STOCK_RATIONS_
        :return:
        """
        if amt > STOCK_RATIONS_FULL or amt < STOCK_RATIONS_MEAGER:
            raise ValueError
        self.items[STOCK_FOOD_IDX].consumption_rate = amt

    def get_rations(self) -> tuple[str, int]:
        """
        :return: a description of the current ration consumption and its constant
        """
        rate = self.items[STOCK_FOOD_IDX].consumption_rate
        if rate >= STOCK_RATIONS_FULL:
            return "full", STOCK_RATIONS_FULL
        if rate >= STOCK_RATIONS_REDUCED:
            return "reduced", STOCK_RATIONS_REDUCED
        return "meager", STOCK_RATIONS_MEAGER

    def consume_fluids(self) -> int:
        """
        consume a daily amount of fluids. If grog is being rationed and its in stock then it
        is consumed first at its rate. Otherwise water is consumed.
        :return: -1 - no fluid could be consumed
                 0 - water was consumed
                 1 - low level grog consumed
                 2 - high level grog was consumed
        """

        item = self.items[STOCK_GROG_IDX]
        to_consume = item.consumption_rate * gs.crew.seamen_count
        if to_consume <= item.qty:
            item.qty -= to_consume
            return item.consumption_rate
        if item.consumption_rate > STOCK_GROG_LOW:
            # see if we can consume a lower level
            to_consume = STOCK_GROG_LOW * gs.crew.seamen_count
            if to_consume <= item.qty:
                item.qty -= to_consume
                return STOCK_GROG_LOW

        # fall back to water (use any remaining grog)
        grog_remainder = item.qty
        item = self.items[STOCK_WATER_IDX]
        to_consume = item.consumption_rate * gs.crew.seamen_count
        if to_consume <= item.qty+grog_remainder:
            to_consume -= grog_remainder
            item.qty -= to_consume
            return 0

        item.qty = 0
        return -1

    def set_grog_portion(self, i: int):
        """
        Set grog to high, low, nonw
        :param i: STOCK_GROG_*
        :return:
        """
        item = self.items[STOCK_GROG_IDX]
        if i > STOCK_GROG_HIGH or i < STOCK_GROG_NONE:
            raise ValueError
        item.consumption_rate = i

    def get_grog_portion(self) -> tuple[str, int]:
        """
        :return: a description of the current grog consumption and its constant
        """
        rate = self.items[STOCK_GROG_IDX].consumption_rate
        if rate >= STOCK_GROG_HIGH:
            return "a generous portion of grog", STOCK_GROG_HIGH
        if rate >= STOCK_GROG_LOW:
            return "a normal portion of grog", STOCK_GROG_LOW
        return "water only", STOCK_GROG_NONE
