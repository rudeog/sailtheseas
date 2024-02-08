class CargoType:
    def __init__(self, name, units, weight_per_unit, price_coeff, prod_coeff, code):
        self.name: str = name
        # what unit of measure to use
        self.units: str = units
        # weight here is in pounds
        self.weight_per_unit = weight_per_unit
        # price coefficient is per unit. this determines the cost to some degree
        self.price_coefficient = price_coeff
        self.code = code
        # this determines how much can be produced
        self.prod_coefficient = prod_coeff


# All the possible types of cargo that can be carried at sea
cargo_types: list[CargoType] = [
    CargoType("Grain", "tons", 2000, 25, 1000, "gr"),
    CargoType("Preserved foods", "barrels", 500, 110, 500, "pf"),
    CargoType("Livestock", "head", 1000, 100, 550, "li"),
    CargoType("Iron", "tons", 2000, 150, 700, "ir"),
    CargoType("Manufactured goods", "tons", 2000, 150, 300, "mg"),
    CargoType("Rum", "barrels", 520, 200, 200, "ru"),
    CargoType("Lumber", "tons", 2000, 75, 800, "lu"),
    CargoType("Gold", "pounds", 1, 2000, 10, "go"),
]

cargo_type_lookup = {obj.code: index for index, obj in enumerate(cargo_types)}

# cargo type indices into above list
CARGO_GRAIN = 0
CARGO_FOOD = 1
CARGO_LIVESTOCK = 2
CARGO_IRON = 3
CARGO_MFG = 4
CARGO_RUM = 5
CARGO_LUMBER = 6
CARGO_GOLD = 7


class CargoItem:
    def __init__(self, ti: int, q: int):
        self.type_idx = ti
        self.type: CargoType = cargo_types[ti]
        self.quantity: int = q
        # if selling this ends up being the price. if buying this ends up
        # being the amount paid per unit. if on ship, it is how much was paid for it(?)
        self.price_per = 0

    def __str__(self):
        return f"{self.quantity} {self.type.units} of {self.type.name}"


class CargoCollection:
    def __init__(self):
        self.cargo: list[CargoItem] = []

    def __iter__(self):
        return iter(self.cargo)

    def __len__(self):
        return len(self.cargo)

    def __getitem__(self, idx):
        '''
        Return a cargo item with the given type index, otherwise none if its not here
        :param idx: must be a valid type idx
        :return:
        '''
        if not isinstance(idx, int):
            raise TypeError("idx must be a cargo type index")
        return next((p for p in self.cargo if p.type_idx == idx), None)

    def total_weight(self):
        # total weight in pounds for the collection
        w=0
        for it in self.cargo:
            w = w + (it.quantity * it.type.weight_per_unit)
        return w

    def add_remove(self, cargo_type_idx: int, qty):
        """
        Add or remove cargo from the collection. If it exists in the collection,
        the qty only is updated
        :param cargo_type_idx:
        :param cargo_type:
        :param qty: if 0 nothing happens
        :return: the updated qty
        """
        it = self[cargo_type_idx]
        if it:  # exist   already, adjust qty
            it.quantity = it.quantity + qty
            ret = max(it.quantity, 0)
            if it.quantity <= 0:
                self.cargo.remove(it)
            return ret

        if qty > 0:
            self.cargo.append(CargoItem(cargo_type_idx, qty))

        return qty

    def set_price(self, cargo_type_idx: int, price_per: int = 0):
        """
        Set price of cargo if present
        :return:
        """
        item = self[cargo_type_idx]
        if item:
            item.price_per = price_per
