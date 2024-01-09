# current player stats
from cargo import CargoCollection
class Player:
    def __init__(self):
        # player's personal info
        self.name: str = ""
        self.birthplace: str = ""

        # players ship
        self.ship: Ship = Ship()

        # number of days sailing the seas
        self.days = 0

        # personal property
        self.doubloons = 10
        #
        self.location = "port"



class CrewMember:
    def __init__(self):
        self.name = ""
        self.role = ""

class Ship:
    def __init__(self):
        self.name = ""
        self.cargo: CargoCollection = CargoCollection()
