from command import RunType, Command
from state import gs

def register_port_cmds():
    gs.cmdsys.register(Command("dock", "", dock_cmd,
                                     "Dock your ship at a port. This will allow port activities."))
    gs.cmdsys.register(Command("depart", "", depart_cmd,
                               "Depart from a port."))

def dock_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_sailing():
            p = gs.map.get_place_at_location(gs.ship.location)
            if p and p.port:
                return True
        return False
    if rt == RunType.HELP:
        gs.output(
            "If you are nearby an island with a port, you may dock your ship at that port.")
        return
    if not toks:
        p = gs.map.get_place_at_location(gs.ship.location)
        if p and p.port:
            gs.player.set_state_docked()
            gs.output(f"{gs.ship.name} is now docked at {p.port.name} on the island of {p.name}.")
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
        gs.output(f"{gs.ship.name} has departed from {p.name}.")