import json
from pathlib import Path
from state import gs
import os

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
    data = {
        "seed": gs.seed,
        "player_name": gs.player.name,
        "player_birthplace": gs.player.birthplace,
        "player_doubloons": gs.player.doubloons,
        "ship_name": gs.ship.name,
    }
    json_string = json.dumps(data)
    err = _save(json_string)
    return err


def load_game():
    err, json_string = _load()
    if err:
        return err
    data = json.loads(json_string)
    gs.seed = data["seed"]
    gs.player.name = data["player_name"]
    gs.player.birthplace = data["player_birthplace"]
    gs.player.doubloons = data["player_doubloons"]
    gs.ship.name = data["ship_name"]
    return ""
