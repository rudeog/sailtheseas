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
    if run_type is RunType.CHECK_AVAILABLE:
        return True
    if run_type is RunType.HELP or (not toks) or (toks[0] not in topics):
        gs.output("The following topics are available:")
        for k, v in topics.items():
            gs.output(f"{k} - {v[0]}", sub_indented=True)
        return

    gs.output(topics[toks[0]][1])


def register_info_cmds():
    gs.cmdsys.register(Command("read", "topic", cmd_info,
                                               "Display information about the game. Optionally specify an info topic to "
                                               "display that topic."))

