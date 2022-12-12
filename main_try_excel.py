import pandas as pd
from required_classes.dataGenerator import *
from required_classes.scheduler_new import ScheduleAssigner
import traceback

excel_path = r'input_data\Requirements_Data_edited.xlsx'


inputDataObj= InputDataGenerator(excelFilePath=excel_path)
inputDataObj.createAllMachineObjects()


# print(inputDataObj.df_prod_req.head())

daysList = inputDataObj.df_machine_sch['StartDate'].tolist()
inputDataObj.createAllOrders()

print(len(Order_or_job.orderList))


inputDataObj.createAllDaySlots()


dayList = list(DaySlotMachine.daySchedules.keys())
scheduleAssigner = ScheduleAssigner()
ScheduleAssigner.days_list = dayList
for orderToProcess in Order_or_job.orderList:
    try:
        # scheduleAssigner.assign_single_order(order=orderToProcess)
        scheduleAssigner.assign_order_operation_wise(order = orderToProcess)
        # if orderToProcess.isScheduleAssigned:
        #     orderToProcess.print_order_assigned_status()
    
    except Exception as e:
        print(traceback.print_exc())