# global constants

# each island has a class of activities they do. They may have more than one
# does not participate in any activities
ISLAND_CLASS_NONE = 0
# suitable for growing fruit, etc. rum production
ISLAND_CLASS_TROPICAL = 1
# animal farming
ISLAND_CLASS_FARMING = 2
# crop farming
ISLAND_CLASS_AGRI = 3
# forestry
ISLAND_CLASS_FOREST = 4
# mining (gold, iron)
ISLAND_CLASS_MINING = 5
# manufacturing
ISLAND_CLASS_MFG = 6
# just trading etc. (loans?)
ISLAND_CLASS_COMMERCE = 7
class_descriptions = ["None", "Tropical Fruit", "Meat and Dairy", "Agriculture", "Forestry", "Mining", "Manufacturing",
                      "Commerce"]

# island will be from uninhabited up to advanced.
# this integer also determines production levels
ISLAND_CIV_UNINHABITED = 0
ISLAND_CIV_TRIBAL = 1  # natives
ISLAND_CIV_OUTPOST = 2  # some western civilization, has port with basic trading
ISLAND_CIV_TOWN = 3  # has a port with basics, as well as some repair services
ISLAND_CIV_CITY = 4  # has port all the latest amenities, upgrades etc
civ_descriptions = ["Uninhabited", "Tribal", "Outpost", "Small Town", "Big City"]

# stock indices
STOCK_FOOD_IDX = 0
STOCK_WATER_IDX = 1
STOCK_GROG_IDX = 2
STOCK_MEDICINE_IDX = 3
STOCK_MATERIALS_IDX = 4
STOCK_ORDNANCE_IDX = 5

# 5 units per day per abs = full ration
# 3 units per day is reduced ration
# 2 units per day is meager
STOCK_RATIONS_FULL = 5
STOCK_RATIONS_REDUCED = 3
STOCK_RATIONS_MEAGER = 2

# grog consumption rate
STOCK_GROG_HIGH = 2
STOCK_GROG_LOW = 1
STOCK_GROG_NONE = 0