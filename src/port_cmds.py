from command import RunType, Command
from player import PlayerState
from state import gs

def register_port_cmds():
    gs.cmdsys.register(Command("dock", "", dock_cmd,
                                     "Dock your ship at a port. This will allow port activities."))
    gs.cmdsys.register(Command("depart", "", depart_cmd,
                               "Depart from a port."))

def dock_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.state is PlayerState.SAILING:
            p = gs.map.get_place_at_location(gs.player.ship.location)
            if p and p.port:
                return True
        return False
    if rt == RunType.HELP:
        gs.output(
            "If you are nearby an island with a port, you may dock your ship at that port.")
        return
    if not toks:
        p = gs.map.get_place_at_location(gs.player.ship.location)
        if p and p.port:
            gs.player.state = PlayerState.DOCKED
            gs.output(f"{gs.player.ship.name} is now docked at {p.port.name} on the island of {p.name}.")
            gs.player.ship.bearing.reset()

def depart_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.state in (PlayerState.DOCKED, PlayerState.EXPLORING):
            return True
        return False
    if rt == RunType.HELP:
        gs.output(
            "This command allows you to embark.")
        return
    if not toks:
        gs.player.state = PlayerState.SAILING
        p = gs.map.get_place_at_location(gs.player.ship.location)
        gs.output(f"{gs.player.ship.name} has departed from {p.name}.")