# generate names based on an integer which is a random integer
# - people short names
# - people full names
# - place names
# - creature names
# - ship names
# - silly phrases
import random

from util import to_proper_case, ListSelector

male_first_names = ["Sid", "Chalky", "Wallace", "Reggie", "Frampton", "Curtis", "Alex", "Robert", "Bellamy", "Scrag",
                    "Bodkin", "Roy", "Knolly", "Quackso", "Brutus", "Fingers", "Prettyface", "Sticky", "Ron", "Will",
                    "Billiam", "Royster", "Coolin", "John", "James", "Henry", "Paul", "Anders", "Bob", "Christophe",
                    "David", "Conrad", "Roderick", "Oliver", "Leopold",
                    "Eustace", "Fred", "Graeme", "Harolde", "Ian", "Ignatz", "Roach", "Louis", "Manfred",
                    "Norbert", "Oswald", "Patrick", "Quayde", "Rolfe", "Steven", "Tyler", "Umberto", "Vinny",
                    "Wombert", "Xerxes", "Yerkin", "Zool", "Skeeter"]
female_first_names = ["Alice", "Bertha", "Cardigan", "Euphemia", "Fanny", "Geranium", "Herta", "Imogen", "Jessie",
                      "Kelli", "Laurie", "Moonie", "Noleen", "Ophellia", "Penelope", "Qualicia", "Rosy", "Susie",
                      "Tallia", "Unice", "Veroniqua", "Wendeigh", "Xendia", "Yolanda", "Zenia", "Chacona","Fiona",
                      "Cornay", "Pink", "Helen", "Jennifer", "Prudence"]
other_first_names = ["Oaste", "Pat", "Fontarde", "Weem", "Pillial", "Snit"]
# avoid adding common suffixes to these
western_last_names = ["Smith", "Jones", "Trought", "Roth", "Hamm", "Winter", "Robin", "Wiener",
                      "Toe", "Foote", "Summer", "Sawyer", "Hunter", "Chandler", "Tanner", "Baker", "Butcher",
                      "Arcy", "Shirmers", "Edwards", "Axe", "Skenus", "Slurm", "Ball"]

last_name_prefixes = ["Mc","O'","De","St. ", "Le", "D'", "Fitz", "Van"]
last_name_suffixes = ["kin","son","ski","sky","ian","o", "i", "christ", "aloe", "patrick", "is", "fifi","sey","sby"]

# exotic name chunks
names_compound = ["wenn", "gu", "urt", "xa", "sen", "kla", "puj", "jeq", "sto",
                  "ok", "iz", "fee", "owl", "bop", "thek", "uze", "afe", "aat", "qu","spra","nce"]


western_places = ["Giles", "York", "Wales", "London", "Amsterdam", "Paris", "East", "North", "South", "West",
                  "Shayne", "Potato", "Smith", "Furrow", "Wheat", "Cabbage", "Flower", "Cows", "Shartle",
                  "Sisk", "Quayle", "Kitty", "Crescent", "Whiskey", "Bourbon", "Francis", "Paul", "Peter", "Bath",
                  "Cheeks", "Greentree", "Cloud", "Jefferson", "Jacksasm", "Chicken", "Duck", "Bird", "Reginald",
                  "Albert", "William", "Wags", "Chups", "Mumps"]
place_suffixes = ["gate", "ton", "town", " Forest", " Farms", " Patch", " on Avon", " on James", "thorpe", "thwaite",
                  " in the Fields", "wich", " row", "burg", "borough", " Hollow", " Fort", "ville", "port", " Colony",
                  "'s Knee", "'s Armpit", "'s Elbow"]

place_prefixes = ["Holy ", "New ", "Olde ", "Righteous ", "Left ", "Cheap ",
                  "Mc", "Van", "The ", "Green ", "White ", "St. ", "Upper ", "Lower "]
places_compound = ["bal","bu","chin","cha","kap","kwa","iwa","wep"]

class Name:
    def __init__(self):
        self.first = ""
        self.last = ""
        self.title = ""
        self.gender = ""

    def __str__(self):
        # full name
        return (self.title + " " if self.title else "") + \
            self.first + (" " + self.last if self.last else "")

class Place:
    def __init__(self):
        self.name = ""
        self.description = ""
    def __str__(self):
        return self.name

class PlaceGenerator:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self._western_places = ListSelector(self.rng, western_places)
        self._place_prefixes = ListSelector(self.rng, place_prefixes)
        self._place_suffixes = ListSelector(self.rng, place_suffixes)
        self._places_compound = ListSelector(self.rng, places_compound)

    def name(self, desired_class=""):
        """
        Generate a place. returns place
        :param desired_class: w=western, e=exotic, empty string = leave to chance
        :return: a Place string
        """
        r = Place()

        if desired_class not in ("w", "e"):
            cl = self.rng.choice(["w", "e"])
        else:
            cl = desired_class

        if cl == "e":  # exotic - build using chunks
            r.name = to_proper_case(self._compound())
            have_prefix = self.rng.choices([True,False],[1,3],k=1)[0]
            if have_prefix:
                r.name = self._place_prefixes.select() + r.name
            if not have_prefix:
                if self.rng.choices([True,False],[1,3],k=1)[0]:
                    r.name = r.name + self._place_suffixes.select()
        else:  # western name
            src = self._western_places
            r.name  = src.select()
            # prefix on name? (less likely, but could happen)
            have_prefix = self.rng.choice([True,False])
            if have_prefix:
                r.name = self._place_prefixes.select() + r.name
            # suffix on name?
            if not have_prefix or self.rng.choice([True,False]):
                r.name = r.name + self._place_suffixes.select()
        return r
    def _compound(self):
        """
        Make a compound word from a list of words. repeats are ok
        :param l: list to use
        :return:
        """
        # do we want 1, 2 or 3 sections. mostly we want 2
        h = self.rng.choices([1, 2, 3,4], [1, 2,2, 1], k=1)
        r = []
        for i in range(0, h[0]):
            r.append(self._places_compound.select())
        return "".join(r)


class NameGenerator:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self._male_first_names = ListSelector(self.rng, male_first_names)
        self._female_first_names = ListSelector(self.rng, female_first_names)
        self._other_first_names = ListSelector(self.rng, other_first_names)
        self._western_last_names = ListSelector(self.rng, western_last_names)
        self._last_name_prefixes = ListSelector(self.rng, last_name_prefixes)
        self._last_name_suffixes = ListSelector(self.rng, last_name_suffixes)
        self._names_compound = ListSelector(self.rng, names_compound)

    def name(self, desired_gender="", desired_class=""):
        """
        Generate a persons name. returns
        :param desired_gender: m,f,o or empty string to leave it to chance
        :param desired_class: w=western, e=exotic, empty string = leave to chance
        :return: a Name object
        """
        r = Name()

        if desired_gender not in ("o", "m", "f"):
            r.gender = self.rng.choice(["o", "m", "f"])
        else:
            r.gender = desired_gender

        if r.gender == "m":
            r.title = self.rng.choices(["Mr.","Master","Dr.", "Rev.", "Capt."],[5,1,1,1,1],k=1)[0]
        elif r.gender == "f":
            r.title = self.rng.choices(["Mrs.","Miss","Widow","Lady","Auntie"],[9,3,1,1,1],k=1)[0]
        if desired_class not in ("w", "e"):
            cl = self.rng.choice(["w", "e"])
        else:
            cl = desired_class

        if cl == "e":  # exotic - build using chunks
            r.first = to_proper_case(self._compound())
            r.last = to_proper_case(self._compound())

        else:  # western name
            src = self._male_first_names if r.gender == "m" \
                else self._female_first_names if r.gender == "f" \
                else self._other_first_names
            r.first = src.select()
            r.last = self._western_last_names.select()
            # prefix on first name? (less likely, but could happen)
            if self.rng.choices([True,False], [1,8])[0]:
                r.first = self._last_name_prefixes.select() + r.first
            # prefix on last name?
            if self.rng.choices([True,False], [1,4])[0]:
                r.last = self._last_name_prefixes.select() + r.last
            # suffix on last name?
            if self.rng.choices([True,False], [1,4])[0]:
                r.last = r.last + self._last_name_suffixes.select()


        return r

    def _compound(self):
        """
        Make a compound word from a list of words. repeats are ok
        :param l: list to use
        :return:
        """
        # do we want 1, 2 or 3 sections. mostly we want 2
        h = self.rng.choices([1, 2, 3], [1, 3, 1], k=1)
        r = []
        for i in range(0, h[0]):
            r.append(self._names_compound.select())
        return "".join(r)


if __name__ == "__main__":
    i = 0
    ng=NameGenerator(12)
    for x in range(0, 100):
        print(f"{i} {ng.name(desired_gender='f', desired_class='w')}")
        i = i + 1
    pg = PlaceGenerator(3)
    i=0
    print("========================")
    for x in range (0,100):
        print(f"{i} {pg.name(desired_class='e')}")
        i=i+1
