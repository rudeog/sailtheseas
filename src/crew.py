from datetime import timedelta

import state
import util
from state import gs
from util import to_proper_case

NUM_ROLES = 9
# descriptive
roles = ['boatswain', 'first mate', 'carpenter', 'navigator', 'surgeon', 'lookout', 'cook', 'chaplain', "gunner"]
# matches to class attributes that are created on Crew
role_attrs = ['boatswain', 'firstmate', 'carpenter', 'navigator', 'surgeon', 'lookout', 'cook', 'chaplain', "gunner"]
role_desc = [
    "In charge of giving orders to crew as well as crew discipline",
    "Manages all aspects of cargo, equipment and supply stores",
    "Responsible for repairs and enhancements on the ship",
    "In charge of maps and navigation",
    "Responsible for the health and well-being of the crew",
    "Keeps a lookout for land, other ships, sea creatures, etc.",
    "Responsible for providing food to the crew",
    "Provides spiritual guidance to the crew",
    "In charge of battles at sea",
]
dispositions = ['very miserable', 'sombre', 'satisfied', 'happy']
disciplines = ['lawless', 'unruly', 'following orders', 'well disciplined']
healths = ['dying','in very ill health', 'not well', 'healthy']

class CrewMember:
    _serialized_attrs = ['name','role','idx']
    def __init__(self, role, idx):
        self.name = ''
        self.role = role
        self.idx = idx

    def set(self, d):
        util.deserialize_obj(self, d)

    def get(self):
        ret = util.serialize_obj(self)
        return ret
        # at some point we might have skill level and abilities

    def __str__(self):
        return f"{to_proper_case(roles[self.idx])} {self.name}"

    def description(self):
        return role_desc[self.idx]


# General ABS Crew plus the special CrewMembers
class Crew:
    _serialized_attrs = ['_seamen_count','disposition','discipline','_next_payday','_amt_due', '_health']
    def __init__(self):
        # general seamen and their mood, discipline, health
        self._seamen_count = 0
        # a value from 0 to 3 indicating happiness level
        # 0=very miserable, 1=unhappy, 2=neutral, 3=happy
        self.disposition = 2
        # level of discipline
        # 0=lawless, 1=unruly, 2=neutral, 3=obedient
        self.discipline = 3
        # level of health
        # 3 = In good health , 2 = not well, 1=in very ill health, 0 = dying
        # lose 2 points for each day without water, 1 point for each day without food
        self._health = 3
        # next pay day for ABS
        self._next_payday = 0
        self._amt_due = 0

        # specific crew
        for i, c in enumerate(role_attrs):
            setattr(self, c, CrewMember(roles[i], i))


    def get(self):
        ret = util.serialize_obj(self)
        for i, c in enumerate(role_attrs):
            ret[c] = getattr(self, c).get()
        return ret

    def set(self, d: dict):
        util.deserialize_obj(self, d)
        for i, c in enumerate(role_attrs):
            v = d[c]
            getattr(self, c).set(v)

    def decrease_health(self, n=1):
        """
        decrease health by n points
        if we were already at 0, kill off some crew
        """
        if n < 1:
            raise ValueError

        # if we took any hits and we have 0 health, we must kill off some crew
        # we will kill off 20% for now
        if self._health == 0:
            sc = self.seamen_count
            newsc = int(sc * .8)
            self.set_seamen_count(newsc)
            if sc-newsc:
                gs.output(f"{gs.crew.boatswain}: {sc-newsc} able-bodied seamen have died!")
                gs.output(f"{gs.crew.chaplain}: May they rest in peace.")
        else:
            self._health -= n
            if self._health <= 0:
                gs.output(f"{gs.crew.boatswain}: Our crew is in very poor condition!")
                self._health = 0

    def increase_health(self):
        """
        restore a point of health
        """
        if self._health < 3:
            self._health += 1
            if self._health == 3:
                gs.output(f"{gs.crew.boatswain}: Our crew are feeling healthy again.")

    def restore_health(self):
        """
        restore full health
        :return:
        """
        self._health = 3

    @property
    def seamen_count(self):
        return self._seamen_count

    def set_seamen_count(self, count) -> int:
        '''
        Hire or fire seamen. This may debit the amt due based on prorated pay.
        Crew is hired and paid in advance for 30 days of service. If we fire seamen, they
        have already been paid, and we don't recoup that. If we hire new seamen they are
        paid a prorated amount until the next payday.

        :param count:
        :return: prorated amount that needed to be paid
        '''
        old_count = self._seamen_count
        delta = count - old_count
        ret = 0

        if delta > 0:  # hiring

            days_until = max(0, self._next_payday - gs.player.num_days_elapsed)
            prorate = float(days_until) / float(state.ABS_PAY_PERIOD)
            prorate_amt = int((delta * state.ABS_PAY) * prorate)
            if prorate_amt:
                ret = prorate_amt
                self._amt_due += prorate_amt

        self._seamen_count = count
        return ret

    @property
    def next_payday(self):
        return self._next_payday

    # called periodically to check if pay is due and if so debit the amt due and reset to
    # next due date. This returns true if an amount was added
    def update_pay_due(self) -> bool:
        ret = False
        if gs.player.num_days_elapsed >= self._next_payday:
            self._amt_due += (self._seamen_count * state.ABS_PAY)
            if self._seamen_count:
                ret = True
            self._next_payday = gs.player.num_days_elapsed + state.ABS_PAY_PERIOD
        return ret

    def amt_due(self):
        '''
        Used to block activities if crew hasnt been paid
        :return:
        '''
        return self._amt_due

    def pay_crew(self) -> int:
        '''
        Return the amount paid if the crew could be paid in full. if not, no pay is given and 0 is returned.
        This also
        :return:
        '''
        paid = 0
        if self._amt_due:
            if gs.player.doubloons >= self._amt_due:
                paid = self._amt_due
                gs.player.add_remove_doubloons(-self._amt_due)
                self._amt_due = 0

        return paid

    def describe(self):
        if self._seamen_count == 0:
            gs.output("The ship currently has no able-bodied seamen.")
        else:
            gs.output(f"The general crew currently consists of {self._seamen_count} {disciplines[self.discipline]} "
                      f"able-bodied seamen who are currently {healths[self._health]} and {dispositions[self.disposition]}.")

        if self.amt_due():
            gs.output(f"You currently owe {self.amt_due()}D to the crew for their services.")
        else:
            d = self.next_payday - gs.player.num_days_elapsed
            gs.output(f"The next crew pay day is in {d} days.")

        rats, _ = gs.stock.get_rations()
        grog, _ = gs.stock.get_grog_portion()
        gs.output(f"The crew is on {rats} rations and {grog}.")
        gs.output("")
        gs.output("Other positions on the ship:")
        self.describe_named(False)

    def describe_named(self, include_idx):
        for i, r in enumerate(role_attrs):
            role = self.get_by_idx(i)
            n = role.name if role.name else '(unfilled)'
            idx = f"{i + 1} " if include_idx else ""
            gs.output(f"{idx}{n} ({roles[i]}) - {role_desc[i]}")

    def get_by_role(self, role):
        return getattr(self, role)

    def get_by_idx(self, idx):
        return getattr(self, role_attrs[idx])

def pay_description():
    return f"Your ship can support {state.ABS_COUNT_MAX} ABS. It takes a minimum " \
           f"of {state.ABS_COUNT_NONFUNCTIONAL + 1} ABS in order to sail. However anything less than " \
           f"{state.ABS_COUNT_REDUCED + 1} ABS would reduce the functioning of the ship, and less than " \
           f"{state.ABS_COUNT_IMPAIRED + 1} ABS would seriously compromise it. Each ABS will need to be paid up front " \
           f"and then paid every {state.ABS_PAY_PERIOD} days at a rate of {state.ABS_PAY}D. " \
           f"ABS can be hired and fired while at a port. If you hire any additional ABS they will need to be paid a " \
           f"pro-rated amount for the remainder of the pay period. If you fire any ABS they have already been paid and " \
           f"will get to keep their earnings for the remaining days of the pay period."
