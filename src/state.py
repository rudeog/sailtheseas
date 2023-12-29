# manage global game state. This is at the top level

class GlobalState:
    def __init__(self):
        self.player = None
        self.map = None
        self.num_commands=0
        self.quitting=False
