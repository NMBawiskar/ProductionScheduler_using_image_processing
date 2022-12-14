from typing import List
import numpy as np
import cv2
from required_classes.machines_ import Machine
from collections import OrderedDict
import config
from matplotlib import pyplot as plt
import utils2

AVAILABLE = 255
NOT_AVAILABLE = 0
ASSIGNED = 127


MACHINE_AVAILABLE_COLOR = (255,0,0)
MACHINE_ASSIGNED_COLOR = (127,127,127)
MACHINE_NOT_AVAILABLE_COLOR = (0,0,0)


class DaySlotMachine:
    
    # weekSchedules = {}
    daySchedules = OrderedDict()
    days_list = []

    def __init__(self, day, machine:Machine):
        self.day = day
        self.day_string = self.day.strftime("%m-%d-%y")
        self.machine = machine
    

        self.daySlotArray = np.zeros((1,24), dtype='uint8')
        self.colorDaySlotArray = None

       
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

        self.gray_day_slot_img = None
        self.mask_operation_overlap_allowable = None
        self.mask_delay_overlap_allowable = None
        self.mask_assigned_hrs = None
        self.display_img_block = None

    def setInitialDayAvailability(self, stHr, endHr):
        self.dayStHr = stHr
        self.dayEndHr = endHr
        self.stHrForAssigning = stHr
        self.daySlotArray[:,:stHr] = NOT_AVAILABLE
        self.daySlotArray[:,stHr:endHr] = AVAILABLE
        self.daySlotArray[:,endHr:] = NOT_AVAILABLE
        self.display_img_block = cv2.merge((self.daySlotArray, self.daySlotArray, self.daySlotArray))
        self.render_display_img()
        self.get_gray_day_slot_img()

    def assign_weekend_day(self):
        self.daySlotArray[:,:] = NOT_AVAILABLE
        self.display_img_block = cv2.merge((self.daySlotArray, self.daySlotArray, self.daySlotArray))
        self.render_display_img()
        self.get_gray_day_slot_img()
    
    def create_img(self):
        oneCh = self.daySlotArray.copy()
        self.colorDaySlotArray = cv2.merge((oneCh, oneCh, oneCh))
        self.colorDaySlotArray = self.colorDaySlotArray.astype(np.uint8)
        self.colorDaySlotArray[self.daySlotArray==AVAILABLE] = MACHINE_AVAILABLE_COLOR
        self.colorDaySlotArray[self.daySlotArray==NOT_AVAILABLE] = MACHINE_NOT_AVAILABLE_COLOR
        self.colorDaySlotArray[self.daySlotArray==ASSIGNED] = MACHINE_ASSIGNED_COLOR
        self.img_working_hrs = self.colorDaySlotArray[:, self.dayStHr:self.dayEndHr]
        
        return self.colorDaySlotArray
    
    def get_gray_day_slot_img(self):
        self.create_img()
        self.gray_day_slot_img = np.zeros_like(self.daySlotArray)
        self.gray_day_slot_img[self.daySlotArray==AVAILABLE] = config.DAY_MACHINE_WORKING_COLOR
        self.gray_day_slot_img[self.daySlotArray==NOT_AVAILABLE] = config.DAY_MACHINE_NON_WORKING_COLOR
        self.gray_day_slot_img[self.daySlotArray==ASSIGNED] = config.DAY_MACHINE_ASSIGNED_COLOR

        self.mask_operation_overlap_allowable = np.zeros_like(self.daySlotArray)
        self.mask_operation_overlap_allowable[self.daySlotArray==AVAILABLE] = 255

        self.mask_delay_overlap_allowable = np.zeros_like(self.daySlotArray)
        self.mask_delay_overlap_allowable[self.daySlotArray==AVAILABLE] = 255
        self.mask_delay_overlap_allowable[self.daySlotArray==NOT_AVAILABLE] = 255

        self.mask_assigned_hrs = np.zeros_like(self.daySlotArray)
        self.mask_assigned_hrs[self.daySlotArray==ASSIGNED] = 255

        return self.gray_day_slot_img, self.mask_operation_overlap_allowable, self.mask_delay_overlap_allowable, self.mask_assigned_hrs

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


    def get_day_working_img(self):
        if self.img_working_hrs is None:
            self.create_img()
        
        return self.img_working_hrs


    @classmethod
    def assignMachineHrs_for_order(self, dict_machine_name_data_assignment):
        
        """data_to_assign is list [dayIndex, st_hrIndex, end_hrInde, 0 or 1]  0-cycleAssigned, 1-delayAssigned"""
        all_order_images = []
        title_list = []
        for machineName, list_data_to_assign in dict_machine_name_data_assignment.items(): 
            for data_to_assign in list_data_to_assign:
                dayIndex, stHrIndex, endHrIndex, cycle_or_delay = data_to_assign
                day = self.days_list[dayIndex]
                # daySlot = self.daySchedules[day][machineName]
                DaySlotMachine.daySchedules[day][machineName].daySlotArray[:, stHrIndex:endHrIndex] = ASSIGNED
            
                DaySlotMachine.daySchedules[day][machineName].get_gray_day_slot_img()
                if cycle_or_delay == 0:
                    ## cycle color 
                    color_assignment = config.DISPLAY_ASSIGNED_CYCLE_COLOR
                elif cycle_or_delay== 1:
                    color_assignment = config.DISPLAY_ASSIGNED_DELAY_COLOR

                DaySlotMachine.daySchedules[day][machineName].display_img_block[:,stHrIndex:endHrIndex] = color_assignment
                all_order_images.append(DaySlotMachine.daySchedules[day][machineName].display_img_block)
                title_list.append(f"{day}_{machineName}_{stHrIndex}__{endHrIndex}__{cycle_or_delay}")
        # utils2.plot_list_images(all_order_images,title_list)
            

    def render_display_img(self):
        self.display_img_block[self.daySlotArray==ASSIGNED] = config.DISPLAY_ASSIGNED_CYCLE_COLOR
        self.display_img_block[self.daySlotArray==NOT_AVAILABLE] = config.DISPLAY_NOT_ASSIGNED_NON_WORKING_COLOR
        self.display_img_block[self.daySlotArray==AVAILABLE] = config.DISPLAY_NOT_ASSIGNED_WORKING_COLOR
        

    
    @classmethod
    def get_display_day_machine_color_block(self, date_index, machineName):
        day = DaySlotMachine.days_list[date_index]
        daySCh = DaySlotMachine.daySchedules[day][machineName]
       
        # display_img = daySCh.display_img_block
        # utils.showImg(f'DayBlockDisplay_{day}',display_img)
        # cv2.waitKey(-1)
        return DaySlotMachine.daySchedules[day][machineName].display_img_block
