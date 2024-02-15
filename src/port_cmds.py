from command import RunType, Command
from islands import TradingPost
from state import gs
from cargo import cargo_types, cargo_type_lookup
from util import as_int, to_proper_case


def register_port_cmds():
    gs.cmdsys.register(Command("dock",  dock_cmd,
                               "Dock your ship at a port. This will allow port activities."))
    gs.cmdsys.register(Command("depart",  depart_cmd,
                               "Depart from an island and return to the seas."))
    gs.cmdsys.register(Command("trade",  trade_list_cmd,
                               "List cargo for buying and selling."))
    gs.cmdsys.register(Command("buy",  trade_buy_cmd,
                               "Buy cargo."))
    gs.cmdsys.register(Command("sell",  trade_sell_cmd,
                               "Sell cargo."))


def dock_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            p = gs.map.get_place_at_location(gs.ship.location)
            if p and p.island.port:
                return True
        return False
    if rt == RunType.HELP:
        gs.output(
            "If you are nearby an island with a port, you may dock your ship at that port.")
        return
    if not toks:
        p = gs.map.get_place_at_location(gs.ship.location)
        dist = gs.ship.distance_to_location(gs.ship.location)
        if dist > 0:
            gs.output(f"{gs.crew.boatswain}: We are {dist} miles away from the island, and can't dock until we are closer.")

            return
        if p and p.island.port:
            gs.player.set_state_docked()
            gs.output(f"{gs.crew.boatswain}: {gs.ship.name} is now docked at {p.island.port.name} on the island of {p.island.name}.")
            gs.ship.b.reset()


def depart_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_exploring() or gs.player.is_docked():
            return True
        return False
    if rt == RunType.HELP:
        gs.output(
            "This command allows you to embark.")
        return
    if not toks:
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
        if gs.player.is_docked():
            place = gs.map.get_place_at_location(gs.ship.location)
            if place and place.island and place.island.port:  # should be true
                return True
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
    if place and place.island.port:  # should be true
        t = place.island.port.trader

    if not t:
        gs.gm_output("There is no trading available here.")
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
            gs.output(f"[{wtb.type.code}] {wtb.type.name} {wtb.quantity} {wtb.type.units} - {wtb.price_per}D ea.{youhave}")
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
        current_basis = int((have_it.price_per+carg.price_per)/2)
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
        gs.output(f"{pm.first}: You are trying to sell more than you have. You must not try to deal with me in a crooked manner!")
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