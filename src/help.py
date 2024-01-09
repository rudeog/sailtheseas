from state import global_state
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
        global_state.output("Info topics provide info and background about the game.")
        return
    if toks:
        if toks[0] in topics:
            global_state.output(topics[toks[0]][1])
        else:
            global_state.output("That topic does not exist.")

    global_state.output("The following info topics are available. Enter 'info' or 'i' "
                        "followed by a topic name to read that topic:")
    for k, v in topics.items():
        global_state.output(f"{k} - {v[0]}", sub_indented=True)
    return


def register_info_cmds():
    global_state.cmdsys.register_basic(Command("info", "[topic]", cmd_info,
                                               "Display information about the game. Optionally specify an info topic to "
                                               "display that topic."))
    global_state.cmdsys.register_alias("i", "info")
