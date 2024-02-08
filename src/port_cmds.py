from command import RunType, Command
from islands import TradingPost
from state import gs
from cargo import cargo_types, cargo_type_lookup
from util import as_int

def register_port_cmds():
    gs.cmdsys.register(Command("dock", "", dock_cmd,
                               "Dock your ship at a port. This will allow port activities."))
    gs.cmdsys.register(Command("depart", "", depart_cmd,
                               "Depart from a port."))
    gs.cmdsys.register(Command("trade", "", trade_cmd,
                               "Buy/sell"))


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
        if gs.ship.distance_to_location(gs.ship.location) > 0:
            gs.output("You are not close enough to the island to dock")
            return
        if p and p.island.port:
            gs.player.set_state_docked()
            gs.output(f"{gs.ship.name} is now docked at {p.island.port.name} on the island of {p.island.name}.")
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
        gs.output(f"{gs.ship.name} has departed from {p.island.name}.")


def trade_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_docked():
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
        gs.output(
            "The trade command has subcommands:")
        gs.output("list - list items that the port is selling or wants to buy (ie 'trade list')")
        gs.output("buy - buy an item. Specify quantity and item code. Eg 'trade buy 10 mg'")
        gs.output("sell - sell an item. Specify quantity to sell and an item code. Eg 'trade sell 5 pf'")
        gs.output("You may also specify 'all' instead of a quantity to either buy or sell the max available.")
        return

    place = gs.map.get_place_at_location(gs.ship.location)
    if place.island.port:  # should be true
        t = place.island.port.trader
    else:
        gs.gm_output("There is no trading available here.")
        return

    if toks[0] == 'list':
        gs.output("Available items to buy")
        for avail in t.on_hand:
            gs.output(
                f"[{avail.type.code}] {avail.type.name} - {avail.quantity} {avail.type.units} - {avail.price_per}D ea.")

        gs.output("")
        gs.output("Want to buy")
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
                gs.gm_output("Quantity entered must be a number or 'all'.")
                return
        else:
            quant = -1

        cti = cargo_type_lookup[type_code]
        if toks[0] == 'buy':
            trade_buy(t, quant, cti)
        else:
            trade_sell(t, quant, cti)


def trade_buy(t: TradingPost, qty, type_idx):
    carg = t.on_hand[type_idx]
    if not carg:
        gs.gm_output("That item type is not available for sale.")
        return

    if qty == -1:  # all
        qty = carg.quantity
    elif qty > carg.quantity or qty < 0:
        gs.gm_output("The amount that you want to buy is not available.")
        return

    if qty * carg.price_per > gs.player.doubloons:
        gs.gm_output(f"It appears that you don't have sufficient funds to make a purchase of {qty * carg.price_per}D.")
        return

    ct = cargo_types[type_idx]
    weight = qty * ct.weight_per_unit
    if gs.ship.cargo.total_weight() + weight > gs.ship.cargo_capacity:
        avail = int((gs.ship.cargo_capacity - gs.ship.cargo.total_weight()) / 2000)
        if weight < 2000:
            wt = f"{weight} pounds"
        else:
            wt = f"{int(weight / 2000)} tons"
        gs.gm_output(f"Your ship has {avail} tons of remaining capacity, and "
                     f"would be overburdened with the additional weight of {wt}.")
        return

    # its a go
    t.on_hand.add_remove(type_idx, -qty)
    gs.ship.cargo.add_remove(type_idx, qty)
    sale_price = qty * carg.price_per
    gs.player.add_remove_doubloons(-sale_price)
    gs.gm_output(f"You purchased {qty} {ct.units} of {ct.name} at a price of {sale_price}D.")


def trade_sell(t: TradingPost, qty, type_idx):
    my_cargo = gs.ship.cargo[type_idx]
    if not my_cargo:
        gs.gm_output(f"You don't have any {cargo_types[type_idx].name} to sell.")
        return

    want_carg = t.want[type_idx]
    if not want_carg:
        gs.gm_output("That item type is not wanted at this time.")
        return

    if qty == -1:  # all
        qty = my_cargo.quantity
    elif qty > my_cargo.quantity or qty < 0:
        gs.gm_output("You are trying to sell more than you have. You must not try to deal in a crooked manner!")
        return

    if qty > want_carg.quantity:
        gs.gm_output("The quantity you are trying to sell is more than is wanted at this time.")
        return

    t.want.add_remove(type_idx, -qty)
    # todo recalc cost basis on ships cargo
    gs.ship.cargo.add_remove(type_idx, -qty)
    sale_price = qty * want_carg.price_per
    gs.player.add_remove_doubloons(sale_price)

    gs.gm_output(f"You sold {qty} {cargo_types[type_idx].units} of {cargo_types[type_idx].name} "
                 f"for a total price of {sale_price}D.")
