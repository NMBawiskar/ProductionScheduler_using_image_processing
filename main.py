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


machineObj = getMachineObj(machineObjList, 'M2')
if machineObj is not None:
    daySlotMachine = DaySlotMachine(day=day,machine=machineObj)
    daySlotMachine.setInitialDayAvailability(stTime.hour, endTime.hour)
    daySlotMachine.plot_img()


############ Create operations
# OrderId	Step	MachineRequired	SuccessorStep	CycleTime(Hrs)	MinDelay	MaxDelay
# CO1	OP10	M1	OP30	4	2	10
# CO1	OP20	M2	OP30	5	0	0
# CO1	OP30	M3	-	5	-	-
    
machineObjOperation = getMachineObj(machineObjList, 'M1')
operationId, cycleTimeHrs, minDelay, maxDelay = ["C01_OP10", 4,2,10]
operation1 = Operation(operationID=operationId, machineReq=machineObjOperation)
operation1.setCycleTime(cycleTimeHrs)
operation1.setMinMaxDelays(minDelay, maxDelay)


machineObjOperation = getMachineObj(machineObjList, 'M2')
operationId, cycleTimeHrs, minDelay, maxDelay = ["C01_OP20", 5,0,0]
operation2 = Operation(operationID=operationId, machineReq=machineObjOperation)
operation2.setCycleTime(cycleTimeHrs)
operation2.setMinMaxDelays(minDelay, maxDelay)

machineObjOperation = getMachineObj(machineObjList, 'M3')
operationId, cycleTimeHrs, minDelay, maxDelay = ["C01_OP30", 5,0,0]
operation3 = Operation(operationID=operationId, machineReq=machineObjOperation)
operation3.setCycleTime(cycleTimeHrs)
operation3.setMinMaxDelays(minDelay, maxDelay)

ORDER_NAME = 'C01'
orderC01 = Order_or_job(id=ORDER_NAME)
orderC01.setOperationSequences([operation1, operation2, operation3])

for order in orderC01.operationSeq:
    order.create_image()