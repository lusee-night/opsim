class Device():
    def __init__(self, name=None, power_profile = None, data_profile = None, state='OFF'):
        self.name       = name
        self.state      = state
        # add OFF state if not present
        if (power_profile is not None) and ('OFF' not in power_profile):
            power_profile['OFF'] = 0.0
        if (data_profile is not None) and ('OFF' not in data_profile):
            data_profile['OFF'] = 0.0
        self.powers   = power_profile
        self.data_rates = data_profile

    def power(self):
        if self.power is None:
            return 0.0
        return self.powers[self.state]
    
    def power_tx(self):
        if self.power is None:
            return 0.0
        return self.powers['TX']
    
    def data_rate(self):
        if self.data_rates is None:
            return 0.0
        return self.data_rates[self.state]
    
    def data_rate_tx(self):
        if self.data_rates is None:
            return 0.0
        return self.data_rates['TX']

    def info(self):
        name = self.name + ','
        return f'''Device:{name:16}\tstate:{self.state},\power:{self.power()}'''
    