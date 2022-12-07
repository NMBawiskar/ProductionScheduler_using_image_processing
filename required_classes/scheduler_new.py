from required_classes.prod_req import *
from required_classes.machine_sch import *

from utils import showImg
import cv2
import numpy as np

GRAY_GRAY = 50
BLACK_GRAY = 0
YELLOW_GRAY = 157
BLUE_GRAY = 29

YELLOW_PLUS_BLUE_GRAY = 186
GRAY_PLUS_BLUE_GRAY = 79
BLACK_PLUS_BLUE_GRAY = 29


class ScheduleAssigner:
    def __init__(self):
        self.current_weekImg = None
        self.current_weekNo = 0
    
        self.orderImg = None
        self.orderImgList = []
        self.currentOrderObj = None

        self.hWeek, self.wWeek = None, None
        self.hOrder, self.wOrder = None, None

        self.days_list = []

    def assign_single_order(self, order:Order_or_job):
        
        self.totalOrderImg = order.getTotalOrderImage()
        self.currentOrderObj = order
        machineSeq = [operation.machineReq.name for operation in order.operationSeq]
        n_machines = len(machineSeq)
        print('machineSeq',machineSeq)
        showImg("totalOrderImg",self.totalOrderImg)


        dayList = list(DaySlotMachine.daySchedules.keys())
        allOpearationHrs = self.totalOrderImg.shape[1]
        opStartDateIndex = 0        
        totalDaysReq = int(allOpearationHrs / 8)+3
        daysScheduleImgList = [] 
        for day in dayList[opStartDateIndex:opStartDateIndex+totalDaysReq]:
            daySchedule = DaySlotMachine.daySchedules[day]
            machineDayImages = []
            for machine in machineSeq:
                if machine in daySchedule.keys():
                    dayScheduleReq = daySchedule[machine]
                    daySchImg = dayScheduleReq.get_day_working_img()
                    # showImg("daySchImg",daySchImg)
                    # cv2.waitKey(-1)
                    machineDayImages.append(daySchImg)
                    # print("daySchImg.shape",daySchImg.shape)
            imgSingleDay = np.zeros((len(machineSeq), 8,3))
            # print("len(machineDayImages)",len(machineDayImages))
            for i, machineDayImg in enumerate(machineDayImages):                
                imgSingleDay[i:i+1, :] = machineDayImg
                # showImg('imgSingleDay',imgSingleDay)
                # cv2.waitKey(-1)
            
            daysScheduleImgList.append(imgSingleDay)
            # print("totalSingleDayImg.shape",imgSingleDay.shape)
    
        totaldayImage = np.hstack(tuple(daysScheduleImgList))
        showImg("totaldayImage",totaldayImage)
        # print("totaldayImage.shape",totaldayImage.shape)
        # print("self.totalOrderImg.shape",self.totalOrderImg.shape)

        gray_order_img = cv2.cvtColor(self.totalOrderImg.astype(np.uint8), cv2.COLOR_BGR2GRAY)
        gray_day_img = cv2.cvtColor(totaldayImage.astype(np.uint8), cv2.COLOR_BGR2GRAY)
        # gray_order_img = cv2.cvtColor(self.totalOrderImg, cv2.COLOR_BGR2GRAY)

        # print("np.unique(gray_order_img)",np.unique(gray_order_img))
        # print("np.unique(gray_day_img)",np.unique(gray_day_img))

        added = totaldayImage.copy()
        stHr = 0
        isOrderAssignable = False
        machineWiseImgAssigned = []
        while isOrderAssignable==False:
            added[:,stHr:stHr+allOpearationHrs] = added[:,stHr:stHr+allOpearationHrs]+self.totalOrderImg
            gray_added = gray_day_img.copy()
            gray_added[:,stHr:stHr+allOpearationHrs] = gray_added[:,stHr:stHr+allOpearationHrs]+gray_order_img

            # print("np.unique(gray_added)",np.unique(gray_added))
            showImg("convolutioned",added)
            showImg("gray_added",gray_added)
            showImg("gray_order_img",gray_order_img)
            showImg("gray_day_img",gray_day_img)
            
            stacked_gray_added = self.break_days_combined_image(gray_added)
            
            


            stacked_st_days = stacked_gray_added[:, 0]
            stacked_end_days = stacked_gray_added[:, -1]
            # print("stacked_st_days",stacked_st_days)
            # print("stacked_end_days",stacked_end_days)
            
            if GRAY_PLUS_BLUE_GRAY not in stacked_st_days and  GRAY_PLUS_BLUE_GRAY not in stacked_end_days:
                isOrderAssignable = True
                for i, machine in enumerate(machineSeq):
                    machine_img_all_days = gray_added[i:i+1, :]
                    stacked_gray_machine = self.break_days_combined_image(machine_img_all_days)
                    machineWiseImgAssigned.append(stacked_gray_machine)
                    
                break
            stHr+=1




            cv2.waitKey(-1)



        if isOrderAssignable==True:
            assigned_values_list = [] # list of operation with values stDate, stHr, endDate, endHr

            for i, machineWiseImg in enumerate(machineWiseImgAssigned):
                showImg(f'machine {machineSeq[i]}',machineWiseImg)

                points = np.argwhere(machineWiseImg>BLACK_PLUS_BLUE_GRAY)
                # print(f"machine {machineSeq[i]}", points)
                minRow = np.min(points, axis=0)[0]
                maxRow = np.max(points, axis=0)[0]
                minRowValues =  points[points[:,0]==minRow]
                maxRowValues = points[points[:,0]==maxRow]
                stHrIndex = np.min(minRowValues,axis=0)[1]
                endHrIndex = np.max(maxRowValues, axis=0)[1]
                
                stDate, endDate = dayList[opStartDateIndex+minRow], dayList[opStartDateIndex+maxRow]
                stHr, endHr = 8 + stHrIndex, 8 + endHrIndex
                print(f"minRow {minRow} stHr {stHrIndex} maxRow {maxRow} endHrIndex {endHrIndex}")
                print(f"stDate {stDate} stHr {stHr}  endDate {endDate} endHr {endHr}")
                assigningList = [stDate, stHr, endDate, endHr]
                assigned_values_list.append(assigningList)
                # print("minRowValues",minRowValues)
                
            order.assign_order(assigned_values_list)
            cv2.waitKey(-1)    
            

    def break_days_combined_image(self, combinedImg):
        st = 0
        list_img_8hrs = []
        while True:
            end = st+8
            if st == combinedImg.shape[1]:
                break
            crop = combinedImg[:, st:end]
            list_img_8hrs.append(crop)
            st = end
        
        vstacked = np.vstack(list_img_8hrs)
        
        return vstacked

