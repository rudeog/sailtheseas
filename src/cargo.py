class CargoType:
    def __init__(self, name, units, weight_per_unit):
        self.name: str = name
        # what unit of measure to use
        self.units: str = units
        # weight here is in pounds
        self.weight_per_unit = weight_per_unit


cargo_types: list[CargoType] = [
    CargoType("Wheat", "tons", 2000),
    CargoType("Rum", "barrels", 520),
    CargoType("Lumber", "tons", 2000),
    CargoType("Gold", "pounds", 1),
]


class CargoItem:
    def __init__(self, t: CargoType, q: int):
        self.type: CargoType = t
        self.quantity: int = q

    def __str__(self):
        return f"{self.quantity} {self.type.units} of {self.type.name}"


class CargoCollection:
    def __init__(self):
        self.cargo: list[CargoItem] = []
    def __iter__(self):
        return iter(self.cargo)
    def __len__(self):
        return len(self.cargo)

    def add_remove(self, cargo_type: CargoType, qty: int = 0):
        """
        Add or remove cargo from the collection
        :param cargo_type:
        :param qty: if 0, all cargo is removed
        :return:
        """
        for it in self.cargo:
            if it.type == cargo_type:
                if not qty:
                    it.quantity = 0
                else:
                    it.quantity = it.quantity + qty
                if it.quantity <= 0:
                    self.cargo.remove(it)
                return

        self.cargo.append(CargoItem(cargo_type, qty))
