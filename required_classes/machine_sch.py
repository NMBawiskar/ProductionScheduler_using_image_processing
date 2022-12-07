from typing import List
import numpy as np
import cv2
from required_classes.machines_ import Machine
from collections import OrderedDict
AVAILABLE = 1
NOT_AVAILABLE = 0
ASSIGNED = 0.5


MACHINE_AVAILABLE_COLOR = (255,0,0)
MACHINE_ASSIGNED_COLOR = (127,127,127)
MACHINE_NOT_AVAILABLE_COLOR = (0,0,0)


class DaySlotMachine:
    
    weekSchedules = {}
    daySchedules = OrderedDict()

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
        
        if self.day_string not in self.daySchedules.keys():
            self.daySchedules.__setitem__(self.day_string,{})
        if self.machine.name not in self.daySchedules[self.day_string].keys():
            self.daySchedules[self.day_string][self.machine.name] = self


        self.colorImg = None
        self.dayStHr = None
        self.dayEndHr = None
        self.stHrForAssigning = None

        self.img_working_hrs = None
        self.img_not_assigned_hrs = []   # list of not assigned blocks

        self.availableHrs = None
        self.assignedHrs = None
        self.notAvailableHrs = None
        self.hourList_available = []
        self.hourList_assigned = []

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
        self.dayStHr = stHr
        self.dayEndHr = endHr
        self.stHrForAssigning = stHr
        for hr in range(stHr, endHr):
            self.daySlotArray[0,hr] = AVAILABLE
    
    def create_img(self):
        oneCh = self.daySlotArray.copy()
        self.colorDaySlotArray = cv2.merge((oneCh, oneCh, oneCh))
        self.colorDaySlotArray = self.colorDaySlotArray.astype(np.uint8)
        self.colorDaySlotArray[self.daySlotArray==AVAILABLE] = MACHINE_AVAILABLE_COLOR
        self.colorDaySlotArray[self.daySlotArray==NOT_AVAILABLE] = MACHINE_NOT_AVAILABLE_COLOR
        self.colorDaySlotArray[self.daySlotArray==ASSIGNED] = MACHINE_ASSIGNED_COLOR
        self.img_working_hrs = self.colorDaySlotArray[:, self.dayStHr:self.dayEndHr]
        
        return self.colorDaySlotArray

  
    
    def get_available_hrs_assigned_hrs_count(self):
        if self.img_working_hrs is None:
            self.get_day_working_img()
        
        hrsAvailable = 0
        hrsAssigned = 0


        for hr in range(self.img_working_hrs.shape[1]):
            if self.img_working_hrs[0,hr] == MACHINE_AVAILABLE_COLOR:
                hrsAvailable +=1
                self.hourList_available.append(self.dayStHr+hr)
                
            elif self.img_working_hrs[0,hr] == MACHINE_ASSIGNED_COLOR:
                self.hourList_assigned.append(self.dayStHr+hr)
                hrsAssigned+=1
        
        self.assignedHrs = hrsAssigned
        self.availableHrs = hrsAvailable
        self.notAvailableHrs = 24 - self.assignedHrs - self.availableHrs

        return self.availableHrs



    def plot_img(self):
        widowName = f"daySchedule {self.machine.name} 1/1/22"
        
    @classmethod
    def plot_week_img(self, machineSequenceNames, weekNo=1):
        daysDict = DaySlotMachine.weekSchedules[weekNo]
        
        imgHt = sum([len(daysDict[machineName]) for machineName in daysDict.keys()])
        self.colorImg = np.zeros((imgHt, 24,3)).astype(np.uint8)

        rowNo = 0
        for i, dayStr in enumerate(daysDict.keys()):
            
            sortedmachineScheduleList = []
            for j, machineName in enumerate(machineSequenceNames):
                daySlot = daysDict[dayStr][machineName]
                imgDaySlot = daySlot.create_img()
                self.colorImg[rowNo:rowNo+1, :] = imgDaySlot
                rowNo+=1
        
                sortedmachineScheduleList.append(daySlot)

        
        return self.colorImg

    def get_day_working_img(self):
        if self.img_working_hrs is None:
            self.create_img()
        
        return self.img_working_hrs

    def get_available_working_slots(self):
        self.get_available_hrs_assigned_hrs_count()
        ## relative hrs 
        relativeHrList = [hr - self.dayStHr for hr in self.hourList_available]
        index_to_split_at =  []
        hr_list_crop = []
        for i, hrAvailable in enumerate(relativeHrList):
            if i>0:
                if hrAvailable - relativeHrList[i-1] == 1:
                    pass
                else:
                    index_to_split_at.append(i)

        if len(index_to_split_at)>0:
            ## more than one available block to assign
            for j, index in enumerate(index_to_split_at):
                if j==0:
                    hr_list_crop.append(relativeHrList[0:index])

                if j>0:                    
                    hr_list_crop.append(relativeHrList[index_to_split_at[j-1]:index_to_split_at[j]])
            hr_list_crop.append(relativeHrList[index_to_split_at[1]:]) 

        else:
            hr_list_crop = [relativeHrList]

        return hr_list_crop
