from simpy import Container as C

#################################################################################

class SSD(C):
    def __init__(self, env, config):
        initial = float(config['initial'])
        capacity = float(config['capacity'])
        C.__init__(self, env, init=initial, capacity=capacity)

    def change (self, delta):

        if delta>=0:
            self.put(delta)
        else:
            if self.level>0.0: self.get(min(-delta, self.level))
            