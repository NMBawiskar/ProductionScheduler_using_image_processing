from required_classes.prod_req import *
from required_classes.machine_sch import *

from utils import showImg
import cv2
import numpy as np
import config


GRAY_GRAY = 50
BLACK_GRAY = 0
YELLOW_GRAY = 157
BLUE_GRAY = 29

YELLOW_PLUS_BLUE_GRAY = 186
GRAY_PLUS_BLUE_GRAY = 79
BLACK_PLUS_BLUE_GRAY = 29


class ScheduleAssigner:
    days_list = []
    def __init__(self):
        self.current_weekImg = None
        self.current_weekNo = 0
    
        self.orderImg = None
        self.orderImgList = []
        self.currentOrderObj = None

        self.hWeek, self.wWeek = None, None
        self.hOrder, self.wOrder = None, None

        # self.days_list = []

    def assign_single_order(self, order:Order_or_job):
        
        self.totalOrderImg = order.getTotalOrderImage()
        self.currentOrderObj = order
        machineSeq = [operation.machineReq.name for operation in order.operationSeq]
        n_machines = len(machineSeq)
        print('machineSeq',machineSeq)
        showImg("totalOrderImg",self.totalOrderImg)


       
        allOpearationHrs = self.totalOrderImg.shape[1]
        opStartDateIndex = 0        
        totalDaysReq = int(allOpearationHrs / 8)+3
        daysScheduleImgList = [] 
        for day in ScheduleAssigner.days_list[opStartDateIndex:opStartDateIndex+totalDaysReq]:
            daySchedule = DaySlotMachine.daySchedules[day]
            machineDayImages = []
            for machine in machineSeq:
                if machine in daySchedule.keys():
                    dayScheduleReq = daySchedule[machine]
                    daySchImg = dayScheduleReq.get_day_working_img()
                    
                    machineDayImages.append(daySchImg)
                    # print("daySchImg.shape",daySchImg.shape)
            imgSingleDay = np.zeros((len(machineSeq), 8,3))
            # print("len(machineDayImages)",len(machineDayImages))
            for i, machineDayImg in enumerate(machineDayImages):                
                imgSingleDay[i:i+1, :] = machineDayImg
                # showImg('imgSingleDay',imgSingleDay)
                # cv2.waitKey(-1)
            
            daysScheduleImgList.append(imgSingleDay)
            # print("totalSingleDayImg.shape",imgSingleDay.shape)
    
        totaldayImage = np.hstack(tuple(daysScheduleImgList))
        showImg("totaldayImage",totaldayImage)
        # print("totaldayImage.shape",totaldayImage.shape)
        # print("self.totalOrderImg.shape",self.totalOrderImg.shape)

        gray_order_img = cv2.cvtColor(self.totalOrderImg.astype(np.uint8), cv2.COLOR_BGR2GRAY)
        gray_day_img = cv2.cvtColor(totaldayImage.astype(np.uint8), cv2.COLOR_BGR2GRAY)
        # gray_order_img = cv2.cvtColor(self.totalOrderImg, cv2.COLOR_BGR2GRAY)

        # print("np.unique(gray_order_img)",np.unique(gray_order_img))
        # print("np.unique(gray_day_img)",np.unique(gray_day_img))

        added = totaldayImage.copy()
        stHr = 0
        isOrderAssignable = False
        machineWiseImgAssigned = []
        while isOrderAssignable==False:
            added[:,stHr:stHr+allOpearationHrs] = added[:,stHr:stHr+allOpearationHrs]+self.totalOrderImg
            gray_added = gray_day_img.copy()
            gray_added[:,stHr:stHr+allOpearationHrs] = gray_added[:,stHr:stHr+allOpearationHrs]+gray_order_img

            # print("np.unique(gray_added)",np.unique(gray_added))
            showImg("convolutioned",added)
            showImg("gray_added",gray_added)
            showImg("gray_order_img",gray_order_img)
            showImg("gray_day_img",gray_day_img)
            
            stacked_gray_added = self.break_days_combined_image(gray_added)
            
            


            stacked_st_days = stacked_gray_added[:, 0]
            stacked_end_days = stacked_gray_added[:, -1]
            # print("stacked_st_days",stacked_st_days)
            # print("stacked_end_days",stacked_end_days)
            
            if GRAY_PLUS_BLUE_GRAY not in stacked_st_days and  GRAY_PLUS_BLUE_GRAY not in stacked_end_days:
                isOrderAssignable = True
                for i, machine in enumerate(machineSeq):
                    machine_img_all_days = gray_added[i:i+1, :]
                    stacked_gray_machine = self.break_days_combined_image(machine_img_all_days)
                    machineWiseImgAssigned.append(stacked_gray_machine)
                    
                break
            stHr+=1




            cv2.waitKey(-1)

        if isOrderAssignable==True:
            assigned_values_list = [] # list of operation with values stDate, stHr, endDate, endHr

            for i, machineWiseImg in enumerate(machineWiseImgAssigned):
                showImg(f'machine {machineSeq[i]}',machineWiseImg)

                points = np.argwhere(machineWiseImg>BLACK_PLUS_BLUE_GRAY)
                # print(f"machine {machineSeq[i]}", points)
                minRow = np.min(points, axis=0)[0]
                maxRow = np.max(points, axis=0)[0]
                minRowValues =  points[points[:,0]==minRow]
                maxRowValues = points[points[:,0]==maxRow]
                stHrIndex = np.min(minRowValues,axis=0)[1]
                endHrIndex = np.max(maxRowValues, axis=0)[1]
                
                stDate, endDate = ScheduleAssigner.cycleTimeHrs[opStartDateIndex+minRow], ScheduleAssigner.cycleTimeHrs[opStartDateIndex+maxRow]
                stHr, endHr = 8 + stHrIndex, 8 + endHrIndex
                # print(f"minRow {minRow} stHr {stHrIndex} maxRow {maxRow} endHrIndex {endHrIndex}")
                print(f"stDate {stDate} stHr {stHr}  endDate {endDate} endHr {endHr}")
                assigningList = [stDate, stHr, endDate, endHr]
                assigned_values_list.append(assigningList)
                # print("minRowValues",minRowValues)
                
            order.assign_order(assigned_values_list)
            cv2.waitKey(-1)    
            

    def break_days_combined_image(self, combinedImg):
        st = 0
        list_img_8hrs = []
        while True:
            end = st+8
            if st == combinedImg.shape[1]:
                break
            crop = combinedImg[:, st:end]
            list_img_8hrs.append(crop)
            st = end
        
        vstacked = np.vstack(list_img_8hrs)
        
        return vstacked



    def assign_order_operation_wise(self, order:Order_or_job):
        ###
        start_date_index = 0
        start_time_hr = 0

        for operation in order.operationSeq:

            machineName = operation.machineReq.name
            #### Get current day and machine day sch gray image
            daySlotGrayImg, mask_allowable_work, mask_allowable_delay = self.get_day_machine_sch_img(start_date_index, machineName)



            listOperationImages, mask_working_delay_images_list = operation.get_working_delay_img_list()


            for i, operationDelayImg in enumerate(listOperationImages):
                showImg('delay Img',operationDelayImg)
                
                mask_operation_working, mask_operation_delay = mask_working_delay_images_list[i]

                assignerSingleOperation = AssignerSingleOperation(startDayIndex=start_date_index, stHrIndex=start_time_hr,
                    operationGrayImg=operationDelayImg, operationMachinName=machineName)

                assignerSingleOperation.get_operation_img_day_mask()

                vaildator = Validator(dayScheduleImg=daySlotGrayImg, assigningOrderImg=operationDelayImg,
                    assigningWorkingHrMask=mask_operation_working, delayHrsMask= mask_operation_delay)



                showImg('mask_working',mask_operation_working)
                showImg('mask_operation_delay',mask_operation_delay)
                cv2.waitKey(-1)




    @classmethod
    def get_day_machine_sch_img(self, dayIndex, machineName):
        day = ScheduleAssigner.days_list[dayIndex]
        return DaySlotMachine.daySchedules[day][machineName].get_gray_day_slot_img()



    def get_next_day_image_for_order(self):
        """For each order if required, get next day schedule image and join to the current scheduler image"""
        pass


    def check_if_delay_hrs_to_resize(self):
        """Check if process is breaking at gray over gray..."""
        pass
    

    def break_operation_and_move_remaining_for_next_day(self):
        """"""
        pass

    def try_next_increment(self):
        pass

  
class AssignerSingleOperation:
    """Class to iterate over each hour and place the operation image over day/days schedule image"""

    def __init__(self, startDayIndex, stHrIndex, operationGrayImg, operationMachinName):
        self.startDayIndex = startDayIndex
        self.stHrIndex = stHrIndex
        self.operationGrayImg = operationGrayImg
        self.operationMachinName = operationMachinName
        
        self.list_day_oper_crop_images = []
        self.list_day_images = []

    def get_operation_img_day_mask(self):
        

        list_day_oper_crop_images = []  ## List containing list of  [dayImg, corr.operation crop img]
        width_op_img = self.operationGrayImg.shape[1]
        
        current_day_index = self.startDayIndex 
        # for i in range(5):
        #     current_day_index = i
        dayGrayImg, mask_allowable_work, mask_allowable_delay = ScheduleAssigner.get_day_machine_sch_img(dayIndex=current_day_index, machineName=self.operationMachinName)
        start_working_hr = self.get_starting_hr_operation_working(mask_allowable_delay)
        print("start_working hour", start_working_hr)


        showImg('dayGrayImg',dayGrayImg)
        showImg('mask_allowable_work',mask_allowable_work)
        showImg('mask_allowable_delay',mask_allowable_delay)
        cv2.waitKey(-1)
        print('sch')
        # current_st_hr = self.stHrIndex
        # endHr = current_st_hr + width_op_img

        # if endHr <= self.dayGrayImg.shape[1]:
        #     ## No need to crop

        #     operation_img_padded = np.zeros_like(dayGrayImg)
        #     operation_img_padded[:,current_st_hr:endHr] = self.operationGrayImg
        #     list_day_oper_crop_images.append([dayGrayImg, operation_img_padded])
        
        # else:
        #     ## get next day image
        #     remaining_img_w = 
        #     while 

        #     nextDayIndex += 1
        #     nextDay 
        #     DaySlotMachine.daySchedules[]

    def get_starting_hr_operation_working(self, mask_allowable_work):

        min_values = np.min(np.argwhere(mask_allowable_work==255))
        if len(min_values.shape) == 0:
            print("No whites found means no working hours available in the day")
            min_x = -1
        else:    
            min_x = min_values[1]
            print('min start working hr ', min_x)


        return min_x




    








class Validator:
    """Class to validate all order assigning rules"""
    def __init__(self, dayScheduleImg, assigningOrderImg, assigningWorkingHrMask, delayHrsMask, st_hr):
        self.assigningWorkingHrMask = assigningWorkingHrMask
        self.delayHrsMask = delayHrsMask
        self.assigningOrderImg = assigningOrderImg
        self.dayScheduleImg = dayScheduleImg

    def check_rule(self):
        """Rules
        1. Gray_order can overlap NightNon working hours as well as production hours
        2. Color_order can overlap only on working and non assigned hours of day
        3.     
        """

        

    def check_if_other_operation_assigned_in_between(self):
        """"""
        pass

    def check_if_color_on_gray(self):
        """"""
        pass
        




