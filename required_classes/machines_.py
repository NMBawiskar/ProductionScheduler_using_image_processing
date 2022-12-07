


class Machine:
    dict_machine_name = {}
    def __init__(self, machineName):
        self.name = machineName

        self.available_daywise_slots = []
        self.filled_daywise_slots = []
        self.non_working_slots = []
        self.dict_machine_name[self.name] = self

    def schedule(self):
        pass

    def getDateAvailability(self, date):
        pass
