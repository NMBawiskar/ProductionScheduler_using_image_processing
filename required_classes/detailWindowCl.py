import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QMainWindow, QStackedWidget, QWidget, QProgressBar, QDialog

from PyQt5.uic import loadUi
import os
from utils_pyqt5 import apply_img_to_label_object


class DetailWindow(QWidget):
    def __init__(self, mainUiObj):
        super().__init__()
        self.imgPath = None
                     
        loadUi(r'uiFiles\detailsWindow.ui',self)
        self.mainUiObj = mainUiObj


        self.comboBox_ord.addItems(self.mainUiObj.orderList)
        # self.comboBox_ord.addItems(["CO1","CO2","CO3"])
    
        self.comboBox_ord.currentIndexChanged.connect(self.show_img)
        self.show_img()

    def show_img(self):
        current_order = self.comboBox_ord.currentText()
        print("current_order",current_order)
        imgPath = os.path.join(self.mainUiObj.outputImgDir, f"{current_order}.png")
        if os.path.exists(imgPath):
            apply_img_to_label_object(imgPath, self.label_img_order)
        else:
            self.label_img_order.clear()