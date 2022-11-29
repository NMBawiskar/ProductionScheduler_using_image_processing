from typing import List
import numpy as np
import cv2

AVAILABLE = 1
NOT_AVAILABLE = 0
ASSIGNED = 0.5

DELAY_COLOR = (127,127,127)
OPERATION_COLOR = (0,255,255)

MACHINE_AVAILABLE_COLOR = (255,0,0)
MACHINE_ASSIGNED_COLOR = (127,127,127)
MACHINE_NOT_AVAILABLE_COLOR = (0,0,0)


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
        self.machine = machine

        self.daySlotArray = np.zeros((24,1), dtype=np.float32)
    
    def assignMachineHrs_filled(self, listHrsBooked:List[int]):
        """Function takes in list of hrs ex. [10,11,12,13,14] adds them to self.hrs_filled_up"""
        for hr in listHrsBooked: 
            self.daySlotArray[hr,0] = ASSIGNED

    def calculate_hrs_available(self):
        self.hrs_available = []
        for hr in range(1,25):
            if hr not in self.hrs_filled_up and hr not in self.hrs_not_working:
                self.hrs_available.append(hr)

    def add_non_working_hrs(self, stHr, endHr):
        for hr in range(stHr, endHr):
            self.daySlotArray[hr,0] = NOT_AVAILABLE

    def setInitialDayAvailability(self, stHr, endHr):
        for hr in range(stHr, endHr):
            self.daySlotArray[hr,0] = AVAILABLE
    
    def plot_img(self):
        oneCh = self.daySlotArray.copy()
        plotImgArray = cv2.merge((oneCh, oneCh, oneCh))
        plotImgArray = plotImgArray.astype(np.uint8)
        plotImgArray[self.daySlotArray==AVAILABLE] = MACHINE_AVAILABLE_COLOR
        plotImgArray[self.daySlotArray==NOT_AVAILABLE] = MACHINE_NOT_AVAILABLE_COLOR
        plotImgArray[self.daySlotArray==ASSIGNED] = MACHINE_ASSIGNED_COLOR
        widowName = f"daySchedule {self.machine.name} 1/1/22"
        cv2.namedWindow(widowName,cv2.WINDOW_NORMAL)
        cv2.imshow(widowName, plotImgArray)
        cv2.waitKey(-1)




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

        self.npArray = None

    def setCycleTime(self, cycleTimeInHrs):
        self.cycleTime = cycleTimeInHrs

    def setMinMaxDelays(self, minDelayHrs, maxDelayHrs):
        if minDelayHrs != "-":
            self.minDelayHrs = minDelayHrs
        if maxDelayHrs !="-":
            self.maxDelayHrs = maxDelayHrs


    def create_image(self):
        totalMaxHrs = self.cycleTime + self.maxDelayHrs
        self.npArray = np.zeros((1,totalMaxHrs,3), np.uint8)

        self.npArray[:, :self.cycleTime] = OPERATION_COLOR
        self.npArray[:, self.cycleTime:] = DELAY_COLOR


        return self.npArray


class Order_or_job:
    def __init__(self, id) -> None:
        self.id = id
        self.operationSeq = []

        self.assigned_st_dayTime = None     ## DateTimeObject
        self.assigned_end_dayTime = None    ## DateTimeObject

        isScheduleAssigned = False
        self.grayStartList = []
        self.grayEndList = []

        self.cumulativeOpEnd = 0

        self.totalMinTime = 0
        self.totalMaxTime = 0

    def setOperationSequences(self, operationSeqList:List[Operation]):
        self.operationSeq = operationSeqList

    def create_and_add_operation(self, df_line, machineObjList):

        """ """
        opId = self.id
        df_line = df_line.replace("-",0)
        step, machineRequired, prevOp, cycleTimeHrs, minDelay, maxDelay = df_line
        print("opId, step, machineRequired, prevOp, cycleTimeHrs, minDelay, maxDelay",opId, step, machineRequired, prevOp, cycleTimeHrs, minDelay, maxDelay)
        machineObjOperation = self.__getMachineObj(machineRequired, machineObjList)
        # operationId, cycleTimeHrs, minDelay, maxDelay = [f"{opId}_{step}", 4, 2, 10]
        operationId = f"{opId}_{step}"
        operation1 = Operation(operationID=operationId, machineReq=machineObjOperation)
        operation1.setCycleTime(cycleTimeHrs)
        if maxDelay != "-" and maxDelay!=0:
            graySt = self.cumulativeOpEnd + cycleTimeHrs
            grayEnd  = self.cumulativeOpEnd + cycleTimeHrs + maxDelay
            
            self.grayStartList.append(graySt)
            self.grayEndList.append(grayEnd)

            self.cumulativeOpEnd += grayEnd
        
        else:
            self.cumulativeOpEnd += cycleTimeHrs

        operation1.setMinMaxDelays(minDelay, maxDelay)

        self.operationSeq.append(operation1)
    
    def __getMachineObj(self, machineName, machineObjectsList):
        for machineObj in machineObjectsList:
            if machineObj.name == machineName:
                return machineObj
        
        return None
    
    def getOrderImage(self):

        imageList = []
        for operation in self.operationSeq:
            img = operation.create_image()
            imageList.append(img)
        
        # wList = [img.shape[1] for img in imageList]
        # totalSecondShape = sum(hList)
        
        newImage = np.hstack(imageList)
        print("self.grayStartList", self.grayStartList)
        print("self.grayStartList", self.grayEndList)
        widowName = f"Operation {self.id}"
        cv2.namedWindow(widowName,cv2.WINDOW_NORMAL)
        cv2.imshow(widowName, newImage)
        cv2.waitKey(-1)

        



class AllDayWiseMachineSchedules:

    def __init__(self) -> None:
        pass

    
