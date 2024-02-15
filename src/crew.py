from state import gs
from util import to_proper_case
NUM_ROLES = 8
roles = ['boatswain', 'first mate', 'carpenter', 'navigator', 'surgeon', 'lookout', 'cook', 'chaplain']
role_attrs = ['boatswain', 'firstmate', 'carpenter', 'navigator', 'surgeon', 'lookout', 'cook', 'chaplain']
role_desc = [
    "In charge of equipment and supply stores as well as crew discipline",
    "Manages all aspects of cargo",
    "Responsible for repairs and enhancements on the ship",
    "In charge of maps and navigation",
    "Responsible for the health and well-being of the crew",
    "Keeps a lookout for land, other ships, sea creatures, etc.",
    "Responsible for providing food to the crew",
    "Provides spiritual guidance to the crew",
]
dispositions = ['very miserable', 'sombre', 'satisfied', 'happy']
disciplines = ['lawless', 'unruly', 'following orders', 'well disciplined']
class CrewMember:
    def __init__(self, role, idx):
        self.name = ''
        self.role = role
        self.idx = idx
        # at some point we might have skill level and abilities

    def __str__(self):
        return f"{to_proper_case(roles[self.idx])} {self.name}"

    def description(self):
        return role_desc[self.idx]

    def set(self, d) -> bool:
        try:
            self.name = d['n']
            self.role = d['r']
            self.idx = d['i']
        except KeyError:
            return False
        return True
    def get(self):
        ret={}
        ret['n']=self.name
        ret['r']=self.role
        ret['i']=self.idx
        return ret

class Crew:
    def __init__(self):
        # general seamen and their mood, discipline, health
        self.seamen_count = 0
        self.health = 100
        # a value from 0 to 3 indicating happiness level
        # 0=very miserable, 1=unhappy, 2=neutral, 3=happy
        self.disposition = 2
        # level of discipline
        # 0=lawless, 1=unruly, 2=neutral, 3=obedient
        self.discipline = 3

        # specific crew
        for i,c in enumerate(role_attrs):
            setattr(self, c, CrewMember(roles[i], i))

    def describe(self):
        if self.seamen_count==0:
            gs.output("The ship currently has no able-bodied seamen.")
        else:
            gs.output(f"The general crew currently consists of {self.seamen_count} {disciplines[self.discipline]} "
                f"able-bodied seamen who have "
                f"{self.health}% health. They are currently {dispositions[self.disposition]}.")

        gs.output("Other positions on the ship:")
        self.describe_named(False)

    def describe_named(self, include_idx):
        for i,r in enumerate(role_attrs):
            role = self.get_by_idx(i)
            n=role.name if role.name else '(unfilled)'
            idx = f"{i+1} " if include_idx else ""
            gs.output(f"{idx}{n} ({roles[i]}) - {role_desc[i]}")

    def get_by_role(self, role):
        return getattr(self, role)
    def get_by_idx(self, idx):
        return getattr(self, role_attrs[idx])


    def get(self):
        ret = {}
        for i,c in enumerate(role_attrs):
            ret[c]=getattr(self, c).get()

        ret['sc'] = self.seamen_count
        ret['h']=self.health
        ret['disp']=self.disposition
        ret['disc']=self.discipline
        return ret


    def set(self, d: dict) -> bool:
        try:
            self.seamen_count=d['sc']
            self.health=d['h']
            self.disposition=d['disp']
            self.discipline=d['disc']
            for i,c in enumerate(role_attrs):
                v = d[c]
                if not getattr(self, c).set(v):
                    return False
            return True
        except KeyError:
            return False

