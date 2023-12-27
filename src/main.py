import mainloop
import ship_cmds
import state
import setup

player = state.Player()

if setup.do_setup(player):
    ship_cmds.show_status(player, [])
    mainloop.run_loop(player)