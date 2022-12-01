import pandas as pd
from required_classes.dataGenerator import *
from required_classes.scheduler import ScheduleAssigner

excel_path = r'input_data\Requirements_Data_edited.xlsx'


inputDataObj= InputDataGenerator(excelFilePath=excel_path)
inputDataObj.createAllMachineObjects()

# print(inputDataObj.df_prod_req.head())


inputDataObj.createAllOrders()
print(len(Order_or_job.orderList))


inputDataObj.createAllDaySlots()


scheduleAssigner = ScheduleAssigner()
scheduleAssigner.assign_single_order(order=Order_or_job.orderList[0])