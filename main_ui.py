from PyQt5 import QtWidgets, QtMultimedia, QtCore,QtGui
from PyQt5.QtGui import QImage, QPixmap
import sys
import utils_pyqt5 as ut
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QFileDialog,  QInputDialog, QMainWindow, QStackedWidget, QWidget, QProgressBar, QDialog
import os
import pandas as pd
from required_classes.dataGenerator import InputDataGenerator
from required_classes.scheduler_new import ScheduleAssigner
from required_classes.prod_req import *
from required_classes.machine_sch import *
import traceback
from utils2 import get_output_csv_file_path
import csv
from required_classes.detailWindowCl import DetailWindow
from PyQt5.QtWidgets import * 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
             
        loadUi(r'uiFiles\mainUI.ui',self)
        
        self.input_excel_path = ""
        
        
        self.btn_browse.clicked.connect(self.selectFile)
        self.btn_start.clicked.connect(self.start_assigning)
        self.btn_details.clicked.connect(self.toDetailsWindow)

        self.outputImgDir = "orderImages"
        self.orderList = []
        # self.show_table_details(r'input_data\assigned_NewData_121822.csv')
        
    def selectFile(self):

        qWid = QWidget()
        print("file browse")
        path_file,_ = QFileDialog.getOpenFileName(qWid, 'Open a file', '','Excel Files (*.xlsx)')        
        self.textEdit_file_path.setPlainText(path_file)
        self.input_excel_path = path_file


    def toDetailsWindow(self):
        detailsWindow = DetailWindow(self)
        self.window = detailsWindow
        self.window.show()


    def show_table_details(self, filePathCsv):
        # csvFilePath = r'input_data\assigned_Requirements_Data_edited.csv'
        
        dataRows = []
        with open(filePathCsv, 'r') as f:
            csvReader = csv.reader(f)
            header = next(csvReader)
            print("header",header)
            dataRows.append(header)
            for row in csvReader:
                print('row',row)
                dataRows.append(row)
          
        
        print("dataRows",dataRows)

        self.tableWidgetResult.setColumnCount(9)
        self.tableWidgetResult.setRowCount(len(dataRows))
        for rowNo, dataRow in enumerate(dataRows):
            for colNo, text_ in enumerate(dataRow):
                item_ = QtWidgets.QTableWidgetItem(text_)
                self.tableWidgetResult.setItem(rowNo, colNo, item_)

                self.tableWidgetResult.horizontalHeader().setStretchLastSection(True)
                self.tableWidgetResult.horizontalHeader().setSectionResizeMode(
                    QHeaderView.Stretch)


    def start_assigning(self):
        if os.path.exists(self.input_excel_path):
            inputDataObj= InputDataGenerator(excelFilePath=self.input_excel_path)
            inputDataObj.createAllMachineObjects()

            daysList = inputDataObj.df_machine_sch['StartDate'].tolist()
            inputDataObj.createAllOrders()

            print(len(Order_or_job.orderList))
            self.orderList = [obj.id for obj  in Order_or_job.orderList]

            inputDataObj.createAllDaySlots()


            dayList = list(DaySlotMachine.daySchedules.keys())
            scheduleAssigner = ScheduleAssigner()

            outputCsvFilePath = get_output_csv_file_path(self.input_excel_path)
            scheduleAssigner.output_file = outputCsvFilePath
            try:
                os.remove(scheduleAssigner.output_file)  
            except:
                pass
            ScheduleAssigner.days_list = dayList
            ScheduleAssigner.outputImgDir = self.outputImgDir

            DaySlotMachine.days_list = dayList

            for orderToProcess in Order_or_job.orderList:
                try:
                    scheduleAssigner.assign_order_operation_wise(order = orderToProcess)
                
                except Exception as e:
                    print(traceback.print_exc())

            self.show_table_details(scheduleAssigner.output_file)
            ### Add result to table widget

            self.model = QtGui.QStandardItemModel(self)

            self.tableView = QtWidgets.QTableView(self)
            self.tableView.horizontalHeader().setStretchLastSection(True)

            with open(outputCsvFilePath, "r") as fileInput:
                for row in csv.reader(fileInput):    
                    items = [QtGui.QStandardItem(field) for field in row]
                    print(items)
                    self.model.appendRow(items)

            self.tableView.setModel(self.model)
            





    def is_valid(self):
        if self.textEdit_fileNames.toPlainText() != '':
            return True
        else:
            return False

       
       
    def debug_start(self):
        self.label.clear()
        self.textEdit.clear()
        self.label.setText("Please enter the employee name.") 
        self.resrt = True

 
          
    def displayImage(self, uiObj, img):
        qformat = QImage.Format_BGR888
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        uiObj.setPixmap(QPixmap.fromImage(img))

    def close_win(self):
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w.setWindowTitle("Registration window")
    # w.setWindowIcon(QtGui.QIcon(r'resources/QuicSolv-Fevicon.png'))
    sys.exit(app.exec())
    