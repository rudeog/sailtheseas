from state import gs

class Pirate:
    def __init__(self, name, ship_name):
        # set to true when completed
        self.completed = False
        # if we evade or they evade, they will still have damage
        self.health = 100
        # pirate's name
        self.name = name
        self.ship_name = ship_name
    def get(self):
        # we only need to keep track of their completed state and health because they are generated
        # with world data
        return {"com": self.completed, "h": self.health}

    def set(self, d: dict):
        self.completed = d["com"]
        self.health = d["h"]

