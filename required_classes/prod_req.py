from required_classes.machines_ import Machine
from typing import List
import numpy as np
import cv2
import config

DELAY_COLOR = (50,50,50)
OPERATION_COLOR = (10,255,20)


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
        self.grayImg = None

        self.operationStart_date = None
        self.operationStart_time = None
        self.operationEnd_date = None
        self.operationEnd_time = None

    # def __str__(self):
        # return f"opId {self.id}, step, machineRequired, prevOp, cycleTimeHrs, minDelay, maxDelay , step, machineRequired, prevOp, cycleTimeHrs, minDelay, maxDelay)
   
    def setCycleTime(self, cycleTimeInHrs):
        self.cycleTimeHrs = cycleTimeInHrs

    def setMinMaxDelays(self, minDelayHrs, maxDelayHrs):
        if minDelayHrs != "-":
            self.minDelayHrs = minDelayHrs
        if maxDelayHrs !="-":
            self.maxDelayHrs = maxDelayHrs
        
        self.totalMaxHrs = self.cycleTimeHrs + self.maxDelayHrs
        self.totalMinHrs = self.cycleTimeHrs + self.minDelayHrs

    def create_image(self):
        singleCh = np.zeros((1,self.totalMaxHrs),dtype=np.float32)
        self.npArray = cv2.merge((singleCh,singleCh,singleCh))
        self.npArray = self.npArray.astype(np.uint8)
        self.npArray[:, :self.cycleTimeHrs] = OPERATION_COLOR
        self.npArray[:, self.cycleTimeHrs:] = DELAY_COLOR


        return self.npArray
    
    def get_working_delay_img_list(self):

        imageListWithMinMaxDelay = []
        mask_working_delay_images_list = []

        for delayHr in range(self.minDelayHrs, self.maxDelayHrs+1):
                
            grayImg = np.zeros((1, self.cycleTimeHrs + delayHr, 1), dtype='uint8')
            mask_operation_working = np.zeros_like(grayImg)
            mask_operation_delay = np.zeros_like(grayImg)

            grayImg[:, :self.cycleTimeHrs] = config.OPERATION_COLOR
            mask_operation_working[:, :self.cycleTimeHrs] = 255

            grayImg[:, self.cycleTimeHrs:] = config.DELAY_COLOR
            mask_operation_delay[:, self.cycleTimeHrs:] = 255
            imageListWithMinMaxDelay.append(grayImg)
            mask_working_delay_images_list.append([mask_operation_working, mask_operation_delay])
        

        return imageListWithMinMaxDelay, mask_working_delay_images_list




    def print_operation_schedule(self):
        print(f"""Operation ID {self.id} : Machine {self.machineReq.name} START {self.operationStart_date} 
        - {self.operationStart_time} hrs, END {self.operationEnd_date} - {self.operationEnd_time} hrs
        """)



class Order_or_job:
    orderList = []
    def __init__(self, id) -> None:
        self.id = id
        self.operationSeq = []

        self.assigned_st_dayTime = None     ## DateTimeObject
        self.assigned_end_dayTime = None    ## DateTimeObject

        self.isScheduleAssigned = False
        self.grayStartList = []
        self.grayEndList = []

        self.cumulativeOpEnd = 0

        self.totalMinTime = 0
        self.totalMaxTime = 0

        self.orderImg = None
        self.orderImageListSeq = []
        self.isInfeasibleForProduction = False


    def setOperationSequences(self, operationSeqList:List[Operation]):
        self.operationSeq = operationSeqList

        self.check_operations_infeasibility_by_delay_hrs()

    def create_and_add_operation(self, df_line, machineObjList):

        """ """
        opId = self.id
        df_line = df_line.replace("-",0)
        step, machineRequired, prevOp, cycleTimeHrs, minDelay, maxDelay = df_line
        
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
    
    def getOrderOperationImageList(self):
        
        
        
        for i, operation in enumerate(self.operationSeq):
            imgOp = operation.create_image()
            self.orderImageListSeq.append(imgOp)
        
       
        widowName = f"Operation {self.id}"
        
        return self.orderImageListSeq


    def getTotalOrderImage(self):
        if len(self.orderImageListSeq)==0:
            self.getOrderOperationImageList()
        
        imageHt = len(self.operationSeq)
        imageWd = self.totalMaxTime
        self.orderImg = np.zeros((imageHt, imageWd, 3))
        
        st = 0
        for i, img in enumerate(self.orderImageListSeq):
            operationImgWidth = img.shape[1]
            end = st + operationImgWidth
            self.orderImg[i, st:end] = img

            st = end

        return self.orderImg 



    def __str__(self):
        return f"Order name {self.id} assignedstDay {self.assigned_st_dayTime}"
        
    def save_order(self):
        self.orderList.append(self)


    def assign_order(self, assigned_values_list):
        """assign all operations the start and end time
        param list of list of assigning values ex [[stDate, stHr, endDate, endHr], [stDate, stHr, endDate, endHr]]"""
        
        for i, operation in enumerate(self.operationSeq):
            # start_day_operation = start_day_first_operation
            stDate, stHr, endDate, endHr = assigned_values_list[i]
            operation.operationStart_date =stDate
            operation.operationStart_time = stHr
            operation.operationEnd_date = endDate
            operation.operationEnd_time = endHr
        
        self.isScheduleAssigned = True
        self.isInfeasibleForProduction=False
    
    def print_order_assigned_status(self):
        if self.isInfeasibleForProduction:
            print(f"Order {self.id} is infeasible for scheduling for production")
        else:
            if self.isScheduleAssigned:
                print(f"Order {self.id} is scheduled for production as below : ")
                for operation in self.operationSeq:
                    operation.print_operation_schedule()
                

    def check_operations_infeasibility_by_delay_hrs(self):
        for operation in self.operationSeq:
            if operation.minDelayHrs > 8:
                self.isInfeasibleForProduction=True
                break
    
    

