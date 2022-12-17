import pandas as pd
from required_classes.machine_sch import *
from required_classes.prod_req import Order_or_job
from datetime import datetime


class InputDataGenerator:
    def __init__(self, excelFilePath):
        self.excelFilePath = excelFilePath

        self.df_machine_sch = None
        self.df_prod_req = None
        
        self.machineObjectsList = []
        self.get_dataFrames()

    def get_dataFrames(self):
        xls = pd.ExcelFile(self.excelFilePath)
        self.df_machine_sch = pd.read_excel(xls, sheet_name="MachineAvailability")
        self.df_prod_req = pd.read_excel(xls, sheet_name="ProductionRequirement")

        self.df_machine_sch['StartDate'] = self.df_machine_sch['StartDate'].astype(str)
        self.df_machine_sch['EndDate'] = self.df_machine_sch['EndDate'].astype(str)

        self.df_machine_sch['day_st_time'] = self.df_machine_sch['StartDate'].astype(str) + "__" + self.df_machine_sch['StartTime'].astype(str)
        self.df_machine_sch['day_end_time'] = self.df_machine_sch['EndDate'].astype(str) + "__" + self.df_machine_sch['EndTime'].astype(str)



    def createAllMachineObjects(self):
        """Create All machines objects"""
        machines_list = self.df_machine_sch['Machine'].tolist()
        uniqueMachinesList = set(machines_list)

        for machineName in uniqueMachinesList:
            m = Machine(machineName)
            self.machineObjectsList.append(m)


    def __getMachineObj(self, machineName):
        if machineName in Machine.dict_machine_name.keys():

            return Machine.dict_machine_name[machineName]
        else:
            return None

    def createAllOrders(self):
        
        # print("self.df_prod_req",self.df_prod_req)
        list_orderNames = list(set(self.df_prod_req['OrderId'])) 

        self.df_prod_req = self.df_prod_req.set_index('OrderId')
        for orderName in list_orderNames:
            # print(self.df_prod_req.loc[orderName])
            frameLength = len(self.df_prod_req.loc[orderName])
            print()
            order = Order_or_job(id=orderName)
            for i in range(frameLength):
                dfLine = self.df_prod_req.loc[orderName].iloc[i] 
                order.create_and_add_operation(dfLine, self.machineObjectsList)

            order.save_order()


    def createAllDaySlots(self):
        print(self.df_machine_sch.head())
       
        self.df_machine_sch.reset_index()
        
        for index, row in self.df_machine_sch.iterrows():
            # print(row['day_st_time'], row['day_end_time'])
            if "XXX" in row['day_st_time'] or "XXX" in row['day_end_time']:
                stTime = None
                endTime = None
                day = datetime.strptime(row['StartDate'],"%Y-%m-%d")
        
            else:
                
                stTime = datetime.strptime(row['day_st_time'] ,"%Y-%m-%d__%H:%M:%S")
                endTime =datetime.strptime(row['day_end_time'],"%Y-%m-%d__%H:%M:%S")
                # weekNo = stTime.isocalendar()[1]
                
                day = stTime.date()

            machineObj = self.__getMachineObj(row['Machine'])
            if machineObj is not None:
                daySlotMachine = DaySlotMachine(day=day,machine=machineObj)
                if stTime is not None:
                    daySlotMachine.setInitialDayAvailability(stTime.hour, endTime.hour)
                else:
                    daySlotMachine.assign_weekend_day()
    