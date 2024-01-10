from simpy import Container as C

#################################################################################

class SSD(C):
    def __init__(self, env, init=0.0, capacity = 0.):
        C.__init__(self, env, init=init, capacity=capacity)

