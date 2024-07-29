from datetime import time

# list of log targets that can be turned on.
# by default if logging is turned on, all targets are present

# GEN general logging (info)
# NAV navigation related logging
# TRADE trade related logging
log_targets = {'GEN','NAV','TRADE'}



def list_log_targets():
    for i in log_targets:
        print(i + " ")

class Logger:
    def __init__(self, filename, targets):
        self.file = open(filename, "w")
        self.targets = targets

    def log(self, level: str, message):
        if not self.targets or level.lower() in self.targets:
            log_message = f"[{level}] {message}\n"
            self.file.write(log_message)
            self.file.flush()

    def close(self):
        self.file.close()

global_logger: Logger = None

def init(f: str, filt):
    global global_logger
    lt = {}
    if filt:
        for i in filt:
            if i.upper() in log_targets:
                lt.append(i.lower())

    global_logger = Logger(f, lt)

def cleanup():
    if global_logger:
        global_logger.close()

def log(level, msg):
    if global_logger:
        global_logger.log(level, msg)
