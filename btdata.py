import datetime

class btQuote:
    def __init__(self, dt, value):
        self.datetime = dt
        self.value = value
        


class btTrade:
    def __init__(self):
        self.date = None
        self.price = None
        self.volume = None
        self.id = None
        self.type = None
