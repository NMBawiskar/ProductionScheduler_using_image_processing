from required_classes.prod_req import *

from required_classes.machine_sch import DaySlotMachine
from matplotlib import pyplot as plt 
import cv2
import numpy as np
import csv
import utils2


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
        self.output_file = 'output.csv'

    # def assign_single_order(self, order):
        
    #     self.totalOrderImg = order.getTotalOrderImage()
    #     self.currentOrderObj = order
    #     machineSeq = [operation.machineReq.name for operation in order.operationSeq]
    #     n_machines = len(machineSeq)
    #     print('machineSeq',machineSeq)
    #     # showImg("totalOrderImg",self.totalOrderImg)


       
    #     allOpearationHrs = self.totalOrderImg.shape[1]
    #     opStartDateIndex = 0        
    #     totalDaysReq = int(allOpearationHrs / 8)+3
    #     daysScheduleImgList = [] 
    #     for day in ScheduleAssigner.days_list[opStartDateIndex:opStartDateIndex+totalDaysReq]:
    #         daySchedule = DaySlotMachine.daySchedules[day]
    #         machineDayImages = []
    #         for machine in machineSeq:
    #             if machine in daySchedule.keys():
    #                 dayScheduleReq = daySchedule[machine]
    #                 daySchImg = dayScheduleReq.get_day_working_img()
                    
    #                 machineDayImages.append(daySchImg)
    #                 # print("daySchImg.shape",daySchImg.shape)
    #         imgSingleDay = np.zeros((len(machineSeq), 8,3))
    #         # print("len(machineDayImages)",len(machineDayImages))
    #         for i, machineDayImg in enumerate(machineDayImages):                
    #             imgSingleDay[i:i+1, :] = machineDayImg
    #             # showImg('imgSingleDay',imgSingleDay)
    #             # cv2.waitKey(-1)
            
    #         daysScheduleImgList.append(imgSingleDay)
    #         # print("totalSingleDayImg.shape",imgSingleDay.shape)
    
    #     totaldayImage = np.hstack(tuple(daysScheduleImgList))
    #     # showImg("totaldayImage",totaldayImage)
    #     # print("totaldayImage.shape",totaldayImage.shape)
    #     # print("self.totalOrderImg.shape",self.totalOrderImg.shape)

    #     gray_order_img = cv2.cvtColor(self.totalOrderImg.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    #     gray_day_img = cv2.cvtColor(totaldayImage.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    #     # gray_order_img = cv2.cvtColor(self.totalOrderImg, cv2.COLOR_BGR2GRAY)

    #     # print("np.unique(gray_order_img)",np.unique(gray_order_img))
    #     # print("np.unique(gray_day_img)",np.unique(gray_day_img))

    #     added = totaldayImage.copy()
    #     stHr = 0
    #     isOrderAssignable = False
    #     machineWiseImgAssigned = []
    #     while isOrderAssignable==False:
    #         added[:,stHr:stHr+allOpearationHrs] = added[:,stHr:stHr+allOpearationHrs]+self.totalOrderImg
    #         gray_added = gray_day_img.copy()
    #         gray_added[:,stHr:stHr+allOpearationHrs] = gray_added[:,stHr:stHr+allOpearationHrs]+gray_order_img

    #         # print("np.unique(gray_added)",np.unique(gray_added))
    #         # showImg("convolutioned",added)
    #         # showImg("gray_added",gray_added)
    #         # showImg("gray_order_img",gray_order_img)
    #         # showImg("gray_day_img",gray_day_img)
            
    #         stacked_gray_added = self.break_days_combined_image(gray_added)
            
            


    #         stacked_st_days = stacked_gray_added[:, 0]
    #         stacked_end_days = stacked_gray_added[:, -1]
    #         # print("stacked_st_days",stacked_st_days)
    #         # print("stacked_end_days",stacked_end_days)
            
    #         if GRAY_PLUS_BLUE_GRAY not in stacked_st_days and  GRAY_PLUS_BLUE_GRAY not in stacked_end_days:
    #             isOrderAssignable = True
    #             for i, machine in enumerate(machineSeq):
    #                 machine_img_all_days = gray_added[i:i+1, :]
    #                 stacked_gray_machine = self.break_days_combined_image(machine_img_all_days)
    #                 machineWiseImgAssigned.append(stacked_gray_machine)
                    
    #             break
    #         stHr+=1




    #         cv2.waitKey(-1)

    #     if isOrderAssignable==True:
    #         assigned_values_list = [] # list of operation with values stDate, stHr, endDate, endHr

    #         for i, machineWiseImg in enumerate(machineWiseImgAssigned):
    #             showImg(f'machine {machineSeq[i]}',machineWiseImg)

    #             points = np.argwhere(machineWiseImg>BLACK_PLUS_BLUE_GRAY)
    #             # print(f"machine {machineSeq[i]}", points)
    #             minRow = np.min(points, axis=0)[0]
    #             maxRow = np.max(points, axis=0)[0]
    #             minRowValues =  points[points[:,0]==minRow]
    #             maxRowValues = points[points[:,0]==maxRow]
    #             stHrIndex = np.min(minRowValues,axis=0)[1]
    #             endHrIndex = np.max(maxRowValues, axis=0)[1]
                
    #             stDate, endDate = ScheduleAssigner.cycleTimeHrs[opStartDateIndex+minRow], ScheduleAssigner.cycleTimeHrs[opStartDateIndex+maxRow]
    #             stHr, endHr = 8 + stHrIndex, 8 + endHrIndex
    #             # print(f"minRow {minRow} stHr {stHrIndex} maxRow {maxRow} endHrIndex {endHrIndex}")
    #             print(f"stDate {stDate} stHr {stHr}  endDate {endDate} endHr {endHr}")
    #             assigningList = [stDate, stHr, endDate, endHr]
    #             assigned_values_list.append(assigningList)
    #             # print("minRowValues",minRowValues)
                
    #         order.assign_order(assigned_values_list)
    #         cv2.waitKey(-1)    

    # def break_days_combined_image(self, combinedImg):
    #     st = 0
    #     list_img_8hrs = []
    #     while True:
    #         end = st+8
    #         if st == combinedImg.shape[1]:
    #             break
    #         crop = combinedImg[:, st:end]
    #         list_img_8hrs.append(crop)
    #         st = end
        
    #     vstacked = np.vstack(list_img_8hrs)
        
    #     return vstacked

    def assign_order_operation_wise(self, order):
        """Main starter function to try assign all operation of an order"""
        
        result_all_operation_assigned = self.try_assigning_all_operations(order)
        if result_all_operation_assigned == True:
            
            dict_machine_name_data_assignment = {}
            
            for operation in order.operationSeq:
                machineName = operation.machineReq.name
                print(f"operation {operation.id} list_details {operation.day_st_end_assigned_list}")
                dict_machine_name_data_assignment[machineName] = operation.day_st_end_assigned_list

            DaySlotMachine.assignMachineHrs_for_order(dict_machine_name_data_assignment=dict_machine_name_data_assignment)


            day_index_machine_list = []
            for machineName, list_data_to_assign in dict_machine_name_data_assignment.items():
                for data_to_assign in list_data_to_assign:
                    dayIndex, stHrIndex, endHrIndex, cycle_or_delay = data_to_assign
                    if [dayIndex, machineName] not in day_index_machine_list:
                        day_index_machine_list.append([dayIndex, machineName])

            

            daysList = [item[0] for item in day_index_machine_list]
            machineList = [item[1] for item in day_index_machine_list]
            minDay, maxDay = min(daysList), max(daysList)
            dayList_machineName_to_display = []
            lastMachineName = None
            for day in range(minDay, maxDay+1,1):
                if day not in daysList and lastMachineName is not None:
                    dayList_machineName_to_display.append([day, lastMachineName])
                
                else:
                    machineName = machineList[daysList.index(day)]
                    dayList_machineName_to_display.append([day, machineName])
                    lastMachineName = machineName


            
            imgList = []
            title_list = []
            for day, machineName in dayList_machineName_to_display:
                imgDaySlotAssigned = DaySlotMachine.get_display_day_machine_color_block(dayIndex, machineName)
                imgList.append(imgDaySlotAssigned)
                title_list.append(f"{self.days_list[day]}__{machineName}")
                    
            utils2.plot_list_images(imgList, title_list)
           
            
            
        else:
            ## Mark order as not assignable
            pass
      
    def validate_if_prev_op_cycle_ends_at_day_end(self, prev_op_assignent_list, curr_op_assignment_list, prev_op_max_delay_hrs):
        
        prev_cycle_day_index, end_hr_prev_cycle = None, None
        curr_cycle_day_index, start_hr_curr_cycle = None, None
        
        new_prev_op_delay_stretched_list = []

        for op_assigned in prev_op_assignent_list[::-1]:
            day_index, st_hr, end_hr, type_cycle_delay = op_assigned
            if type_cycle_delay==0:
                prev_cycle_day_index, end_hr_prev_cycle = day_index, end_hr
                break

        for op_assigned in prev_op_assignent_list[::-1]:
            day_index, st_hr, end_hr, type_cycle_delay = op_assigned
            if type_cycle_delay==0:
                new_prev_op_delay_stretched_list.append(op_assigned)
                
        
        for op_assigned in curr_op_assignment_list:
            day_index, st_hr, end_hr, type_cycle_delay = op_assigned
            if type_cycle_delay==0:
                curr_cycle_day_index, start_hr_curr_cycle = day_index, st_hr
                break
        

        if prev_cycle_day_index and  end_hr_prev_cycle and curr_cycle_day_index and start_hr_curr_cycle:
            hrs_to_elapse = 0
            delay_stretched_new_list = []
            if prev_cycle_day_index == curr_cycle_day_index:
                ## Same day start of next operation
                hrs_to_elapse = start_hr_curr_cycle - end_hr_prev_cycle
                delay_stretched_new_list.append([prev_cycle_day_index, start_hr_curr_cycle, end_hr_prev_cycle, 1])


            else:
                ## Next day start of next operation
                for day_index in range(prev_cycle_day_index, curr_cycle_day_index+1):
                    if day_index==prev_cycle_day_index:
                        hrs_to_accomodate = 24 - end_hr_prev_cycle
                        list_delay_to_add = [day_index, end_hr_prev_cycle, 24, 1]
                    elif day_index==curr_cycle_day_index:
                        hrs_to_accomodate = start_hr_curr_cycle - 1
                        list_delay_to_add = [day_index, 0, start_hr_curr_cycle, 1]
                    else:
                        hrs_to_accomodate = 24
                        list_delay_to_add = [day_index, 0, 24, 1]
                    hrs_to_elapse+= hrs_to_accomodate 
                    delay_stretched_new_list.append(list_delay_to_add)           

            if hrs_to_elapse >1:
                ### Check if prev_operation_max_delay can accomodate this
                if hrs_to_elapse<= prev_op_max_delay_hrs:
                    ## OK can go further
                    ## create new_list_of prev operation
                    
                    new_prev_op_delay_stretched_list.extend(delay_stretched_new_list)
                    return True, new_prev_op_delay_stretched_list
                else:
                    return False, []
            else:
                ## no time gap 
                return True, prev_op_assignent_list



    def restart_assigning_with_next_hour(self, order):

        n_operations = len(order.operationSeq)
        first_operation = order.operationSeq[0]
        for i in range(n_operations):
            operation = order.operationSeq[i]
            ### Reset all day assignment list 
            operation.day_st_end_assigned_list = []

        if first_operation.temp_assigned_st_hr_index==23:
            next_trial_st_hr =  0
            next_trial_day_index = first_operation.temp_assigned_st_day_index + 1

        else:
            next_trial_st_hr = first_operation.temp_assigned_st_hr_index + 1
            next_trial_day_index = first_operation.temp_assigned_st_day_index

        print(f"PREVIOUS trial of start day {first_operation.temp_assigned_st_day_index} and hr {first_operation.temp_assigned_st_hr_index} not feasible")
        print(f"TRYING NEXT trial for start day {next_trial_day_index} and hr {next_trial_st_hr} ")
        self.try_assigning_all_operations(order, trial_start_day_index=next_trial_day_index, 
            trial_start_hr= next_trial_st_hr )


    def try_assigning_all_operations(self, order, trial_start_hr=0, trial_start_day_index=0):

        ### 1. Get first/next operation, its machine name, start day and start hour 
        ### 2. get corresponding machine daySlot
        ### 3. Try assigning 
        ### 4. If assigned return current operation end Hr and end dayIndex, take next operation at End hour and end day of prev operation
        ### Repeat the process above
        
        ### Make CycleAssignerValidator list empty
        # make_cycle_assigner_list_empty()

        n_operations = len(order.operationSeq)
        first_operation_assigned_successfully = True
        remaining_all_operation_assignable = True
        ### 1. Get firstoperation, set its temp start day and start hour 
        first_operation_index = 0
        first_operation = order.operationSeq[first_operation_index]
        
        
        # trial_start_hr = 0
        # trial_start_day_index = 0
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
                    # first_operation.temp_assigned_end_hr_index += self.increment
                    first_operation_assigned_successfully = False


            else:
                ### no min max delay
                endDelayDayIndex, endDelayHrIndex = endCycleDayIndex, endCycleHrIndex
                first_operation.temp_assigned_end_day_index, first_operation.temp_assigned_end_hr_index = endDelayDayIndex, endDelayHrIndex

        if first_operation_assigned_successfully ==True:
            first_operation.day_st_end_assigned_list.extend(first_operation.delay_detail_list)
            print("FIRST operation temporary assignment details :")
            print(f"""Operation ID {first_operation.id} : Machine {first_operation.machineReq.name} 
            START {ScheduleAssigner.days_list[first_operation.temp_assigned_st_day_index]} 
            - {first_operation.temp_assigned_st_hr_index} hrs, END {ScheduleAssigner.days_list[first_operation.temp_assigned_end_day_index]} 
            - {first_operation.temp_assigned_end_hr_index} hrs
            """)
        #### once done first operation
        # next_operations are directly assigned and checked for validations
        if first_operation_assigned_successfully==False:
            ## restart the operation
            if first_operation.temp_assigned_st_day_index is not None:
                self.restart_assigning_with_next_hour(order)
                # print(f"PREVIOUS trial of start day {first_operation.temp_assigned_st_day_index} and hr {first_operation.temp_assigned_st_hr_index} not feasible")
                # next_trial =  first_operation.temp_assigned_st_hr_index + 1
                # print(f"TRYING NEXT trial for start day {first_operation.temp_assigned_st_day_index} and hr {next_trial} ")

                # self.try_assigning_all_operations(order, trial_start_day_index= first_operation.temp_assigned_st_day_index, trial_start_hr=next_trial )

        else:
            ### Try assigning next operations    


            prev_op_end_day_index = first_operation.temp_assigned_end_day_index
            prev_op_end_hr_index = first_operation.temp_assigned_end_hr_index

            for i in range(1,n_operations):
                print("Trying to set next operation")
                next_operation = order.operationSeq[i]
                print(next_operation)
                endCycleDayIndex, endCycleHrIndex = next_operation.try_assigning_op_cycle(prev_op_end_day_index, prev_op_end_hr_index, isFirstOrder=False)

                if endCycleDayIndex is not None:
                    ### Check if previous operation cycle part ends at day end and it has delay to accomodate all hours within
                    prev_operation = order.operationSeq[i-1]
                    prev_operation_cycle_end_time = prev_operation.day_st_end_assigned_list
                    print("prev_operation_cycle_end_time",prev_operation_cycle_end_time)

                    result_validation, new_prev_order_assignment_list = self.validate_if_prev_op_cycle_ends_at_day_end(prev_operation_cycle_end_time, curr_op_assignment_list=next_operation.day_st_end_assigned_list,
                        prev_op_max_delay_hrs= prev_operation.maxDelayHrs)

                    if result_validation==True:
                        order.operationSeq[i-1].day_st_end_assigned_list = new_prev_order_assignment_list
                        
                    else:
                        ### Not assigned next opearation
                        remaining_all_operation_assignable = False
                        self.restart_assigning_with_next_hour(order)
                        # first_operation.day_st_end_assigned_list = []
                        # next_operation.day_st_end_assigned_list = []
                        # print(f"PREVIOUS trial of start day {first_operation.temp_assigned_st_day_index} and hr {first_operation.temp_assigned_st_hr_index} not feasible")
                        # next_trial =  first_operation.temp_assigned_st_hr_index + 1
                        # print(f"TRYING NEXT trial for start day {first_operation.temp_assigned_st_day_index} and hr {next_trial} ")
                        # self.try_assigning_all_operations(order, trial_start_day_index= first_operation.temp_assigned_st_day_index, trial_start_hr=next_trial )


                    ## if delay hrs in operation
                    if next_operation.maxDelayHrs>0:
                        ### try assigning delay hrs
                        endDelayDayIndex, endDelayHrIndex = next_operation.try_assigning_op_delay(endCycleDayIndex, endCycleHrIndex)
                        next_operation.temp_assigned_end_day_index, next_operation.temp_assigned_end_hr_index = endDelayDayIndex, endDelayHrIndex
                        if endDelayDayIndex is None:
                            #### Operation not assignable 
                            ### Increment and restart the process 
                            # next_operation.temp_assigned_end_hr_index += self.increment
                            # restart complete operation using
                            remaining_all_operation_assignable = False
                            break
                        else:
                            #assignable 
                            # extend delay st end details list
                              
                            next_operation.day_st_end_assigned_list.extend(next_operation.delay_detail_list)


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

                else:
                    ### Not assigned next opearation
                    remaining_all_operation_assignable = False
                    self.restart_assigning_with_next_hour(order)
                    # first_operation.day_st_end_assigned_list = []
                    # next_operation.day_st_end_assigned_list = []
                    # print(f"PREVIOUS trial of start day {first_operation.temp_assigned_st_day_index} and hr {first_operation.temp_assigned_st_hr_index} not feasible")
                    # next_trial =  first_operation.temp_assigned_st_hr_index + 1
                    # print(f"TRYING NEXT trial for start day {first_operation.temp_assigned_st_day_index} and hr {next_trial} ")
                    # self.try_assigning_all_operations(order, trial_start_day_index= first_operation.temp_assigned_st_day_index, trial_start_hr=next_trial )




            print("All operations assignable :: ", remaining_all_operation_assignable)
            f = open(self.output_file, 'a+',  newline="")
            csvWriter = csv.writer(f)
            header = ["Operation_name", "machine_name", "CycleTime(Hrs)", "MinDelay",	"MaxDelay", "Start_date", "start_time", "end_date", "end_time"]
            csvWriter.writerow(header)
            if remaining_all_operation_assignable==True:
                for i, operation in enumerate(order.operationSeq):
                    operation.freeze_operation_st_end_times(self.days_list)

                    csvWriter.writerow([operation.id, operation.machineReq.name, operation.cycleTimeHrs, operation.minDelayHrs, 
                        operation.maxDelayHrs, operation.operationStart_date, 
                        operation.operationStart_time, operation.operationEnd_date, operation.operationEnd_time])

                
            else:
                ## restart the operation
                if first_operation.temp_assigned_st_day_index is not None:
                    self.restart_assigning_with_next_hour(order)
                    # print(f"PREVIOUS trial of start day {first_operation.temp_assigned_st_day_index} and hr {first_operation.temp_assigned_st_hr_index} not feasible")
                    # next_trial =  first_operation.temp_assigned_st_hr_index + 1
                    # print(f"TRYING NEXT trial for start day {first_operation.temp_assigned_st_day_index} and hr {next_trial} ")

                    # self.try_assigning_all_operations(order, trial_start_day_index= first_operation.temp_assigned_st_day_index, trial_start_hr=next_trial )
            
            f.close()

        return remaining_all_operation_assignable

    @classmethod
    def get_day_machine_sch_img(self, dayIndex, machineName):
        day = ScheduleAssigner.days_list[dayIndex]
        return DaySlotMachine.daySchedules[day][machineName]

  
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

    def iterate_operation_working_mask(self):


        """            """
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
        

