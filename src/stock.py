from cargo import CargoItem, cargo_types
from util import serialize_obj, deserialize_obj
from state import gs
import const


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
        self.price_coeff: float = price_coeff

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
            StockItem(const.STOCK_FOOD_IDX, 5, 3500, .3),

            # water is consumed at a fixed rate of 1 unit per day per abs
            # assuming grog is not being given.
            # a full amount of water should last 4 days
            StockItem(const.STOCK_WATER_IDX, 1, 400, 0),

            # grog is an optional item. if given at 1 unit per day, crew is
            # kept from becoming dissatisfied. if given at 2 per day, crew
            # can gain happiness. if withheld, crew becomes dissatisfied
            # if grog is set at 0, water is consumed at 1 per day
            # can restock from rum and water
            StockItem(const.STOCK_GROG_IDX, 1, 700, 2),

            # medical supplies are consumed at 1 per day. after calamities, they are consumed more.
            # they may only be available at higher level islands
            StockItem(const.STOCK_MEDICINE_IDX, 1, 28, 50),

            # materials to fix the ship. the ship can become damaged due to storm, animals, battles.
            # it also has a natural wear and tear. 1 unit gets consumed normally per day.
            # generally available
            StockItem(const.STOCK_MATERIALS_IDX, 1, 20, 30),

            # cannon balls and powder. consumed during battles. each battle round consumes 1
            # unit.
            StockItem(const.STOCK_ORDNANCE_IDX, 0, 10, 70),
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

    def check_important_stock(self, nohint):
        """
        This will check to see whether any important items of stock are less than 50% and report that.
        :return: True if any important items are less than 50%
        """
        s = []
        r = False
        for v in self.items:
            if v.idx in (const.STOCK_GROG_IDX, const.STOCK_ORDNANCE_IDX):
                continue  # these are considered non-essential
            pctage = int(100 * v.qty / v.max_qty)
            if pctage <= 50:
                s.append((stock_name[v.idx], pctage))

        if len(s) == 1:
            gs.output(f"{gs.crew.firstmate}: Captain, {gs.ship.name} only has {s[0][1]}% of {s[0][0]} remaining.")
            r = True
        elif len(s):
            gs.output(f"{gs.crew.firstmate}: Captain, {gs.ship.name} is low on the following supplies:")
            for ss in s:
                gs.output(f"{ss[0]} - {ss[1]}%")
            r = True
        if r and not nohint:
            gs.hints.show("lowsupp")
        return r

    def describe(self):
        ret = ""
        for v in self.items:
            pctage = int(100 * v.qty / v.max_qty)
            ret = ret + f"{stock_name[v.idx]} - {pctage}%\n"
        return ret

    def consume_rations(self) -> bool:
        '''
        consume a daily amount of rations at the current rate.
        :return: False if we came up short, true otherwise
        '''
        item = self.items[const.STOCK_FOOD_IDX]
        to_consume = item.consumption_rate * gs.crew.seamen_count
        if item.qty < to_consume:
            item.qty = 0
            return False
        item.qty -= to_consume
        return True

    def set_rations(self, amt):
        """
        set the current rations
        :param amt: use one of const.STOCK_RATIONS_
        :return:
        """
        if amt > const.STOCK_RATIONS_FULL or amt < const.STOCK_RATIONS_MEAGER:
            raise ValueError
        self.items[const.STOCK_FOOD_IDX].consumption_rate = amt

    def get_rations(self) -> tuple[str, int]:
        """
        :return: a description of the current ration consumption and its constant
        """
        rate = self.items[const.STOCK_FOOD_IDX].consumption_rate
        if rate >= const.STOCK_RATIONS_FULL:
            return "full", const.STOCK_RATIONS_FULL
        if rate >= const.STOCK_RATIONS_REDUCED:
            return "reduced", const.STOCK_RATIONS_REDUCED
        return "meager", const.STOCK_RATIONS_MEAGER

    def consume_fluids(self) -> int:
        """
        consume a daily amount of fluids. If grog is being rationed and its in stock then it
        is consumed first at its rate. Otherwise water is consumed.
        :return: -1 - no fluid could be consumed
                 0 - water was consumed
                 1 - low level grog consumed
                 2 - high level grog was consumed
        """
        grog_offset = 0
        item = self.items[const.STOCK_GROG_IDX]
        if item.consumption_rate > const.STOCK_GROG_NONE:
            to_consume = item.consumption_rate * gs.crew.seamen_count
            if to_consume <= item.qty:
                item.qty -= to_consume
                return item.consumption_rate

            if item.consumption_rate > const.STOCK_GROG_LOW:
                # see if we can consume a lower level
                to_consume = const.STOCK_GROG_LOW * gs.crew.seamen_count
                if to_consume <= item.qty:
                    item.qty -= to_consume
                    return const.STOCK_GROG_LOW
            # consume the rest of the grog as an offset to water
            grog_offset = item.qty
            item.qty = 0

        # fall back to water (use any remaining grog if we were consuming it)
        item = self.items[const.STOCK_WATER_IDX]
        to_consume = (item.consumption_rate * gs.crew.seamen_count) - grog_offset
        if to_consume > 0:  # and it should be
            if to_consume <= item.qty:
                item.qty -= to_consume
                return 0

            # failed to satisfy the need, see if grog remains
            to_consume -= item.qty  # drink remaining water
            item.qty = 0
            item = self.items[const.STOCK_GROG_IDX]
            if item.qty >= to_consume:
                item.qty -= to_consume
                return 0

            item.qty = 0
            return -1
        else:
            return 0  # probably wouldnt get here

    def set_grog_portion(self, i: int):
        """
        Set grog to high, low, nonw
        :param i: const.STOCK_GROG_*
        :return:
        """
        item = self.items[const.STOCK_GROG_IDX]
        if i > const.STOCK_GROG_HIGH or i < const.STOCK_GROG_NONE:
            raise ValueError
        item.consumption_rate = i

    def get_remaining_grog(self):
        return self.items[const.STOCK_GROG_IDX].qty

    def get_grog_portion(self) -> tuple[str, int]:
        """
        :return: a description of the current grog consumption and its constant
        """
        rate = self.items[const.STOCK_GROG_IDX].consumption_rate
        if rate >= const.STOCK_GROG_HIGH:
            return "a generous portion of grog", const.STOCK_GROG_HIGH
        if rate >= const.STOCK_GROG_LOW:
            return "a normal portion of grog", const.STOCK_GROG_LOW
        return "water only", const.STOCK_GROG_NONE

    def consume_medicine(self):
        '''
        Consume units of medicine.
        Normally a single unit is consumed per day.
        Possibly the consumption rate gets increased in certain circumstances
        :return: True if able to consume
        '''
        item = self.items[const.STOCK_MEDICINE_IDX]
        to_consume = item.consumption_rate
        item.qty -= to_consume
        if item.qty < 0:
            item.qty = 0
            return False

        return True


def do_interactive_restock():
    class _restock:
        def __init__(self, stock_idx, description, from_island: bool, price,
                     qty_to_fill, partial: bool,
                     carg_item=None, carg_qty=None):
            self.stock_idx = stock_idx
            self.description = description
            self.from_island = from_island
            self.price = price  # total price to be paid
            self.partial = partial  # true if partial fill
            self.qty_to_fill = qty_to_fill
            self.carg_item: CargoItem = carg_item
            self.carg_qty = carg_qty

    first_time = True
    cash_strapped = False
    while True:
        restock_options: list[_restock] = []
        # a dict keyed off stock idx. value is description
        if gs.player.is_onland():
            place = gs.map.get_place_at_location(gs.ship.location)
            avail_at_island = place.island.available_stock()
        else:
            avail_at_island = {}

        avail_in_cargo = gs.ship.cargo.get_restock()

        need_items = False
        for stock_item in gs.stock.items:
            if stock_item.qty < stock_item.max_qty:
                need_items = True
                name = stock_name[stock_item.idx]
                qty_needed = stock_item.max_qty - stock_item.qty

                # see if this stock item can be restocked from island
                if stock_item.idx in avail_at_island:
                    partial = False
                    price_to_fill = stock_item.price_coeff * qty_needed
                    qty_to_fill = qty_needed
                    if price_to_fill > gs.player.doubloons:
                        # player doesn't have enough money to do a full refill. calc what they can afford
                        cash_strapped = True
                        qty_to_fill = int(gs.player.doubloons / stock_item.price_coeff)
                        price_to_fill = int(qty_to_fill * stock_item.price_coeff)
                        partial = True

                    if qty_to_fill:  # if we can actually afford anything
                        desc = avail_at_island[stock_item.idx]
                        restock_options.append(_restock(stock_item.idx, desc, True,
                                                        price_to_fill, qty_to_fill, partial))

                # see if this stock item can be restocked from ship's cargo
                if stock_item.idx in avail_in_cargo:
                    # this is a tuple of CargoItem and how many stock units each cargo unit can provide
                    x = avail_in_cargo[stock_item.idx]
                    carg: CargoItem = x[0]
                    stock_per_carg = x[1]

                    cargo_units_needed = max(1, int(qty_needed / stock_per_carg))
                    partial = False
                    qty_to_fill = qty_needed
                    if cargo_units_needed > carg.quantity:
                        # don't have enough cargo to fill the stock, so see how much we can fill
                        cargo_units_needed = carg.quantity
                        qty_to_fill = cargo_units_needed * stock_per_carg
                        partial = True

                    desc = (f"Restock {name} "
                            f"using {cargo_units_needed} {cargo_types[carg.type_idx].units} of"
                            f" {carg.type.name} from ship's cargo")
                    restock_options.append(_restock(stock_item.idx, desc, False, None,
                                                    qty_to_fill, partial, carg, cargo_units_needed))

        if not need_items:
            if first_time:
                gs.output(f"{gs.crew.firstmate}: Captain, we are fully supplied with everything we need.")
            return

        if not len(restock_options):
            if first_time:
                if cash_strapped:
                    gs.output(
                        f"{gs.crew.firstmate}: Captain, we don't currently have necessary funds for items we need.")
                else:
                    gs.output(f"{gs.crew.firstmate}: Captain, we don't currently have access to items we need.")
            return

        if first_time:
            gs.output(f"{gs.crew.firstmate}: Captain, these are our options for restocking {gs.ship.name}:")
            first_time = False

        for idx, option in enumerate(restock_options):
            si = gs.stock.items[option.stock_idx]
            have = int(si.qty * 100 / si.max_qty)
            gs.output(f"{idx + 1} - {option.description} (currently {have}%)")

        sel = gs.input_num(1, len(restock_options), "Enter an option or $ when finished")
        if sel < 1:
            return

        ro = restock_options[sel - 1]
        if ro.price is not None:  # from island
            if not ro.price:
                tofill = ro.qty_to_fill
                spend = 0
            else:
                gs.output(f"{gs.crew.firstmate}: We can {'partially' if ro.partial else 'fully'} restock "
                          f"{stock_name[ro.stock_idx]} for {ro.price}D")
                doall = gs.confirm(f"Do you want to spend the full {ro.price}D?", True)
                if doall is None:
                    continue
                if doall:
                    spend = ro.price
                    tofill = ro.qty_to_fill
                else:
                    spend = gs.input_num(1, ro.price, f"We have {gs.player.doubloons}D, How much will we spend?")
                    if spend < 1:
                        if gs.quitting:
                            return
                        continue
                    pctage = spend / ro.price
                    tofill = int(ro.qty_to_fill * pctage)

            gs.player.add_remove_doubloons(-spend)
            gs.stock.items[ro.stock_idx].qty += tofill
            if spend:
                txt = f"We paid {spend}D to restock"
            else:
                txt = f"We restocked"
            gs.output(f"{gs.crew.firstmate}: {txt} {stock_name[ro.stock_idx]}. "
                      f"We are now at {int(100 * gs.stock.items[ro.stock_idx].qty / gs.stock.items[ro.stock_idx].max_qty)}%.")
        elif ro.carg_item:  # from cargo
            gs.ship.cargo.add_remove(ro.carg_item.type_idx, -ro.carg_qty)
            gs.stock.items[ro.stock_idx].qty += ro.qty_to_fill
            gs.output(f"{gs.crew.firstmate}: We restocked {stock_name[ro.stock_idx]} using cargo. "
                      f"We are now at {int(100 * gs.stock.items[ro.stock_idx].qty / gs.stock.items[ro.stock_idx].max_qty)}%.")
        else:
            raise ValueError
        gs.output("")


def do_full_restock():
    '''
    Note that this should only be used during setup phase as no checks are made as to the
    availability of items
    :return:
    '''
    total_d = 0
    for stock_item in gs.stock.items:
        if stock_item.qty < stock_item.max_qty:
            qty_needed = stock_item.max_qty - stock_item.qty
            price_to_fill = stock_item.price_coeff * qty_needed
            total_d += price_to_fill
            stock_item.qty = stock_item.max_qty
    if total_d > gs.player.doubloons:
        return None
    gs.player.add_remove_doubloons(-total_d)
    return int(total_d)
