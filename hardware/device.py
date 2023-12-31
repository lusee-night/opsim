class Device():
    def __init__(self, name=None, profile = None, state='OFF'):
        self.name       = name
        self.state      = state
        self.currents   = profile

    def current(self):
        return self.currents[self.state]

    def info(self):
        name = self.name + ','
        return f'''Device:{name:16}\tstate:{self.state},\tcurrent:{self.current()}'''
    