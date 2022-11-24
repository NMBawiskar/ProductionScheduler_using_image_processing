from typing import List

AVAILABLE = 1
NOT_AVAILABLE = 0
ASSIGNED = 0.5
    

class Machine:
    def __init__(self, machineName):
        self.name = machineName

        self.available_daywise_slots = []
        self.filled_daywise_slots = []
        self.non_working_slots = []

    def schedule(self):
        pass

    def getDateAvailability(self, date):

        pass


class DaySlotMachine:
    def __init__(self, day, machine:Machine):
        self.day = day
        self.hrs_not_working = []  ### list of hrs
        self.hrs_filled_up = []
        self.hrs_available = []
    
    def assignMachineHrs_filled(self, listHrsBooked:List[int]):
        """Function takes in list of hrs ex. [10,11,12,13,14] adds them to self.hrs_filled_up"""
        self.hrs_filled_up.extend(listHrsBooked)

    def calculate_hrs_available(self):
        self.hrs_available = []
        for hr in range(1,25):
            if hr not in self.hrs_filled_up and hr not in self.hrs_not_working:
                self.hrs_available.append(hr)

    def add_non_working_hrs(self, stHr, endHr):
        for hr in range(stHr, endHr):
            self.hrs_not_working.append(hr)



class EachDaySchedule:
    def __init__(self, date) -> None:
        self.date = date
        self.listDaySlotMachines = []   # list containing DaySlot of each machines
    
    def addDaySlotOfmachine(self, daySlotMachine: DaySlotMachine):
        self.listDaySlotMachines.append(daySlotMachine)



class Operation:
    def __init__(self, operationID, machineReq:Machine):
        self.id = operationID
        self.machineReq = machineReq
        self.cycleTimeHrs = 0
        self.minDelayHrs = 0
        self.maxDelayHrs = 0
        self.timeOperation = 'hrs'

    def setCycleTime(self, cycleTimeInHrs):
        self.cycleTime = cycleTimeInHrs

    def setMinMaxDelayes(self, minDelayHrs, maxDelayHrs):
        self.minDelayHrs = minDelayHrs
        self.maxDelayHrs = maxDelayHrs


    def create_image(self):



class Order_or_job:
    def __init__(self, id) -> None:
        self.id = id
        self.operationSeq = []
    def setOperationSequences(self, operationSeqList:List[Operation]):
        self.operationSeq = operationSeqList




class AllDayWiseMachineSchedules:

    def __init__(self) -> None:
        pass

    
