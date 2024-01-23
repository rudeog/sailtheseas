class CargoType:
    def __init__(self, name, units, weight_per_unit, price_coeff, code):
        self.name: str = name
        # what unit of measure to use
        self.units: str = units
        # weight here is in pounds
        self.weight_per_unit = weight_per_unit
        # price coefficient is per unit
        self.price_coefficient = price_coeff
        self.code = code

# "The largest merchant ships were the East Indiamen, in three broad classes, of 1200 tons, 800 tons, or 500 tons."

# All the possible types of cargo that can be carried at sea
cargo_types: list[CargoType] = [
    CargoType("Grain", "tons", 2000, 25, "gr"),
    CargoType("Preserved foods", "barrels", 500, 100, "pf"),
    CargoType("Livestock", "head", 1000, 100, "li"),
    CargoType("Iron", "tons", 2000, 10, "ir"),
    CargoType("Manufactured goods", "tons", 2000, 150, "mg"),
    CargoType("Rum", "barrels", 520, 200, "ru"),
    CargoType("Lumber", "tons", 2000, 5, "lu"),
    CargoType("Gold", "pounds", 1, 2000, "go"),
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

    def total_weight(self):
        # total weight in pounds for the collection
        w=0
        for it in self.cargo:
            w = w + (it.quantity * it.type.weight_per_unit)
        return w

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
