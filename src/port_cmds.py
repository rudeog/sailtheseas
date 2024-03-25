from command import RunType, Command
from islands import TradingPost
from state import gs
from cargo import cargo_types, cargo_type_lookup, CargoItem
from explore import do_explore
from util import as_int, to_proper_case
import stock


def register_port_cmds():
    gs.cmdsys.register(Command("land", land_cmd,
                               "Land on an island. If the island has a port you will dock at the "
                               "port, otherwise you will drop anchor and disembark."))
    gs.cmdsys.register(Command("depart", depart_cmd,
                               "Depart from an island and return to the seas."))
    gs.cmdsys.register(Command("trade", trade_list_cmd,
                               "List cargo for buying and selling."))
    gs.cmdsys.register(Command("buy", trade_buy_cmd,
                               "Buy cargo."))
    gs.cmdsys.register(Command("sell", trade_sell_cmd,
                               "Sell cargo."))
    gs.cmdsys.register(Command("explore", explore_cmd,
                               "Explore the island."))
    gs.cmdsys.register(Command("restock",  restock_cmd,
                               "Restock your ship with supplies."))


def restock_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output("You can restock your ship at any port. If you are at sea, you may be able to "
                  "restock some of your supplies from cargo that you are carrying.")
        return


    class _restock:
        def __init__(self, stock_idx, description, from_island:bool, price,
                     qty_to_fill, partial:bool,
                     carg_item=None, carg_qty=None):
            self.stock_idx = stock_idx
            self.description = description
            self.from_island = from_island
            self.price = price  # total price to be paid
            self.partial = partial  # true if partial fill
            self.qty_to_fill = qty_to_fill
            self.carg_item: CargoItem = carg_item
            self.carg_qty = carg_qty


    first_time=True
    cash_strapped=False
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
                name = stock.stock_name[stock_item.idx]
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
                        price_to_fill = qty_to_fill * stock_item.price_coeff
                        partial = True

                    if qty_to_fill: # if we can actually afford anything
                        desc = avail_at_island[stock_item.idx]
                        desc = ("Partially " if partial else "Fully ") + desc
                        desc += f" (cost {price_to_fill}D)"
                        restock_options.append(_restock(stock_item.idx,desc, True,
                                                        price_to_fill, qty_to_fill, partial))

                # see if this stock item can be restocked from ship's cargo
                if stock_item.idx in avail_in_cargo:
                    # this is a tuple of CargoItem and how many stock units each cargo unit can provide
                    x = avail_in_cargo[stock_item.idx]
                    carg: CargoItem = x[0]
                    stock_per_carg = x[1]

                    cargo_units_needed = max(1,int(qty_needed / stock_per_carg))
                    partial = False
                    qty_to_fill = qty_needed
                    if cargo_units_needed > carg.quantity:
                        # don't have enough cargo to fill the stock, so see how much we can fill
                        cargo_units_needed = carg.quantity
                        qty_to_fill = cargo_units_needed * stock_per_carg
                        partial = True

                    desc = (f"restock {name} "
                            f"using {cargo_units_needed} {cargo_types[carg.type_idx].units} of"
                            f" {carg.type.name} from ship's cargo")
                    desc = ("Partially " if partial else "Fully ") + desc
                    restock_options.append(_restock(stock_item.idx, desc, False, None,
                                                    qty_to_fill, partial, carg, cargo_units_needed ))

        if not need_items:
            if first_time:
                gs.output(f"{gs.crew.firstmate}: Captain, we are fully supplied with everything we need.")
            return

        if not len(restock_options):
            if first_time:
                if cash_strapped:
                    gs.output(f"{gs.crew.firstmate}: Captain, we don't currently have necessary funds for items we need.")
                else:
                    gs.output(f"{gs.crew.firstmate}: Captain, we don't currently have access to items we need.")
            return

        if first_time:
            gs.output(f"{gs.crew.firstmate}: Captain, these are our current options for restocking {gs.ship.name}:")

        first_time=False
        while True:
            for idx, option in enumerate(restock_options):
                gs.output(f"{idx+1} - {option.description}")


            sel = gs.input("Enter a number or $ to cancel: ")
            gs.output("")
            if sel == '$':
                return
            if sel == '!':
                gs.quitting = True
                return

            nsel = as_int(sel)
            if nsel < 1 or nsel > len(restock_options):
                gs.gm_output(f"Please enter one of the available options, {gs.player.name}.")
                gs.output("")
            else:
                break

        ro = restock_options[nsel-1]
        if ro.price is not None:
            gs.player.add_remove_doubloons(-ro.price)
            gs.stock.items[ro.stock_idx].qty += ro.qty_to_fill
            if ro.price:
                txt = f"We paid {ro.price}D to restock"
            else:
                txt = f"We restocked"
            gs.output(f"{gs.crew.firstmate}: {txt} {stock.stock_name[ro.stock_idx]}. "
                      f"We are now at {int(100*gs.stock.items[ro.stock_idx].qty/gs.stock.items[ro.stock_idx].max_qty)}%.")
        elif ro.carg_item:
            gs.ship.cargo.add_remove(ro.carg_item.type_idx, -ro.carg_qty)
            gs.output(f"{gs.crew.firstmate}: We restocked {stock.stock_name[ro.stock_idx]} using cargo. "
                      f"We are now at {int(100*gs.stock.items[ro.stock_idx].qty/gs.stock.items[ro.stock_idx].max_qty)}%.")
        else:
            raise ValueError
        gs.output("")





def land_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            # we will show the command even if unavailable to give the opportunity to explain that we still need to sail
            p = gs.map.get_place_at_location(gs.ship.location)
            if p:
                return True
        return False
    if rt == RunType.HELP:
        gs.output(
            "If you are at an island, you may land your ship there. Landing at an island with "
            "a port will dock you at that port. Landing at an island without a port will mean dropping anchor "
            "and going ashore with your crew.")
        return
    if not toks:
        p = gs.map.get_place_at_location(gs.ship.location) # should alway succeed due to above check
        dist = gs.ship.distance_to_location(gs.ship.location)
        if dist > 0:
            gs.output(
                f"{gs.crew.boatswain}: We are {dist} miles away from the island, and can't land until we are close to shore.")

            return
        gs.player.set_state_landed()
        if p.island.port:
            gs.output(
                f"{gs.crew.boatswain}: {gs.ship.name} is now docked at {p.island.port.name} on the island of {p.island.name}.")
        else:
            gs.output(f"{gs.crew.boatswain}: {gs.ship.name} has dropped anchor and the crew has gone ashore.")
        gs.ship.b.reset() # reset bearing since we are not sailing


def depart_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_onland():
            return True
        return False
    if rt == RunType.HELP:
        gs.output(
            "This command allows you to embark.")
        return
    if not toks:
        if gs.stock.check_stock() and not gs.gm_confirm("Do you want to depart anyway without restocking?"):
            return
        gs.player.set_state_sailing()
        p = gs.map.get_place_at_location(gs.ship.location)
        gs.output(f"{gs.crew.boatswain}: {gs.ship.name} has departed from {p.island.name}.")


def _show_bs_help():
    gs.output("The trading commands allow you to buy and sell goods. "
              "The 'trade' command lists items that are available for purchase and also items that are wanted "
              "by the island.")
    gs.output("Use the 'buy' and 'sell' commands to buy and sell products using their codes as follows:")
    gs.output("  buy <qty> <code>")
    gs.output("  sell <qty> <code>")
    gs.output("You may also specify 'all' instead of a quantity to either buy or sell the max available.")
    gs.output("Examples:")
    gs.output("  'buy 10 gr' - buy 10 units of grain.")
    gs.output("  'sell all lu' - sell all lumber in cargo.")


def trade_list_cmd(rt: RunType, toks):
    return trade_shared_cmd(rt, ['list'] + toks)


def trade_buy_cmd(rt: RunType, toks):
    return trade_shared_cmd(rt, ['buy'] + toks)


def trade_sell_cmd(rt: RunType, toks):
    return trade_shared_cmd(rt, ['sell'] + toks)


def trade_shared_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_onland():
            place = gs.map.get_place_at_location(gs.ship.location)
            if place:  # should be true
                return True # we'll let it succeed even if no trading to let them know that fact
        return False

    help = False
    if rt == RunType.HELP:
        help = True
    elif len(toks) != 1 and len(toks) != 3:
        help = True
    elif len(toks) == 1 and toks[0] != 'list':
        help = True
    elif len(toks) == 3 and toks[0] not in ['buy', 'sell', 'list']:
        help = True
    if help:
        _show_bs_help()
        return

    t = None
    place = gs.map.get_place_at_location(gs.ship.location)
    if place and place.island and place.island.port:  # should be true
        t = place.island.port.trader

    if not t:
        gs.gm_output(f"There is no trading available on {place.island.name}.")
        return
    pm = place.island.port.port_master
    if toks[0] == 'list':
        gs.output(f"Port manager {pm} has these items available to buy:")
        for avail in t.on_hand:
            max_afford = int(gs.player.doubloons / avail.price_per)
            if max_afford >= avail.quantity:
                ycb = "(you can buy all)"
            elif max_afford == 0:
                ycb = "(you can't afford this)"
            else:
                ycb = f"(you can afford {max_afford} {avail.type.units})"

            gs.output(
                f"[{avail.type.code}] {avail.type.name} - {avail.quantity} {avail.type.units} - {avail.price_per}D ea. {ycb}")

        gs.output("")
        gs.output(f"{to_proper_case(pm.pronoun())} is looking to buy these items:")
        for wtb in t.want:
            incargo = gs.ship.cargo[wtb.type_idx]
            if incargo:
                youhave = f" (you have {incargo.quantity} {wtb.type.units})"
            else:
                youhave = ""
            gs.output(
                f"[{wtb.type.code}] {wtb.type.name} {wtb.quantity} {wtb.type.units} - {wtb.price_per}D ea.{youhave}")
        gs.output("")
        gs.gm_output(f"You have {gs.player.doubloons}D "
                     f"and {int((gs.ship.cargo_capacity - gs.ship.cargo.total_weight()) / 2000)} "
                     "tons of remaining cargo capacity")
    else:
        qty = toks[1]
        type_code = toks[2]
        if type_code not in cargo_type_lookup:
            gs.gm_output("That is an invalid code. Please enter a valid two letter code from the list.")
            return

        if qty != 'all':
            quant = as_int(qty)
            if quant < 0:
                gs.gm_output(f"Quantity entered must be a number or 'all'.")
                return
        else:
            quant = -1

        cti = cargo_type_lookup[type_code]
        if toks[0] == 'buy':
            trade_buy(t, quant, cti, pm)
        else:
            trade_sell(t, quant, cti, pm)


def trade_buy(t: TradingPost, qty, type_idx, pm):
    carg = t.on_hand[type_idx]
    if not carg:
        gs.output(f"{pm.first}: I don't have any of that for sale.")
        return

    if qty < 0:  # all
        qty = carg.quantity
    elif qty > carg.quantity or qty < 0:
        gs.output(f"{gs.crew.firstmate}: That is more than we have available, captain.")
        return

    if qty * carg.price_per > gs.player.doubloons:
        gs.gm_output(f"You don't have sufficient funds to make a purchase of {qty * carg.price_per}D. "
                     "You only have {gs.player.doubloons}D.")
        return

    ct = cargo_types[type_idx]
    weight = qty * ct.weight_per_unit
    if gs.ship.cargo.total_weight() + weight > gs.ship.cargo_capacity:
        avail = int((gs.ship.cargo_capacity - gs.ship.cargo.total_weight()) / 2000)
        if weight < 2000:
            wt = f"{weight} pounds"
        else:
            wt = f"{int(weight / 2000)} tons"
        gs.output(f"{gs.crew.firstmate}: We have {avail} tons of remaining capacity, and "
                  f"would be overburdened with the additional weight of {wt}.")
        return

    # its a go
    t.on_hand.add_remove(type_idx, -qty)

    # do we already have this type of cargo
    have_it = gs.ship.cargo[type_idx]
    if have_it:
        current_basis = int((have_it.price_per + carg.price_per) / 2)
    else:
        current_basis = carg.price_per

    gs.ship.cargo.add_remove(type_idx, qty)
    gs.ship.cargo.set_price(type_idx, current_basis)
    sale_price = qty * carg.price_per
    gs.player.add_remove_doubloons(-sale_price)
    gs.gm_output(f"You purchased {qty} {ct.units} of {ct.name} at a price of {sale_price}D. "
                 f"This leaves you with {gs.player.doubloons}D.")
    gs.output(f"{pm.first}: It's a pleasure doing business with you.")


def trade_sell(t: TradingPost, qty, type_idx, pm):
    my_cargo = gs.ship.cargo[type_idx]
    if not my_cargo:
        gs.output(f"{gs.crew.firstmate}: Captain, we don't have any {cargo_types[type_idx].name} to sell.")
        return

    want_carg = t.want[type_idx]
    if not want_carg:
        gs.output(f"{pm.first}: I don't want any {my_cargo.type.name} at this time.")
        return

    if qty == -1:  # all
        qty = my_cargo.quantity
    elif qty > my_cargo.quantity or qty < 0:
        gs.output(
            f"{pm.first}: You are trying to sell more than you have. You must not try to deal with me in a crooked manner!")
        return

    if qty > want_carg.quantity:
        gs.output(f"{pm.first}: The quantity you are trying to sell is more than I want at this time.")
        return

    # it's a go
    prof_loss = qty * (want_carg.price_per - my_cargo.price_per)
    if prof_loss < 0:
        pl = "loss"
    else:
        pl = "profit"

    t.want.add_remove(type_idx, -qty)

    gs.ship.cargo.add_remove(type_idx, -qty)
    sale_price = qty * want_carg.price_per
    gs.player.add_remove_doubloons(sale_price)

    gs.gm_output(f"You sold {qty} {cargo_types[type_idx].units} of {cargo_types[type_idx].name} "
                 f"for a total price of {sale_price}D which yields a {pl} of {prof_loss}D. "
                 f"You now have {gs.player.doubloons}D.")
    gs.output(f"{pm.first}: Looking forward to doing more business with you.")

def explore_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_onland():
            return True
        return False
    if rt == RunType.HELP:
        gs.output(f"The islands of {gs.world_name} are fascinating places. You never know what you'll find when you "
                  "explore them. Each time you run the 'explore' command you will explore a certain percentage of the "
                  "island you are landed on. Once this reaches 100% then no further exploration is necessary.")

    place = gs.map.get_place_at_location(gs.ship.location)
    if place and place.island:  # should be true
        do_explore(place.island)
