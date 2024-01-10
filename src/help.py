from state import gs
from command import Command, RunType

topics = {"about": ["About the game",
                    "This is a turn based game in which you sail to and explore islands, trade goods, do battle and "
                    "collect rewards. You play this game by issuing text commands. The game will only "
                    "progress as you enter commands. You are awarded points based on your accomplishments."],
          "trading": ["How to buy and sell goods",
                      "Buy low sell high!"],
          }


def cmd_info(run_type: RunType, toks):
    if run_type == RunType.CHECK_AVAILABLE:
        return True
    if run_type == RunType.HELP:
        gs.output("Info topics provide info and background about the game.")
        return
    if toks:
        if toks[0] in topics:
            gs.output(topics[toks[0]][1])
        else:
            gs.output("That topic does not exist.")

    gs.output("The following info topics are available. Enter 'info' or 'i' "
                        "followed by a topic name to read that topic:")
    for k, v in topics.items():
        gs.output(f"{k} - {v[0]}", sub_indented=True)
    return


def register_info_cmds():
    gs.cmdsys.register_basic(Command("info", "[topic]", cmd_info,
                                               "Display information about the game. Optionally specify an info topic to "
                                               "display that topic."))
    gs.cmdsys.register_alias("i", "info")
