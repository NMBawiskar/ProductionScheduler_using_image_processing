import pandas as pd
from required_classes.dataGenerator import *


excel_path = r'input_data\Requirements_Data_edited.xlsx'


inputDataObj= InputDataGenerator(excelFilePath=excel_path)
inputDataObj.createAllMachineObjects()

print(inputDataObj.df_prod_req.head())
print("Total machine objects created : ",len(inputDataObj.machineObjectsList))

# print(inputDataObj.df_prod_req['OrderId'].filter(["C01"]))
inputDataObj.df_prod_req = inputDataObj.df_prod_req.set_index('OrderId')
print(inputDataObj.df_prod_req.index)
print(inputDataObj.df_prod_req)

print(inputDataObj.df_prod_req.loc["CO1"])
frameLength = len(inputDataObj.df_prod_req.loc["CO1"])
print()
order = Order_or_job(id="CO1")
for i in range(frameLength):
    dfLine = inputDataObj.df_prod_req.loc["CO1"].iloc[i] 
    order.create_and_add_operation(dfLine, inputDataObj.machineObjectsList)

order.getOrderImage()


print(order.operationSeq)

