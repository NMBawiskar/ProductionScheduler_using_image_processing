from required_classes.prod_req import *
from required_classes.machine_sch import *

# from utils import showImg
import cv2
import numpy as np
import config
# from utils import get_operation_work_and_delay_masks, showImg

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
        self.increment = 1

        # self.days_list = []

    def assign_single_order(self, order):
        
        self.totalOrderImg = order.getTotalOrderImage()
        self.currentOrderObj = order
        machineSeq = [operation.machineReq.name for operation in order.operationSeq]
        n_machines = len(machineSeq)
        print('machineSeq',machineSeq)
        # showImg("totalOrderImg",self.totalOrderImg)


       
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
            # showImg("convolutioned",added)
            # showImg("gray_added",gray_added)
            # showImg("gray_order_img",gray_order_img)
            # showImg("gray_day_img",gray_day_img)
            
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



    def assign_order_operation_wise(self, order):
        ###
        

        ### 1. Get first/next operation, its machine name, start day and start hour 
        ### 2. get corresponding machine daySlot
        ### 3. Try assigning 
        ### 4. If assigned return current operation end Hr and end dayIndex, take next operation at End hour and end day of prev operation
        ### Repeat the process above
        
        n_operations = len(order.operationSeq)

        ### 1. Get firstoperation, set its temp start day and start hour 
        first_operation_index = 0
        first_operation = order.operationSeq[first_operation_index]
        
        
        trial_start_hr = 0
        trial_start_day_index = 0
        endCycleDayIndex, endCycleHrIndex = first_operation.try_assigning_op_cycle(trial_start_day_index, trial_start_hr, isFirstOrder=True)
        if endCycleDayIndex is not None:
            ## if delay hrs in operation
            if first_operation.maxDelayHrs>0:
                ### try assigning delay hrs
                endDelayDayIndex, endDelayHrIndex = first_operation.try_assigning_op_delay(endCycleDayIndex, endCycleHrIndex)
                first_operation.temp_assigned_end_day_index, first_operation.temp_assigned_end_hr_index = endDelayDayIndex, endDelayHrIndex
                if endDelayDayIndex is None:
                    #### Operation not assignable 
                    ### Increment and restart the process 
                    first_operation.temp_assigned_end_hr_index += self.increment
             


            else:
                ### no min max delay
                endDelayDayIndex, endDelayHrIndex = endCycleDayIndex, endCycleHrIndex
                first_operation.temp_assigned_end_day_index, first_operation.temp_assigned_end_hr_index = endDelayDayIndex, endDelayHrIndex


        print("FIRST operation temporary assignment details :")
        print(f"""Operation ID {first_operation.id} : Machine {first_operation.machineReq.name} 
        START {ScheduleAssigner.days_list[first_operation.temp_assigned_st_day_index]} 
        - {first_operation.temp_assigned_st_hr_index} hrs, END {ScheduleAssigner.days_list[first_operation.temp_assigned_end_day_index]} 
        - {first_operation.temp_assigned_end_hr_index} hrs
        """)
        #### once done first operation
        # next_operations are directly assigned and checked for validations

        prev_op_end_day_index = first_operation.temp_assigned_end_day_index
        prev_op_end_hr_index = first_operation.temp_assigned_end_hr_index

        for i in range(1,n_operations):
            print("Trying to set next operation")
            next_operation = order.operationSeq[i]
            print(next_operation)
            endCycleDayIndex, endCycleHrIndex = next_operation.try_assigning_op_cycle(prev_op_end_day_index, prev_op_end_hr_index, isFirstOrder=False)

            if endCycleDayIndex is not None:
                ## if delay hrs in operation
                if next_operation.maxDelayHrs>0:
                    ### try assigning delay hrs
                    endDelayDayIndex, endDelayHrIndex = next_operation.try_assigning_op_delay(endCycleDayIndex, endCycleHrIndex)
                    next_operation.temp_assigned_end_day_index, next_operation.temp_assigned_end_hr_index = endDelayDayIndex, endDelayHrIndex
                    # if endDelayDayIndex is None:
                    #     #### Operation not assignable 
                    #     ### Increment and restart the process 
                    #     next_operation.temp_assigned_end_hr_index += self.increment

                else:
                    ### no min max delay
                    endDelayDayIndex, endDelayHrIndex = endCycleDayIndex, endCycleHrIndex
                    next_operation.temp_assigned_end_day_index, next_operation.temp_assigned_end_hr_index = endDelayDayIndex, endDelayHrIndex

                print("FIRST operation temporary assignment details :")
                print(f"""Operation ID {next_operation.id} : Machine {next_operation.machineReq.name} 
                START {ScheduleAssigner.days_list[next_operation.temp_assigned_st_day_index]} 
                - {next_operation.temp_assigned_st_hr_index} hrs, END {ScheduleAssigner.days_list[next_operation.temp_assigned_end_day_index]} 
                - {next_operation.temp_assigned_end_hr_index} hrs
                """)
                prev_op_end_day_index = endDelayDayIndex
                prev_op_end_hr_index = endDelayHrIndex


      



    @classmethod
    def get_day_machine_sch_img(self, dayIndex, machineName):
        day = ScheduleAssigner.days_list[dayIndex]
        return DaySlotMachine.daySchedules[day][machineName]



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
    """Class i) to iterate over each hour and 
        ii) place the operation image over day/days schedule image
        iii) validate rules
        iv) return the final, start_daytime, end_daytime, delayHours used"""

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
        
        for i in range(10): # 10 days
        # while True:
            dayGrayImg, mask_allowable_work, mask_allowable_delay, mask_assigned_hrs = ScheduleAssigner.get_day_machine_sch_img(dayIndex=current_day_index, machineName=self.operationMachinName)
            start_working_hr = self.get_starting_hr_operation_working(mask_allowable_work)

            if start_working_hr == -1:
                ### Means no working hour available in that day
                current_day_index+=1
            else:
                ### Try assigning the at start hr
                remaining_operation_img = self.operationGrayImg
                self.validate_and_crop_operation_for_next_day(remaining_operation_img, dayStartIndex=current_day_index, startHr=start_working_hr)

              

            print("start_working hour", start_working_hr)


            # showImg('dayGrayImg',dayGrayImg)
            # showImg('mask_allowable_work',mask_allowable_work)
            # showImg('mask_allowable_delay',mask_allowable_delay)
            # cv2.waitKey(-1)
            print('sch')
     

    def get_starting_hr_operation_working(self, mask_allowable_work):

        if mask_allowable_work.size==0:
            min_x = 1
        else:
            coordinates = np.argwhere(mask_allowable_work==255)
            if coordinates.size==0:
                min_x=-1
                print("No whites found means no working hours available in the day")
            else:
                min_values = np.min(np.argwhere(mask_allowable_work==255), axis=0)
                if len(min_values.shape) == 0:
                    print("No whites found means no working hours available in the day")
                    min_x = -1
                else:    
                    min_x = min_values[1]
                    print('min start working hr ', min_x)

        return min_x

    def validate_and_crop_operation_for_next_day(self, remaining_operation_gray_img, dayStartIndex, startHr):
        """Function validate rule of assigning and returns operationAssigned, stHr, endHr, 
            and Remaining cropped image for next day assignment"""

        dayGrayImg, mask_allowable_work, mask_allowable_delay, mask_assigned_hrs = ScheduleAssigner.get_day_machine_sch_img(dayIndex=dayStartIndex, 
                            machineName=self.operationMachinName)
        
        
        mask_operation_work, mask_operation_delay = utils.get_operation_work_and_delay_masks(remaining_operation_gray_img)

        assigned_day_operation_work_mask = np.zeros_like(dayGrayImg)
        assigned_day_operation_delay_mask = np.zeros_like(dayGrayImg)
        width_operation_remaining = remaining_operation_gray_img.shape[1]
        endHr = startHr + width_operation_remaining

        if endHr <= dayGrayImg.shape[1]:
            assigned_day_operation_delay_mask[:,startHr:endHr] = mask_operation_delay
            assigned_day_operation_work_mask[:,startHr:endHr] = mask_operation_work

            stacked_delay_mask = np.vstack((mask_allowable_delay,assigned_day_operation_delay_mask))
            stacked_work_mask = np.vstack((mask_allowable_work,assigned_day_operation_work_mask))
            
            work_subtracted_mask = assigned_day_operation_work_mask - mask_allowable_work
            isOverlapPerfect, cropEndHr = self.check_if_color_on_gray(work_subtracted_mask, assigned_day_operation_work_mask)
            if isOverlapPerfect==True:
                #if color fits perfectly, start putting delay after that
                EndHrOperation_working = cropEndHr
                next_day_crop_gray = None
                return isOverlapPerfect, dayStartIndex, startHr, endHr, next_day_crop_gray
                
            else:
                next_day_crop_mask_total = assigned_day_operation_work_mask[:, cropEndHr:]
                hrs_remaining_for_next_day = np.sum(next_day_crop_mask_total==255)
                next_day_crop_gray = remaining_operation_gray_img[:,width_operation_remaining-hrs_remaining_for_next_day:]
                return isOverlapPerfect, dayStartIndex, startHr, cropEndHr, next_day_crop_gray


            
        #     # work_subtracted_negativemask = mask_allowable_work-assigned_day_operation_work_mask

            
        #     showImg("stacked_delay_mask",stacked_delay_mask)
        #     showImg("stacked_work_mask",stacked_work_mask)
        #     showImg("diff_work",work_subtracted_mask)
        #     # showImg("work_subtracted_negativemask",work_subtracted_negativemask)
        #     cv2.waitKey(-1)            

        # else:
        #     pass



    def iterate_operation_working_mask(self):


        """
        """
        ### RETURN VALUES
        assinged_work_operation_day_st_index = None
        assinged_work_operation_day_st_hr = None
        assinged_work_operation_day_end_index = None
        assinged_work_operation_day_end_hr = None


        current_day_index = self.startDayIndex
        dayGrayImg, mask_allowable_work, mask_allowable_delay = ScheduleAssigner.get_day_machine_sch_img(dayIndex=current_day_index, machineName=self.operationMachinName)
        start_working_hr = self.get_starting_hr_operation_working(mask_allowable_work)
        remaining_operation_img = self.operationGrayImg

        if start_working_hr == -1:
            ### Means no working hour available in that day
            current_day_index+=1
            ### Reset values
            remaining_operation_img = self.operationGrayImg
            start_working_hr = self.get_starting_hr_operation_working(mask_allowable_work)
        
        else:
            ### Try assigning the at start hr
            day_operation_working_indices = []            
            isOverlapPerfect, dayEndIndex, crop_op_startHr, cropEndHr, next_day_crop_gray = self.validate_and_crop_operation_for_next_day(remaining_operation_img, dayStartIndex=current_day_index, startHr=start_working_hr)
            day_operation_working_indices.append(dayEndIndex)
            while isOverlapPerfect==True:
                current_day_index = dayEndIndex+1
                isOverlapPerfect, dayEndIndex, crop_op_startHr, cropEndHr, next_day_crop_gray = self.validate_and_crop_operation_for_next_day(next_day_crop_gray, 

                        dayStartIndex=current_day_index, startHr=start_working_hr)


              



    def stretch_min_max_delay_working_mask(self):
        """"""
        pass


    
    

    def check_if_color_on_gray(self,work_subtracted_mask, assigned_day_operation_work_mask):
        """check if operation_work_mask overlapps on day_work_mask, if extra left, return end hr to crop
        return endHr (int) for next day cropping of operation else None"""

        whiteCount = np.sum(work_subtracted_mask==255)
        if whiteCount==0:
            ## work mask is perfectly overlapped
            cropEndHr = np.min(np.argwhere(assigned_day_operation_work_mask==255), axis=1)[1]
            isOverlapPerfect = True    
        else:
            cropEndHr = np.min(np.argwhere(work_subtracted_mask==255), axis=1)[1]
            # color is overlapping gray
            isOverlapPerfect = False


        return isOverlapPerfect, cropEndHr








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
        




