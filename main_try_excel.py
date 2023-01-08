import pandas as pd
from required_classes.dataGenerator import InputDataGenerator
from required_classes.scheduler_new import ScheduleAssigner
from required_classes.prod_req import *
from required_classes.machine_sch import *
import traceback
from utils2 import get_output_csv_file_path

# excel_path = r'input_data\NewData_121822.xlsx'
excel_path = r'input_data\NewData_121822 - New.xlsx'

inputDataObj= InputDataGenerator(excelFilePath=excel_path)
inputDataObj.createAllMachineObjects()

daysList = inputDataObj.df_machine_sch['StartDate'].tolist()
inputDataObj.createAllOrders()

print(len(Order_or_job.orderList))


inputDataObj.createAllDaySlots()


dayList = list(DaySlotMachine.daySchedules.keys())
scheduleAssigner = ScheduleAssigner()

outputCsvFilePath = get_output_csv_file_path(excel_path)

print("outputCsvFilePath",outputCsvFilePath)
scheduleAssigner.output_file = outputCsvFilePath
ScheduleAssigner.days_list = dayList
DaySlotMachine.days_list = dayList




for orderToProcess in Order_or_job.orderList:
    try:
        # scheduleAssigner.assign_single_order(order=orderToProcess)
        scheduleAssigner.assign_order_operation_wise(order = orderToProcess)
        # if orderToProcess.isScheduleAssigned:
        #     orderToProcess.print_order_assigned_status()
    
    except Exception as e:
        print(traceback.print_exc())

