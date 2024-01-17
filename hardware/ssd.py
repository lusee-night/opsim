from simpy import Container as C

#################################################################################

class SSD(C):
    def __init__(self, env, init=0.0, capacity = 0.):
        C.__init__(self, env, init=init, capacity=capacity)

    def change (self, delta):
        if delta>0:
            self.put(delta)
        else:
            self.get(min(-delta, self.level))
            