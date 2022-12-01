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


class DaySlotMachine:
    
    weekSchedules = {}

    def __init__(self, day, machine:Machine, weekNo):
        self.day = day
        self.day_string = self.day.strftime("%m-%d-%y")
        self.machine = machine
        self.weekNo = weekNo

        self.daySlotArray = np.zeros((1,24), dtype=np.float32)
        self.colorDaySlotArray = None

        if self.weekNo not in self.weekSchedules.keys():
            self.weekSchedules[weekNo] = {}
        if self.day_string not in self.weekSchedules[weekNo].keys():
            self.weekSchedules[weekNo][self.day_string] = {}
        if self.machine.name not in self.weekSchedules[weekNo][self.day_string].keys():
            self.weekSchedules[weekNo][self.day_string][self.machine.name] = self
            

    def assignMachineHrs_filled(self, listHrsBooked:List[int]):
        """Function takes in list of hrs ex. [10,11,12,13,14] adds them to self.hrs_filled_up"""
        for hr in listHrsBooked: 
            self.daySlotArray[0,hr] = ASSIGNED

    def calculate_hrs_available(self):
        self.hrs_available = []
        for hr in range(1,25):
            if hr not in self.hrs_filled_up and hr not in self.hrs_not_working:
                self.hrs_available.append(hr)

    def add_non_working_hrs(self, stHr, endHr):
        for hr in range(stHr, endHr):
            self.daySlotArray[0,hr] = NOT_AVAILABLE

    def setInitialDayAvailability(self, stHr, endHr):
        for hr in range(stHr, endHr):
            self.daySlotArray[0,hr] = AVAILABLE
    
    def create_img(self):
        oneCh = self.daySlotArray.copy()
        self.colorDaySlotArray = cv2.merge((oneCh, oneCh, oneCh))
        self.colorDaySlotArray = self.colorDaySlotArray.astype(np.uint8)
        self.colorDaySlotArray[self.daySlotArray==AVAILABLE] = MACHINE_AVAILABLE_COLOR
        self.colorDaySlotArray[self.daySlotArray==NOT_AVAILABLE] = MACHINE_NOT_AVAILABLE_COLOR
        self.colorDaySlotArray[self.daySlotArray==ASSIGNED] = MACHINE_ASSIGNED_COLOR
        return self.colorDaySlotArray

    
    def plot_img(self):
        widowName = f"daySchedule {self.machine.name} 1/1/22"
        # cv2.namedWindow(widowName,cv2.WINDOW_NORMAL)
        # cv2.imshow(widowName, self.colorDaySlotArray)
        # cv2.waitKey(-1)
    @classmethod
    def plot_week_img(self, machineSequenceNames, weekNo=1):
        daysDict = DaySlotMachine.weekSchedules[weekNo]
        
        imgHt = sum([len(daysDict[machineName]) for machineName in daysDict.keys()])
        imageColorNew = np.zeros((imgHt, 24,3)).astype(np.uint8)

        rowNo = 0
        for i, dayStr in enumerate(daysDict.keys()):
            
            sortedmachineScheduleList = []
            for j, machineName in enumerate(machineSequenceNames):
                daySlot = daysDict[dayStr][machineName]
                imgDaySlot = daySlot.create_img()
                imageColorNew[rowNo:rowNo+1, :] = imgDaySlot
                rowNo+=1
                sortedmachineScheduleList.append(daySlot)

        cv2.imshow("Week no. {weekNo}", imageColorNew)
        cv2.waitKey(-1)


class Operation:
    def __init__(self, operationID, machineReq:Machine):
        self.id = operationID
        self.machineReq = machineReq
        self.cycleTimeHrs = 0
        self.minDelayHrs = 0
        self.maxDelayHrs = 0
        self.timeOperation = 'hrs'
        self.totalMaxHrs = 0
        self.totalMinHrs = 0

        self.npArray = None

    def setCycleTime(self, cycleTimeInHrs):
        self.cycleTime = cycleTimeInHrs

    def setMinMaxDelays(self, minDelayHrs, maxDelayHrs):
        if minDelayHrs != "-":
            self.minDelayHrs = minDelayHrs
        if maxDelayHrs !="-":
            self.maxDelayHrs = maxDelayHrs
        
        self.totalMaxHrs = self.cycleTime + self.maxDelayHrs
        self.totalMinHrs = self.cycleTime + self.minDelayHrs

    def create_image(self):
        self.npArray = np.zeros((1,self.totalMaxHrs,3)).astype(np.uint8)

        self.npArray[:, :self.cycleTime] = OPERATION_COLOR
        self.npArray[:, self.cycleTime:] = DELAY_COLOR


        return self.npArray


class Order_or_job:
    orderList = []
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

        self.orderImg = None

    def setOperationSequences(self, operationSeqList:List[Operation]):
        self.operationSeq = operationSeqList

    def create_and_add_operation(self, df_line, machineObjList):

        """ """
        opId = self.id
        df_line = df_line.replace("-",0)
        step, machineRequired, prevOp, cycleTimeHrs, minDelay, maxDelay = df_line
        print("opId, step, machineRequired, prevOp, cycleTimeHrs, minDelay, maxDelay",opId, step, machineRequired, prevOp, cycleTimeHrs, minDelay, maxDelay)
        machineObjOperation = self.__getMachineObj(machineRequired)
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
        self.totalMinTime += operation1.totalMinHrs
        self.totalMaxTime += operation1.totalMaxHrs

        self.operationSeq.append(operation1)
    
    def __getMachineObj(self, machineName):
        if machineName in Machine.dict_machine_name.keys():
            return Machine.dict_machine_name[machineName]
        else:
            return None
    
    def getOrderImage(self):
        
        imageHt = len(self.operationSeq)
        imageWd = self.totalMaxTime
        newImage = np.zeros(shape=(imageHt, imageWd, 3))
        
        self.orderImg = newImage.astype(np.uint8)
        # imageList = []
        startX = 0
        for i, operation in enumerate(self.operationSeq):
            imgOp = operation.create_image()
            self.orderImg[i:i+1, startX:startX+operation.totalMaxHrs] = imgOp
            startX = startX+operation.totalMaxHrs
        
 
        print("self.grayStartList", self.grayStartList)
        print("self.grayStartList", self.grayEndList)
        widowName = f"Operation {self.id}"
        cv2.namedWindow(widowName,cv2.WINDOW_NORMAL)
        cv2.imshow(widowName, self.orderImg)
        cv2.waitKey(-1)
        return self.orderImg

        
    def save_order(self):
        self.orderList.append(self)    




class ScheduleAssigner:
    def __init__(self):
        pass
    
    def assign_single_order(self, order:Order_or_job):
        orderImg = order.getOrderImage()

        hImg, wImg = orderImg.shape[:2]
        machineSequence = [operation.machineReq.name for operation in order.operationSeq]
        sortedWeekList = sorted(list(DaySlotMachine.weekSchedules.keys())) 
        # for week in sortedWeekList:
        #     DaySlotMachine.weekSchedules[week].plo
        
        DaySlotMachine.plot_week_img(machineSequenceNames=machineSequence, weekNo=1)

