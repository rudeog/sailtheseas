from command import RunType, Command
from state import gs

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
        if gs.ship.distance_to_location(gs.ship.location)>0:
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
    if rt == RunType.HELP:
        gs.output(
            "If you are docked at a port you may buy or sell goods.")
        return

    # the question is, do we have a separate state for trading or just add args to trade
    place = gs.map.get_place_at_location(gs.ship.location)
    if place.island.port: # should be true

        t = place.island.port.trader
        gs.output("Available items to buy")
        for avail in t.on_hand:
            gs.output(f"[{avail.type.code}] {avail.type.name} - {avail.quantity} {avail.type.units} - {avail.price_per} dbl ea.")

