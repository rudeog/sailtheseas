from names import NameGenerator
from place_descriptions import PlaceGenerator
import const
import cargo
import logging
from state import gs

# what each one produces
# gold is going to be special and should be produced in very small qty
production_table = {const.ISLAND_CLASS_NONE: [],
                    const.ISLAND_CLASS_TROPICAL: [cargo.CARGO_FOOD, cargo.CARGO_RUM],
                    const.ISLAND_CLASS_FARMING: [cargo.CARGO_LIVESTOCK],
                    const.ISLAND_CLASS_AGRI: [cargo.CARGO_GRAIN],
                    const.ISLAND_CLASS_FOREST: [cargo.CARGO_LUMBER],
                    const.ISLAND_CLASS_MINING: [cargo.CARGO_IRON, cargo.CARGO_GOLD],
                    const.ISLAND_CLASS_MFG: [cargo.CARGO_MFG],
                    const.ISLAND_CLASS_COMMERCE: []
                    }
# what each one consumes
# earlier in list means higher consumption
consumption_table = {const.ISLAND_CLASS_NONE: [],
                     const.ISLAND_CLASS_TROPICAL: [cargo.CARGO_MFG, cargo.CARGO_GRAIN, cargo.CARGO_IRON,
                                             cargo.CARGO_LIVESTOCK],
                     const.ISLAND_CLASS_FARMING: [cargo.CARGO_GRAIN, cargo.CARGO_MFG, cargo.CARGO_RUM, cargo.CARGO_LUMBER],
                     const.ISLAND_CLASS_AGRI: [cargo.CARGO_MFG, cargo.CARGO_IRON, cargo.CARGO_LUMBER, cargo.CARGO_RUM,
                                         cargo.CARGO_LIVESTOCK],
                     const.ISLAND_CLASS_FOREST: [cargo.CARGO_FOOD, cargo.CARGO_MFG, cargo.CARGO_LIVESTOCK, cargo.CARGO_GRAIN,
                                           cargo.CARGO_IRON],
                     const.ISLAND_CLASS_MINING: [cargo.CARGO_LUMBER, cargo.CARGO_FOOD, cargo.CARGO_RUM, cargo.CARGO_MFG],
                     const.ISLAND_CLASS_MFG: [cargo.CARGO_IRON, cargo.CARGO_LUMBER, cargo.CARGO_LIVESTOCK],
                     const.ISLAND_CLASS_COMMERCE: [cargo.CARGO_GOLD, cargo.CARGO_MFG, cargo.CARGO_FOOD, cargo.CARGO_RUM],
                     }


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

    def get(self):
        return {"have": self.on_hand.get(), "want": self.want.get()}

    def set(self, d: dict):
        have = d["have"]
        want = d["want"]
        self.on_hand.set(have)
        self.want.set(want)

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
        logging.log("trade", f"update tradingpost. pc:"
                             f" {const.class_descriptions[self.primary_class]}, sc: "
                             f"{const.class_descriptions[self.secondary_class]}")
        pt = production_table[self.primary_class]
        logging.log("trade", "  primary production")
        for pi in pt:
            ct = cargo.cargo_types[pi]
            qty = ct.prod_coefficient * 3  # normal amount the island produces
            existing = self.on_hand[pi]
            # cap it off at 2x the production
            if existing:
                qty = min(qty * 2 - existing.quantity, qty)
            self.on_hand.add_remove(pi, qty)

        pt = production_table[self.secondary_class]
        logging.log("trade", "  secondary production")
        for pi in pt:
            ct = cargo.cargo_types[pi]
            qty = ct.prod_coefficient * 2
            existing = self.on_hand[pi]
            # cap it off at 2x the production
            if existing:
                qty = min(qty * 2 - existing.quantity, qty)
            self.on_hand.add_remove(pi, qty)

        # set prices
        for ci in self.on_hand:
            ct = cargo.cargo_types[ci.type_idx]
            normal = ct.prod_coefficient * 3  # considered the 'normal qty on hand'
            qty = ci.quantity
            if qty:
                # price is steady unless we have more than normal in which case price goes down
                ce = min(float(normal) / float(qty), 1.0)
                price = int(ct.price_coefficient * ce)
                self.on_hand.set_price(ci.type_idx, price)

        # want to buy. we will use prod coefficient for now to determine need
        logging.log("trade", "  primary consumption")
        self._update_wtb(3, consumption_table[self.primary_class])
        logging.log("trade", "  secondary consumption")
        self._update_wtb(2, consumption_table[self.secondary_class])

        # if island consumes what it produces, remove the right amt of available resources
        logging.log("trade", "  consume self produced")
        for need in self.want:
            got = self.on_hand[need.type_idx]
            if got is not None:
                gq = got.quantity  # because add_remove will adjust this ptr
                nq = need.quantity
                self.on_hand.add_remove(need.type_idx, -nq)
                self.want.add_remove(need.type_idx, -gq)

        # set prices based on demand
        for ci in self.want:
            ct = cargo.cargo_types[ci.type_idx]
            normal = ct.prod_coefficient * 3  # considered the 'normal qty wanted'
            qty = ci.quantity
            if qty:
                # if we want more than normal, the price goes up, if we want less than normal we still
                # honor the base price
                ce = max((float(qty) / float(normal), 1.0)) + 0.15
                price = int(ct.price_coefficient * ce)
                self.want.set_price(ci.type_idx, price)

    def _update_wtb(self, mult, wanttobuy):
        for pi in wanttobuy:  # earlier in list is higher consumption
            ct = cargo.cargo_types[pi]
            qty = mult * ct.prod_coefficient
            existing = self.want[pi]
            # cap it off at 2x the want
            if existing:
                qty = min(qty * 2 - existing.quantity, qty)
            self.want.add_remove(pi, qty)
            mult = mult - (1 if mult > 1 else 0)


class Port:
    def __init__(self, civ_type, primary_class, secondary_class, ng: NameGenerator, pg: PlaceGenerator, ethnicity,
                 map_rng):

        if map_rng.random() < .4:
            # use a name rather than a place
            port_name = "Port " + ng.name("", ethnicity).last
        else:
            port_name = str(pg.name(ethnicity)) + " Harbor"
        self.port_master = ng.name("")  # might be ethnic
        self.name = port_name
        self.civ_type = civ_type
        self.primary_class = primary_class
        self.secondary_class = secondary_class
        self.trader: TradingPost = TradingPost(civ_type, primary_class, secondary_class)

        # note - port doesnt have any save data right now as its generated.
        # be aware if adding save data

# given an island index, do an update on the trading data there
def update_trading_post(idx):
    isl = gs.map.get_place_by_index(idx).island
    if isl.port:
        isl.port.trader.update()