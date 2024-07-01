class Device():
    def __init__(self, name=None, power_profile = None, outside_heat_profile = None, data_profile = None, state='OFF'):
        self.name       = name
        self.state      = state
        # add OFF state if not present
        if (power_profile is not None) and ('OFF' not in power_profile):
            power_profile['OFF'] = 0.0
        if (data_profile is not None) and ('OFF' not in data_profile):
            data_profile['OFF'] = 0.0
        self.powers   = power_profile
        self.outside_heat = outside_heat_profile
        self.data_rates = data_profile

    def power(self, get_heat=False):
        power = self.powers[self.state]
        if get_heat and self.outside_heat is not None:
            power -= self.outside_heat.get(self.state, 0.0)
        return power
    
    def heat(self):
        return self.power(get_heat=True)
    
    def power_tx(self, get_heat=False):
        ## we will only calls this if this is UT. So let's assert this
        assert ('TX' in self.powers)
        power = self.powers['TX'] 
        if get_heat and self.out_side_heat is not None:
            power -= self.outside_heat.get('TX', 0.0)
        return power


    def heat_tx(self):
        return self.power_tx(get_heat=True)

    def data_rate(self):
        if self.data_rates is None:
            return 0.0
        return self.data_rates[self.state]

    def info(self):
        name = self.name + ','
        return f'''Device:{name:16}\tstate:{self.state},\power:{self.power()}'''
    