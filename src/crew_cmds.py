import state
from command import Command, RunType
from state import gs
import crew
from stock import STOCK_RATIONS_FULL, STOCK_RATIONS_REDUCED, STOCK_RATIONS_MEAGER, STOCK_GROG_HIGH, STOCK_GROG_NONE, \
    STOCK_GROG_LOW
from util import as_int

def register_crew_cmds():
    gs.cmdsys.register(Command("crew",  describe_crew_cmd, "Show information about your crew"))
    gs.cmdsys.register(Command("hiring", hire_fire_cmd,
                               "Hire or fire able-bodied seamen."))
    gs.cmdsys.register(Command("payroll", pay_crew_cmd,
                               "Pay any amount due to crew of able-bodied seamen."))
    gs.cmdsys.register(Command("ration", rations_cmd,
                               "Set the rationing level for able-bodied seamen."))
    gs.cmdsys.register(Command("grog", grog_cmd,
                               "Set the grog apportionment for able-bodied seamen."))


def rations_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP or not toks:
        rats, _ = gs.stock.get_rations()
        gs.output(f"{gs.crew.boatswain}: The crew is on {rats} rations, captain.")
        gs.output("You may adjust the amount of food rations that your crew get while at sea. To do this "
                  "use the ration command followed by a ration level. The following ration levels are valid:"  )
        gs.output("  - full - The crew receives a full portion of food every day")
        gs.output("  - reduced - The crew receives a reduced portion of food every day")
        gs.output("  - meager - The crew receives a very small portion of food every day")
        gs.output("Example: 'ration full")

        return

    if toks[0] not in ['full','meager','reduced']:
        gs.gm_output("Please enter a valid ration amount!")
        return

    _, orig = gs.stock.get_rations()

    if toks[0]=='full':
        gs.stock.set_rations(STOCK_RATIONS_FULL)

    elif toks[0]=='reduced':
        gs.stock.set_rations(STOCK_RATIONS_REDUCED)
    elif toks[0]=='meager':
        gs.stock.set_rations(STOCK_RATIONS_MEAGER)

    rats, cur = gs.stock.get_rations()
    if cur == orig:
        gs.output(f"{gs.crew.boatswain}: Captain, the crew is already on {rats} rations.")
    else:
        gs.output(f"{gs.crew.boatswain}: Captain, I've switched the crew to {rats} rations.")

def grog_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP or not toks:
        grog, _ = gs.stock.get_grog_portion()
        gs.output(f"{gs.crew.boatswain}: The crew is on {grog}, captain.")
        gs.output("You may adjust whether or not the crew get grog while at sea. To do this "
                  "use the grog command followed by a level. The following levels are valid:"  )
        gs.output("  - extra - The crew receives a generous amount of grog every day")
        gs.output("  - normal - The crew receives a normal amount of grog every day")
        gs.output("  - none - The crew receives no grog and must drink water instead")
        gs.output("Example: 'grog extra'")

        return

    if toks[0] not in ['extra','normal','none']:
        gs.gm_output("Please enter a valid grog allotment!")
        return

    _, orig = gs.stock.get_grog_portion()

    if toks[0]=='extra':
        gs.stock.set_grog_portion(STOCK_GROG_HIGH)
    elif toks[0]=='normal':
        gs.stock.set_grog_portion(STOCK_GROG_LOW)
    elif toks[0]=='none':
        gs.stock.set_grog_portion(STOCK_GROG_NONE)

    grog, cur = gs.stock.get_grog_portion()
    if cur == orig:
        gs.output(f"{gs.crew.boatswain}: Captain, the crew is already on {grog}.")
    else:
        gs.output(f"{gs.crew.boatswain}: Captain, I've informed the crew that they are on {grog}.")



def describe_crew_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output("This gives more details about your crew.")
        return

    gs.crew.describe()



def hire_fire_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        if gs.player.is_onland():
            # can only hire/fire when docked at a port
            place = gs.map.get_place_at_location(gs.ship.location)
            if place and place.island and place.island.port:
                return True
        return False

    if rt == RunType.HELP or not toks:
        gs.output(f"This allows you to set your current staffing level for able-bodied seamen (ABS) by either "
                  f"hiring or firing ABS. {crew.pay_description()}")
        gs.output(f"You currently have {gs.crew.seamen_count} ABS. To set the number of ABS, "
            "enter 'hiring' followed by a number. Eg 'hiring 50'.")
        return

    ct = as_int(toks[0], 0)
    if ct <= state.ABS_COUNT_NONFUNCTIONAL or ct > state.ABS_COUNT_MAX:
        gs.gm_output(f"You must enter an amount within the range {state.ABS_COUNT_NONFUNCTIONAL+1} and "
                     f"{state.ABS_COUNT_MAX}")
        return
    delta = ct-gs.crew.seamen_count
    prorate = gs.crew.set_seamen_count(ct)
    if delta > 0:
        if prorate:
            gs.output(f"{gs.crew.boatswain}: Hiring the extra ABS has cost us {prorate}D which must now be paid.")
        else:
            gs.output(f"{gs.crew.boatswain}: We hired {delta} extra ABS.")
    elif delta < 0:
        gs.output(f"{gs.crew.boatswain}: We fired {-delta} ABS. We wish them well in their future endeavors.")
    else:
        gs.gm_output("You already have this number of ABS. No changes in staffing have been made.")


def pay_crew_cmd(rt: RunType, toks):
    if rt == RunType.CHECK_AVAILABLE:
        return True
    if rt == RunType.HELP:
        gs.output("This will pay any amount that is due your crew of able-bodied seamen. If you have an amount due, "
                  "you will not be able to depart from a port or purchase any items until the amount is paid in full.")
        return
    ad = gs.crew.amt_due()
    if ad > 0:
        ap = gs.crew.pay_crew()
        if not ap:
            gs.output(f"{gs.crew.boatswain}: We don't have the necessary {ad}D to pay our crew of able-bodied seamen.")
        else:
            gs.output(f"{gs.crew.boatswain}: The crew of able-bodied seamen has been paid {ap}D.")

    else:
        gs.output(f"{gs.crew.boatswain}: It looks like we don't owe the crew any doubloons at this time, captain.")
