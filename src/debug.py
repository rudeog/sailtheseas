# debugging stuff


class PromptWriter:
    def __init__(self, filename):
        self.file=None
        try:
            self.file = open(filename, "w")
        except:
            print(f"Could not open prompt file {filename} for writing")

    def write(self,val, prompt):
        if self.file:
            self.file.write("___"+prompt+"\n"+ val+"\n")
            self.file.flush()

    def close(self):
        if self.file:
            self.file.close()


class PromptReader:
    def __init__(self, filename):
        self.file = None
        try:
            self.file = open(filename, "r")
        except FileNotFoundError:
            print(f"Could not open prompt file {filename} for reading")


    def read(self):
        if not self.file:
            return None

        while True:
            line = self.file.readline()
            if not line:
                self.close()
                return None
            if not line.startswith("___"):
                return line.rstrip('\n')

    def close(self):
        if self.file:
            self.file.close()
            self.file = None


global_reader = None
global_writer = None

def open_prompt_writer(fn):
    global global_writer
    global_writer = PromptWriter(fn)

def write_prompt(txt, prompt):
    global global_writer
    if global_writer:
        global_writer.write(txt, prompt)

# close all
def close_prompt():
    global global_writer, global_reader
    if global_writer:
        global_writer.close()
    if global_reader:
        global_reader.close()

def open_prompt_reader(fn):
    global global_reader
    global_reader=PromptReader(fn)

def read_prompt():
    global global_reader
    ret = None
    if global_reader:
        ret = global_reader.read()
        if not ret:
            global_reader = None
    return ret