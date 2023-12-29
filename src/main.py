import mainloop
import basic_cmds
import state
import setup

gs = state.GlobalState()

if setup.do_setup(gs):
    basic_cmds.show_status(gs, [])
    mainloop.run_loop(gs)