# this will generate descriptive text about each place
import re
import random

from names import NameGenerator, PlaceGenerator
from state import gs
from util import ListSelector, fancy_date
import islands
from player import STARTING_DATE
from datetime import timedelta

# These are the different main outlines for an island
outlines = [
    "The island of [m,name] which was discovered [date] by [l,discoverer], [l,geog] [l,civ] [l,cls]",
    "Discovered in [date,year] by [l,discoverer], [m,name] [l,geog] [l,cls]",
    "[m,name] was discovered in [date,year] and [l,geog] [l,civ] [l,cls]",
    "Visitors to [m,name] will be surprised to find out that it [l,geog] [l,civ] [l,cls]",
]

# these lists can be looked up with sel (be careful of recursion)
nature_adjectives = [ "violent", "noisy", "ancient", "modern", "slow", "fast", "prehistoric","mysterious","silly"]
colors = ["mauve", "purple", "brown", "reddish", "green", "multi-colored", "blue", "light-yellow", "spotted", "polka-dotted", "grey"]
geog = [ # geographic features following island or place name
    "has [l,look_adj] hills in the [l,dir] which are covered with [l,color] [l,plant] in the spring.",
    "was formed as a result of [l,nat_adj] [p,volcanic,seismic] activity.",
    "is known for [l,look_adj] [p,stony,sandy,dry] beaches on the [l,dir] end.",
    "has a migratory [l,color] [l,animal] population that are [p,notable,renowned] for their [l,nat_adj] [p,ways,mating rituals,traits].",
    "is notorious for its invasive [l,color] [l,animal] population.",
    "is famous for its [l,color] cliffs in the [l,dir].",
]
discoverer = [
    "[m,emperor]'s [p,great,great-great] [p,ancestors,uncle,aunt,grandfather,grandmother]",
    "the reformed pirate captain [person,m,w]",
    "the widow [person,f,w] on her first solo voyage",
    "the [p,notorious,lengthy,tedious,well-documented] [person,m,w] and [person,m,w] expedition",
]
animals=["Guinea pig", "[p,long tailed,tailless,black-faced] monkey","boar", "lion","[word] antelope", "armadillo", "squirrel", "spider", "[p,flightless,wingless,tropical] bird",]
directions=["North","East","South","West"]
look_adj=["pretty", "ugly", "bland", "somewhat boring", "stunning", "interesting", "notable"]
plants = ["flowers", "berry bushes", "ferns","orchids","hemp"]
sports = ["tennis","cricket","bowling","ball","chess"]
fruit = ["mango","banana","avocado","pineapple","breadfruit"]
livestock = ["goats","sheep","cows","bulls","horses","pigs","poultry"]

prox = [
    "which is surrounded by [l,color] hills,",
    "which lies near a [l,look_adj] river,",
    "which is not notable at all,",
    "which is considered [l,look_adj],"
    ]
plague = [
    "poisonous [l,plant]",
    "famine",
    "deadly spores",
    "fatal laughing sickness",
    "[p,bulbous,bleeding,excressive] tumors",
    "[p,bubonic,black] plague",
    "mosquito born illness",
    "noxious gas leaks",
    ]
# any of the lists for sel,gen must be listed here
lookups = {
    "prox": prox,
    "animal": animals,
    "dir": directions,
    "look_adj": look_adj,
    "nat_adj" : nature_adjectives,
    "color" : colors,
    "geog": geog,
    "plant": plants,
    "sport": sports,
    "fruit": fruit,
    "livestock": livestock,
    "plague": plague,
    "discoverer": discoverer,
}

# these are selected according to island with sel,civ
civ_uninhabited = [
    "An event involving [l,plague] in [date,year] wiped out the only settlement.",
    "Nobody has ever attempted to live on [m,name].",
    "It is unknown why nobody lives here.",
    "Disease spread by [l,color] mosquitos wiped out the residents in [date,year].",
    "Its rocky features make it unsuitable for habitation.",
]
civ_tribal = [
    "The native population are noted for growing [l,look_adj] [l,plant] which they call [word].",
    "The locals dress exclusively in [l,color] [l,animal] leather.",
    "The native people fish for [l,color] [word] fish in the [p,warmer,cool,deep,shallow,crystal clear] waters to the [l,dir].",
    "The tribes of [m,name] rely on the [p,gum,leaf,root,bark,pods] of the [word] tree for medicinal purposes.",
]

civ_outpost = [
    "Original settlers in the [l,dir] established a town which became [m,portname].",
    "Ancestors of the current port master [m,portmaster] established the only town.",
    "The outpost, [l,prox] is [p,very quiet,subdued,empty] most times, except for occasional [p,parades,marches,pony races] sponsored by [m,ruler]."
]

civ_smalltown = [
    "Settlers wiped out the [l,nat_adj] [l,animal] population, and established a settlement which became [m,portname].",
    "There is an ongoing [p,civil war,dispute,rivalry,clash] between [p,supporters,followers,family members] of [m,ruler] and his [p,detractors,enemies,rivals] in the [l,dir].",
]

civ_bigcity = [
    "[m,ruler] has established a yearly [l,sport] tournament which is highly regarded throughout [m,world].",
    "The center of [m,portname] [l,prox] is very [p,congested,raucous,hectic,bustling] on most days.",
    "This is a haven for [l,sport] fanatics. It also has a [l,look_adj] night-life.",
    "City life has put a strain on the natural resources of the island, and has driven out most of the [l,color] [l,animal] population.",
    "The main city was rebuilt in [date,year] after a [p,fire,flood,hurricane,landslide] destroyed the original settlement.",
]

class_trop = [
    "The island is known for its [l,fruit] groves.",
    "The plantation in the [l,dir] [l,prox] is [p,very,not at all,incredibly] productive.",
]
class_meatdairy = [
    "Local farmers are [p,proud,boatsful,ashamed] of their [l,color] [l,livestock].",
    "Farming of [l,livestock] continues despite [l,plague].",
]
# these are selected with sel,cls
class_ag = [
    "Fields of [p,oats,wheat,barley,corn] cover the [l,dir] side of the island.",
    "The island is [p,famous,renowned,noted] for their [p,hybrid,plump,bitter,sour,sweet,dried,fermented] [l,color] [p,soybeans,beans,peas].",
    "The island is [p,famous,well known] for its [p,annual,weekly,winter] [word] [p,bean,pea,corn,wheat] festival.",
    "Local farmers have [p,an annual,a monthly,a summer] [p,festival,fair,competition] in which they compete to see who can grow the [p,largest,roundest,smallest,juiciest] [word] [p,squash,fruit,potato].",
]

class_forest = [
    "It is known for having [l,nat_adj] [l,animal]s which roam the forest in the [l,dir].",
    "The forests in the [l,dir] [l,prox] provide most of the lumber on the island.",
    "The main forest [l,prox] provides a steady stream of [word] wood planks.",
]

class_mining = [
    "The main mine [l,prox] is [p,somewhat,very,extremely] deep.",
    "[p,Much,The whole,Half] of the island is covered in [p,shallow,twisty,deep,treacherous] mine shafts.",
]

class_commerce = [
    "Banks and other houses of commerce are to be found [p,on both sides of the,nearby the,down by the] [place,e] [p,river,canal,bay].",
    "Established houses of business can be found in the [place,w] district.",
    "The island's ruler [m,ruler] [p,owns,oversees,has taken over,is very proud of] the largest bank which is in the [place,w] [p,district,area].",
    "The historic city square contains a [l,look_adj] [l,color] statue of the [l,nat_adj] [l,animal] which is native to the island.",
    "The [p,notorious,generous,well-heeled] business partners [person,m,w] & [person,m,w] own all the banking houses.",
    ]

lookups['mfg_big'] = [ "recliners","beds","cannons","wagons", "farm equipment"]
lookups['mfg_small'] = ["wigs","chamber pots", "furbelows", "fluffy things", "hand-puppets", "corsets"]
lookups['mfg_mats'] = ['bamboo','rawhide','iron','whale-bone','clay','bone','poorly constructed', 'well-made']
class_mfg = [
    "This place is [p,well known,notable,the butt of jokes] for their production "
        "of [l,mfg_mats] [l,mfg_big].",
    "A large factory near [place,e] [p,river,mountain,valley] in the [l,dir] is owned by [person,m,e]. After failing in the production of [l,mfg_big], he now mass-produces [l,mfg_small].",
    "Their production of [l,color] [l,mfg_mats] [l,mfg_small] near [m,portname] is [p,well known,talked about] throughout [m,world].",
    "The family of [m,ruler] controls much of the manufacturing of [l,mfg_mats] [l,mfg_small] in the [l,dir]. Recently the production of [l,mfg_mats] [l,mfg_big] has started.",
]

civ_lists = [civ_uninhabited, civ_tribal, civ_outpost, civ_smalltown, civ_bigcity]
class_lists = [[], class_trop, class_meatdairy, class_ag, class_forest, class_mining, class_mfg, class_commerce]


class IslandModel:
    def __init__(self, island=None):
        self.ruler = ""
        self.name = ""
        self.port_master = ""
        self.port_name = ""
        self.civ_type = 0
        self.primary_class = 0
        self.secondary_class = 0
        if island:
            self.ruler = island.ruler
            self.name = island.name
            if island.port:
                self.port_name = island.port.name
                self.port_master = island.port.port_master
            else:
                self.port_name = ""
                self.port_master = ""
            self.civ_type = island.civ_type
            self.primary_class = island.primary_class
            self.secondary_class = island.secondary_class


class _Model:
    '''
    internal model for generating
    '''

    def __init__(self, island_mod: IslandModel, rng):
        self.rng = rng
        self.island = island_mod
        self.civ_select = None
        self.class_select = None
        self.gen_select = None
        self.lu_selectors = None
        self.ng=None
        self.pg=None


# select from specified list and return a random item from that list with replacements made
def ru_select(model: _Model, args: list):
    if len(args) != 1:
        raise ValueError(f"must have 1 arg, got {len(args)} with {args[0] if len(args) else 'nothing'}")
    if args[0] == 'civ':
        sel = model.civ_select
    elif args[0] == 'cls':
        sel = model.class_select
    else:
        if args[0] not in model.lu_selectors:
            return f"[l: {args[0]} not found]"
        sel = model.lu_selectors[args[0]]
    return _replace_tokens(sel.select(), model)

def ru_pick_one(m: _Model, args: list):
    if args:
        ri = m.rng.randint(0,len(args)-1)
        return args[ri]
    return ""

# return some string from model or global
def ru_model_item(m: _Model, args: list):
    w = args[0]
    model=m.island
    if w == 'name':
        ret = model.name
    elif w == 'ruler':
        ret= model.ruler
    elif w == 'portmaster':
        ret = model.port_master
    elif w == 'portname':
        ret = model.port_name
    elif w == 'emperor':
        ret = gs.emperor
    elif w == 'world':
        ret = gs.world_name
    else:
        ret = f"[unknown model item {w}"
    return str(ret)


def ru_rand_hist_year(model: _Model, args: list):
    # some date between 5 and 1000 years ago
    thedate = STARTING_DATE - timedelta(days=(365 * model.rng.randint(5, 500)))
    if args and args[0] == 'year':
        return f"{thedate.year}"
    return fancy_date(thedate)

def ru_place(model: _Model, args: list):
    a=""

    if len(args):
        a=args[0]


    return str(model.pg.name(a))

def ru_word(model: _Model, args: list):
    n=model.ng.name('o','e')
    return n.first

def ru_person(model: _Model, args: list):
    a=""
    b=""
    if len(args):
        a=args[0]
        if len(args) > 1:
            b  = args[1]

    n = model.ng.name(a,b)
    return n.first + " " + n.last

# each rule has a function. it can optionally have args in which case its a list
# where the first element is the function and subsequent ones are the args.
# these args are passed as the 2..n args to the function
rules = {
    # select randomly from a list arg can be gen (generic) civ (civ specific), cls (class specific)
    "l": ru_select,
    # extract text from the model
    "m": ru_model_item,
    # some historical date or year if arg is 'year' then its just the year
    "date": ru_rand_hist_year,
    # pick one of the following at random
    "p": ru_pick_one,
    # person: args are gender (m=male,f=female,o=other) class (w=western,e=exotic)
    "person": ru_person,
    # place: args are w=western,e=exotic,f=fancy
    "place": ru_place,
    "word": ru_word,
}


def _replace_tokens(input_string, model):
    '''
    given rules and an input string, apply replacements in the string
    where it has tokens in [] which are comma separated. The first element
    is the function name which is looked up in rules. Subsequent elements
    are args that are passed to that function
    :param model:
    :param input_string:
    :param rules:
    :return:
    '''

    def replace_token(match):
        r = match.group(1)
        s = r.split(",")
        fname = s[0]
        if fname not in rules:
            return match.group(0)  # not found
        fn = rules[fname]
        if isinstance(fn, list):
            pre_args = fn[1:]
            fn = fn[0]
            args = pre_args + s[1:]
        else:
            args = s[1:]
        subst = fn(model, args)
        return subst

    pattern = r'\[([^\[\]]+)\]'
    c = re.compile(pattern)
    return c.sub(replace_token, input_string)


class DescGen:
    '''
    Description generator for islands
    '''

    def __init__(self, seed, ng, pg):
        self.rng = random.Random(seed)
        self.ng=ng
        self.pg=pg
        self.main_selector = ListSelector(self.rng, outlines)
        self.class_selectors = []
        for l in class_lists:
            self.class_selectors.append(ListSelector(self.rng, l))
        self.civ_selectors = []
        for l in civ_lists:
            self.civ_selectors.append(ListSelector(self.rng, l))
        self.lu_selectors = {}
        for k,v in lookups.items():
            self.lu_selectors[k]=ListSelector(self.rng,v)

    def generate(self, island: IslandModel):
        '''
        Generate description for given island
        :param island:
        :return:
        '''
        model = _Model(island, self.rng)
        model.civ_select = self.civ_selectors[island.civ_type]
        model.class_select = self.class_selectors[island.primary_class]
        model.lu_selectors = self.lu_selectors
        model.ng=self.ng
        model.pg=self.pg

        # select a top level outline generic for any island type
        top = self.main_selector.select()
        res = _replace_tokens(top, model)
        return res


if __name__ == "__main__":
    dg = DescGen(6654546, NameGenerator(109), PlaceGenerator(91))
    isl = IslandModel()
    isl.name = "Franklin"
    isl.primary_class = 3
    isl.secondary_class = 0
    isl.civ_type = 1
    isl.ruler = "John Johns"
    isl.port_name = "OCharlesPort"
    isl.port_master = "Portmaster"
    gs.world_name = "Gnaphisthasia"
    gs.emperor = "Trought"

    gs.output(dg.generate(isl))
    gs.output(dg.generate(isl))
    gs.output(dg.generate(isl))
    gs.output(dg.generate(isl))
    gs.output(dg.generate(isl))
    gs.output(dg.generate(isl))
    gs.output(dg.generate(isl))
