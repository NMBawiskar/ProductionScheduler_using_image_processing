from required_classes.prod_req import *

from required_classes.machine_sch import DaySlotMachine
from matplotlib import pyplot as plt 
import cv2
import numpy as np
import csv
import utils2
import os
import shutil


GRAY_GRAY = 50
BLACK_GRAY = 0
YELLOW_GRAY = 157
BLUE_GRAY = 29

YELLOW_PLUS_BLUE_GRAY = 186
GRAY_PLUS_BLUE_GRAY = 79
BLACK_PLUS_BLUE_GRAY = 29


class ScheduleAssigner:
    days_list = []
    outputImgDir = "orderImages"
    
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
        self.written_header = False
        self.create_dir()

    def create_dir(self):
        try:
            shutil.rmtree(self.outputImgDir)
        except:
            pass
        try:
            os.mkdir(self.outputImgDir)
        except Exception as e:
            pass

    
    def assign_order_operation_wise(self, order):
        """Main starter function to try assign all operation of an order"""

        total_days_to_check = len(DaySlotMachine.days_list)    
        result_all_operation_assigned = self.try_assigning_all_operations(order)
        while True:
            if result_all_operation_assigned==True:
                break
            else:
                first_operation = order.operationSeq[0]
                if first_operation.temp_assigned_st_day_index == total_days_to_check-1:
                    if first_operation.temp_assigned_st_hr_index == 23:
                        break
                try:
                    result_all_operation_assigned = self.restart_assigning_with_next_hour(order)
                except IndexError:
                    break
                
        
        if result_all_operation_assigned == True:
            order.isInfeasibleForProduction = False
            
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
                imgDaySlotAssigned = DaySlotMachine.get_display_day_machine_color_block(day, machineName)
                imgList.append(imgDaySlotAssigned)
                title_list.append(f"{self.days_list[day]}__{machineName}")
                    
            # utils2.plot_list_images(imgList, title_list)
            imgListOrder = []
            title_list_order = []
            machineList_unique = []
            for machineName in machineList:
                if machineName not in machineList_unique:
                    machineList_unique.append(machineName)
            ############## NEw display of order image #############
            for day in range(minDay, maxDay+1,1):
                for machineName in machineList_unique:
                    imgDaySlotAssigned = DaySlotMachine.get_display_day_machine_color_block(day, machineName)
                    imgListOrder.append(imgDaySlotAssigned)
                    title_list_order.append(f"{self.days_list[day]}__{machineName}")

            plotSavePath = os.path.join(self.outputImgDir, f"{order.id}.png")
            utils2.plot_list_images(imgListOrder, title_list_order, plotSavePath)   



            
        else:
            ## Mark order as not assignable
            order.isInfeasibleForProduction = True

        
        self.save_result_to_csv_file(order)
      
    def validate_if_prev_op_cycle_ends_at_day_end(self, prev_op_assignent_list, curr_op_assignment_list, prev_op_max_delay_hrs):
        
        prev_cycle_day_index, end_hr_prev_cycle = None, None
        curr_cycle_day_index, start_hr_curr_cycle = None, None
        
        new_prev_op_delay_stretched_list = []

        for op_assigned in prev_op_assignent_list[::-1]:
            day_index, st_hr, end_hr, type_cycle_delay = op_assigned
            if type_cycle_delay==0:
                prev_cycle_day_index, end_hr_prev_cycle = day_index, end_hr
                break

        for op_assigned in prev_op_assignent_list:
            day_index, st_hr, end_hr, type_cycle_delay = op_assigned
            if type_cycle_delay==0:
                new_prev_op_delay_stretched_list.append(op_assigned)
                
        
        for op_assigned in curr_op_assignment_list:
            day_index, st_hr, end_hr, type_cycle_delay = op_assigned
            if type_cycle_delay==0:
                curr_cycle_day_index, start_hr_curr_cycle = day_index, st_hr
                break
        
        if prev_cycle_day_index is not None and end_hr_prev_cycle is not None and \
            curr_cycle_day_index is not None and start_hr_curr_cycle is not None: 
        # if prev_cycle_day_index and  end_hr_prev_cycle and curr_cycle_day_index and start_hr_curr_cycle:
            hrs_to_elapse = 0
            delay_stretched_new_list = []
            if prev_cycle_day_index == curr_cycle_day_index:
                ## Same day start of next operation
                hrs_to_elapse = start_hr_curr_cycle - end_hr_prev_cycle
                delay_stretched_new_list.append([prev_cycle_day_index, end_hr_prev_cycle, start_hr_curr_cycle, 1])


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

        
        
        return False, []

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
        result_all_operation_assigned = self.try_assigning_all_operations(order, trial_start_day_index=next_trial_day_index, 
            trial_start_hr= next_trial_st_hr)


        return result_all_operation_assigned

    def __write_header_to_csv_file(self):
        try:
            f = open(self.output_file, 'a+',  newline="")
            csvWriter = csv.writer(f)
            header = ["Operation_name", "machine_name", "CycleTime(Hrs)", "MinDelay",	"MaxDelay", "Start_date", "start_time", "end_date", "end_time"]
            csvWriter.writerow(header)
            f.close()
        except Exception as e:
            print("Error in writing header to csv file",e)

    def save_result_to_csv_file(self, order):
        if self.written_header==False:
            print("writing header  to csv file")

            self.__write_header_to_csv_file()
            self.written_header = True
        print("saving result to csv file")

        f = open(self.output_file, 'a+',  newline="")
        csvWriter = csv.writer(f)
        
        for i, operation in enumerate(order.operationSeq):
            operation.freeze_operation_st_end_times(self.days_list)
            if order.isInfeasibleForProduction == False:

                csvWriter.writerow([operation.id, operation.machineReq.name, operation.cycleTimeHrs, operation.minDelayHrs, 
                    operation.maxDelayHrs, operation.operationStart_date, 
                    operation.operationStart_time, operation.operationEnd_date, operation.operationEnd_time])
            else:
                csvWriter.writerow([operation.id, operation.machineReq.name, operation.cycleTimeHrs, operation.minDelayHrs, 
                    operation.maxDelayHrs, "Not_feasible", 
                    "-", "-", "-"])


        f.close()
        print("saved result to csv file...")


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
                try:
                    endDelayDayIndex, endDelayHrIndex = first_operation.try_assigning_op_delay(endCycleDayIndex, endCycleHrIndex)
                except IndexError:
                    return False
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
                # self.restart_assigning_with_next_hour(order)
                return False
                

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
                        # self.restart_assigning_with_next_hour(order)
                        return False
                        
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
                    # self.restart_assigning_with_next_hour(order)
                    return False
                    



            print("All operations assignable :: ", first_operation_assigned_successfully and remaining_all_operation_assignable)
           
        return first_operation_assigned_successfully and remaining_all_operation_assignable

    @classmethod
    def get_day_machine_sch_img(self, dayIndex, machineName):        
        day = ScheduleAssigner.days_list[dayIndex]
        return DaySlotMachine.daySchedules[day][machineName]

  