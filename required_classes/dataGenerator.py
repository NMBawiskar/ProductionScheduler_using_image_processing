import pandas as pd
from required_classes.scheduler import *


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

    def createAllMachineObjects(self):
        """Create All machines objects"""
        machines_list = self.df_machine_sch['Machine'].tolist()
        uniqueMachinesList = set(machines_list)

        for machineName in uniqueMachinesList:
            m = Machine(machineName)
            self.machineObjectsList.append(m)


    def __getMachineObj(self, machineName):
        for machineObj in self.machineObjectsList:
            if machineObj.name == machineName:
                return machineObj
        
        return None
