# generate names based on an integer which is a random integer
# - people short names
# - people full names
# - place names
# - creature names
# - ship names
# - silly phrases
import random

from util import to_proper_case

male_first_names = ["Sid", "Chalky", "Wallace", "Reggie", "Frampton", "Curtis", "Alex", "Robert", "Bellamy", "Scrag",
                    "Bodkin", "Roy", "Knolly", "Quackso", "Brutus", "Fingers", "Prettyface", "Sticky", "Ron", "Will",
                    "Billiam", "Royster", "Coolin", "John", "James", "Henry", "Paul", "Anders", "Bob", "Christophe",
                    "David", "Roderick", "Oliver",
                    "Eustace", "Fred", "Graeme", "Harolde", "Ian", "Ignatz", "Kakkelak", "Louis", "Manfred",
                    "Norbert", "Oswald", "Patrick", "Quayde", "Rolfe", "Steven", "Tyler", "Umberto", "Vinny",
                    "Wombert", "Xerxes", "Yerkin", "Zool"]
female_first_names = ["Alice", "Bertha", "Cardigan", "Euphemia", "Fanny", "Geranium", "Herta", "Imogen", "Jessie",
                      "Kelli", "Laurie", "Moonie", "Noleen", "Ophellia", "Penelope", "Qualicia", "Rosy", "Susie",
                      "Tallia", "Unice", "Veroniqua", "Wendeigh", "Xendia", "Yolanda", "Zenia", "Chacona","Fiona",
                      "Cornay", "Pink", "Helen"]
other_first_names = ["Oaste", "Pat", "Fontarde", "Weem", "Pillial", "Snit"]
# avoid adding common suffixes to these
western_last_names = ["Smith", "Jones", "Trought", "Roth", "Hamm", "Winter", "Robin", "Wiener",
                      "Toe", "Foote", "Summer", "Sawyer", "Hunter", "Chandler", "Tanner", "Baker", "Butcher",
                      "Arcy", "Shirmers", "Edwards", "Axe"]

last_name_prefixes = ["Mc","O'","De","St. ", "Le", "La"]
last_name_suffixes = ["kin","son","ski","sky","ian","o", "i", "christ", "alo", "patrick", "is"]

# exotic name chunks
names_compound = ["wen", "gu", "urt", "kil", "sen", "kla", "pup", "jek", "sto",
                  "ok", "ziz", "fee", "owl", "bop", "thek", "uze"]



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


class ListSelector:
    """
    Given a list will randomly select an item from the list without
    reusing items until all items are used then it should reshuffle
    the list
    """

    def __init__(self, rng, list):
        self.rng = rng
        self.list = list
        self.index = len(list)

    def select(self):
        # If all words have been used, shuffle the list and reset the index
        if self.index == len(self.list):
            self.rng.shuffle(self.list)
            self.index = 0

        # Select the next word in the shuffled list
        selected_word = self.list[self.index]
        self.index += 1
        return selected_word


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
            r.title = self.rng.choices(["Mrs.","Miss","Dr.","Lady"],[8,3,1,1],k=1)[0]
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
        print(f"{i} {ng.name(desired_gender='f', desired_class='e')}")
        i = i + 1
