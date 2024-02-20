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
    data = {}
    data["player"] = gs.player.get()
    data["ship"] = gs.ship.get()
    data["crew"] = gs.crew.get()
    data["seed"] = gs.seed
    data["rng"] = save_rng_state_to_string(gs.rng_play)
    data["trade"] = _save_trading_data()
    data["visited"] = _save_visited_data()

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
        load_rng_state_from_string(gs.rng_play, data["rng"])
        d=data['player']
        if not gs.player.set(d):
            raise KeyError
        d=data["ship"]
        if not gs.ship.set(d):
            raise KeyError
        d=data["crew"]
        if not gs.crew.set(d):
            raise KeyError

    except KeyError:
        return None, "Save file may be from an earlier version."
    return data, ""


def load_trading_and_visited_data(loaded: dict):
    try:
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


        return True

    except Exception as e:
        gs.output(f"Error loading game: invalid save file: {e}")
        return False
