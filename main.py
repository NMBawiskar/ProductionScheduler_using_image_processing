from required_classes.scheduler import *
from datetime import datetime

# Machine	StartDate	StartTime	EndDate	EndTime
# M1	1-1-22	XXX	1-2-22	XXX
# M1	1-2-22	XXX	1-3-22	XXX
# M1	1-3-22	08:00:00	1-4-22	16:00:00
# M1	1-4-22	08:00:00	1-5-22	16:00:00

def getMachineObj(listMachineObjects, machineName):
    for machineObj in listMachineObjects:
        if machineObj.name == machineName:
            return machineObj
    
    return None


machineList = ['M1','M2','M3']
machineObjList = []
for machineName in machineList:
    machineObj = Machine(machineName=machineName)
    machineObjList.append(machineObj)

    
stTime = datetime.strptime("1-1-22__08:00:00","%m-%d-%y__%H:%M:%S")
endTime =datetime.strptime("1-1-22__16:00:00","%m-%d-%y__%H:%M:%S")

day = stTime.date()

list_schedule = ['M1', day, stTime, endTime]


machineObj = getMachineObj(machineName)
if machineObj is not None:
    daySlotMachine = DaySlotMachine(day=day,machine=machineObj)
    