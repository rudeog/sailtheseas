import json
from pathlib import Path
from state import gs
import os

from util import save_rng_state_to_string, load_rng_state_from_string

SAVE_FILE_NAME = "savefile"
SAVE_FILE_PATH = ".sailtheseas"


def _save_file_name():
    home_dir = Path.home()
    return home_dir / SAVE_FILE_PATH / SAVE_FILE_NAME


def save_file_exists():
    p = Path(_save_file_name())
    return p.exists()


def _save(data_to_write):
    fp = _save_file_name()
    directory = os.path.dirname(fp)
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        with open(fp, "w") as file:
            file.write(data_to_write)
            return ""
    except IOError as e:
        return f"Error writing to '{fp}': {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# TODO add get and set to island which should also pull trader stuff then we can
#  just call get and set on island for trading and visited
def _save_trading_data() -> dict:
    ret = {}
    for pl in gs.map.places:
        if pl.island and pl.island.port and pl.island.port.trader:
            t = pl.island.port.trader
            ret[pl.index] = t.get()
    return ret


def _save_visited_data() -> list:
    ret = []
    for loc in gs.map.all_locations():
        if loc.visited:
            vd = {"l": loc.location}
            if loc.island:
                vd['e'] = loc.island.explored
                vd['vc'] = loc.island.visit_count
            ret.append(vd)
    return ret


def _load():
    """
    return a pair of strings, the first is an error (empty if none),
    the second is the data
    :return:
    """
    fp = _save_file_name()
    if not save_file_exists():
        return "No save file found", ""
    try:
        with open(fp, "r") as file:
            content = file.read()
    except IOError as e:
        return f"Error reading from '{fp}': {e}", ""
    except Exception as e:
        return f"An unexpected error occurred: {e}", ""
    return "", content


def save_game():
    data = {"player": gs.player.get(),
            "ship": gs.ship.get(),
            "stock": gs.stock.get(),
            "crew": gs.crew.get(),
            "seed": gs.seed,
            "rng": save_rng_state_to_string(gs.rng_play),
            "trade": _save_trading_data(),
            "visited": _save_visited_data(),
            "wind": gs.wind.get(),
            "hint": gs.hints.get(),
            "quests": [q.get() for q in gs.quests]
            }

    json_string = json.dumps(data)
    err = _save(json_string)

    return err


def load_game():
    # load the game, set initial data, return loaded object
    err, json_string = _load()
    if err:
        return None, err
    data = json.loads(json_string)
    try:
        gs.seed = data["seed"]
        gs.player.set(data['player'])
        gs.ship.set(data['ship'])
        gs.stock.set(data['stock'])
        gs.crew.set(data['crew'])
        gs.wind.set(data['wind'])
        gs.hints.set(data['hint'])


    except KeyError as e:
        return None, f"Save file may be from an earlier version: {e}"
    return data, ""


def load_trading_and_visited_data(loaded: dict):
    try:
        # this can only be loaded once the rng_play is initialized in base_setup
        load_rng_state_from_string(gs.rng_play, loaded["rng"])

        trade_info = loaded["trade"]
        for k, v in trade_info.items():
            loc = gs.map.get_place_by_index(int(k))
            if loc and loc.island and loc.island.port and loc.island.port.trader:
                t = loc.island.port.trader
                t.set(v)
            else:
                gs.output(f"load warning: failed to find trading post at island {k}")

        # visited and explored data
        visited_info = loaded['visited']
        for vis in visited_info:
            loc = gs.map.get_location(vis['l'])
            loc.visited = True
            if loc.island:
                loc.island.explored = vis['e']
                loc.island.visit_count = vis['vc']

        # quest stuff
        for i, v in enumerate(loaded["quests"]):
            gs.quests[i].set(v)

        return True

    except KeyError as e:
        gs.output(f"Error loading game: invalid save file: {e}")
        return False
