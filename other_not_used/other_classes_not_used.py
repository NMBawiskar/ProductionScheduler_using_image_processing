
# class AssignerSingleOperation:
#     """Class i) to iterate over each hour and 
#         ii) place the operation image over day/days schedule image
#         iii) validate rules
#         iv) return the final, start_daytime, end_daytime, delayHours used"""

#     def __init__(self, startDayIndex, stHrIndex, operationGrayImg, operationMachinName):
#         self.startDayIndex = startDayIndex
#         self.stHrIndex = stHrIndex
#         self.operationGrayImg = operationGrayImg
        
#         self.operationMachinName = operationMachinName
        
#         self.list_day_oper_crop_images = []
#         self.list_day_images = []

#     def get_operation_img_day_mask(self):
        


#         list_day_oper_crop_images = []  ## List containing list of  [dayImg, corr.operation crop img]
#         width_op_img = self.operationGrayImg.shape[1]
#         current_day_index = self.startDayIndex 
        
#         for i in range(10): # 10 days
            
#             dayGrayImg, mask_allowable_work, mask_allowable_delay, mask_assigned_hrs = ScheduleAssigner.get_day_machine_sch_img(dayIndex=current_day_index, machineName=self.operationMachinName)
#             start_working_hr = self.get_starting_hr_operation_working(mask_allowable_work)

#             if start_working_hr == -1:
#                 ### Means no working hour available in that day
#                 current_day_index+=1
#             else:
#                 ### Try assigning the at start hr
#                 remaining_operation_img = self.operationGrayImg
                
#                 self.validate_and_crop_operation_for_next_day(remaining_operation_img, dayStartIndex=current_day_index, startHr=start_working_hr)

              

#             print("start_working hour", start_working_hr)


#             # showImg('dayGrayImg',dayGrayImg)
#             # showImg('mask_allowable_work',mask_allowable_work)
#             # showImg('mask_allowable_delay',mask_allowable_delay)
#             # cv2.waitKey(-1)
#             print('sch')
     

#     def get_starting_hr_operation_working(self, mask_allowable_work):

#         if mask_allowable_work.size==0:
#             min_x = 1
#         else:
#             coordinates = np.argwhere(mask_allowable_work==255)
#             if coordinates.size==0:
#                 min_x=-1
#                 print("No whites found means no working hours available in the day")
#             else:
#                 min_values = np.min(np.argwhere(mask_allowable_work==255), axis=0)
#                 if len(min_values.shape) == 0:
#                     print("No whites found means no working hours available in the day")
#                     min_x = -1
#                 else:    
#                     min_x = min_values[1]
#                     print('min start working hr ', min_x)

#         return min_x

#     def validate_and_crop_operation_for_next_day(self, remaining_operation_gray_img, dayStartIndex, startHr):
#         """Function validate rule of assigning and returns operationAssigned, stHr, endHr, 
#             and Remaining cropped image for next day assignment"""

#         dayGrayImg, mask_allowable_work, mask_allowable_delay, mask_assigned_hrs = ScheduleAssigner.get_day_machine_sch_img(dayIndex=dayStartIndex, 
#                             machineName=self.operationMachinName)
        
        
#         mask_operation_work, mask_operation_delay = utils.get_operation_work_and_delay_masks(remaining_operation_gray_img)

#         assigned_day_operation_work_mask = np.zeros_like(dayGrayImg)
#         assigned_day_operation_delay_mask = np.zeros_like(dayGrayImg)
#         width_operation_remaining = remaining_operation_gray_img.shape[1]
#         endHr = startHr + width_operation_remaining

#         if endHr <= dayGrayImg.shape[1]:
#             assigned_day_operation_delay_mask[:,startHr:endHr] = mask_operation_delay
#             assigned_day_operation_work_mask[:,startHr:endHr] = mask_operation_work

#             stacked_delay_mask = np.vstack((mask_allowable_delay,assigned_day_operation_delay_mask))
#             stacked_work_mask = np.vstack((mask_allowable_work,assigned_day_operation_work_mask))
            
#             work_subtracted_mask = assigned_day_operation_work_mask - mask_allowable_work
#             isOverlapPerfect, cropEndHr = self.check_if_color_on_gray(work_subtracted_mask, assigned_day_operation_work_mask)
#             if isOverlapPerfect==True:
#                 #if color fits perfectly, start putting delay after that
#                 EndHrOperation_working = cropEndHr
#                 next_day_crop_gray = None
#                 return isOverlapPerfect, dayStartIndex, startHr, endHr, next_day_crop_gray
                
#             else:
#                 next_day_crop_mask_total = assigned_day_operation_work_mask[:, cropEndHr:]
#                 hrs_remaining_for_next_day = np.sum(next_day_crop_mask_total==255)
#                 next_day_crop_gray = remaining_operation_gray_img[:,width_operation_remaining-hrs_remaining_for_next_day:]
#                 return isOverlapPerfect, dayStartIndex, startHr, cropEndHr, next_day_crop_gray

#     def iterate_operation_working_mask(self):


#         """            """
#         ### RETURN VALUES
#         assinged_work_operation_day_st_index = None
#         assinged_work_operation_day_st_hr = None
#         assinged_work_operation_day_end_index = None
#         assinged_work_operation_day_end_hr = None


#         current_day_index = self.startDayIndex
#         dayGrayImg, mask_allowable_work, mask_allowable_delay = ScheduleAssigner.get_day_machine_sch_img(dayIndex=current_day_index, machineName=self.operationMachinName)
#         start_working_hr = self.get_starting_hr_operation_working(mask_allowable_work)
#         remaining_operation_img = self.operationGrayImg

#         if start_working_hr == -1:
#             ### Means no working hour available in that day
#             current_day_index+=1
#             ### Reset values
#             remaining_operation_img = self.operationGrayImg
#             start_working_hr = self.get_starting_hr_operation_working(mask_allowable_work)
        
#         else:
#             ### Try assigning the at start hr
#             day_operation_working_indices = []            
#             isOverlapPerfect, dayEndIndex, crop_op_startHr, cropEndHr, next_day_crop_gray = self.validate_and_crop_operation_for_next_day(remaining_operation_img, dayStartIndex=current_day_index, startHr=start_working_hr)
#             day_operation_working_indices.append(dayEndIndex)
#             while isOverlapPerfect==True:
#                 current_day_index = dayEndIndex+1
#                 isOverlapPerfect, dayEndIndex, crop_op_startHr, cropEndHr, next_day_crop_gray = self.validate_and_crop_operation_for_next_day(next_day_crop_gray, 

#                         dayStartIndex=current_day_index, startHr=start_working_hr)

#     def stretch_min_max_delay_working_mask(self):
#         """"""
#         pass

#     def check_if_color_on_gray(self,work_subtracted_mask, assigned_day_operation_work_mask):
#         """check if operation_work_mask overlapps on day_work_mask, if extra left, return end hr to crop
#         return endHr (int) for next day cropping of operation else None"""

#         whiteCount = np.sum(work_subtracted_mask==255)
#         if whiteCount==0:
#             ## work mask is perfectly overlapped
#             cropEndHr = np.min(np.argwhere(assigned_day_operation_work_mask==255), axis=1)[1]
#             isOverlapPerfect = True    
#         else:
#             cropEndHr = np.min(np.argwhere(work_subtracted_mask==255), axis=1)[1]
#             # color is overlapping gray
#             isOverlapPerfect = False


#         return isOverlapPerfect, cropEndHr




# class Validator:
#     """Class to validate all order assigning rules"""
#     def __init__(self, dayScheduleImg, assigningOrderImg, assigningWorkingHrMask, delayHrsMask, st_hr):
#         self.assigningWorkingHrMask = assigningWorkingHrMask
#         self.delayHrsMask = delayHrsMask
#         self.assigningOrderImg = assigningOrderImg
#         self.dayScheduleImg = dayScheduleImg

#     def check_rule(self):
#         """Rules
#         1. Gray_order can overlap NightNon working hours as well as production hours
#         2. Color_order can overlap only on working and non assigned hours of day
#         3.     
#         """

        

#     def check_if_other_operation_assigned_in_between(self):
#         """"""
#         pass

#     def check_if_color_on_gray(self):
#         """"""
#         pass
        

# def assign_single_order(self, order):
        
    #     self.totalOrderImg = order.getTotalOrderImage()
    #     self.currentOrderObj = order
    #     machineSeq = [operation.machineReq.name for operation in order.operationSeq]
    #     n_machines = len(machineSeq)
    #     print('machineSeq',machineSeq)
    #     # showImg("totalOrderImg",self.totalOrderImg)


       
    #     allOpearationHrs = self.totalOrderImg.shape[1]
    #     opStartDateIndex = 0        
    #     totalDaysReq = int(allOpearationHrs / 8)+3
    #     daysScheduleImgList = [] 
    #     for day in ScheduleAssigner.days_list[opStartDateIndex:opStartDateIndex+totalDaysReq]:
    #         daySchedule = DaySlotMachine.daySchedules[day]
    #         machineDayImages = []
    #         for machine in machineSeq:
    #             if machine in daySchedule.keys():
    #                 dayScheduleReq = daySchedule[machine]
    #                 daySchImg = dayScheduleReq.get_day_working_img()
                    
    #                 machineDayImages.append(daySchImg)
    #                 # print("daySchImg.shape",daySchImg.shape)
    #         imgSingleDay = np.zeros((len(machineSeq), 8,3))
    #         # print("len(machineDayImages)",len(machineDayImages))
    #         for i, machineDayImg in enumerate(machineDayImages):                
    #             imgSingleDay[i:i+1, :] = machineDayImg
    #             # showImg('imgSingleDay',imgSingleDay)
    #             # cv2.waitKey(-1)
            
    #         daysScheduleImgList.append(imgSingleDay)
    #         # print("totalSingleDayImg.shape",imgSingleDay.shape)
    
    #     totaldayImage = np.hstack(tuple(daysScheduleImgList))
    #     # showImg("totaldayImage",totaldayImage)
    #     # print("totaldayImage.shape",totaldayImage.shape)
    #     # print("self.totalOrderImg.shape",self.totalOrderImg.shape)

    #     gray_order_img = cv2.cvtColor(self.totalOrderImg.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    #     gray_day_img = cv2.cvtColor(totaldayImage.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    #     # gray_order_img = cv2.cvtColor(self.totalOrderImg, cv2.COLOR_BGR2GRAY)

    #     # print("np.unique(gray_order_img)",np.unique(gray_order_img))
    #     # print("np.unique(gray_day_img)",np.unique(gray_day_img))

    #     added = totaldayImage.copy()
    #     stHr = 0
    #     isOrderAssignable = False
    #     machineWiseImgAssigned = []
    #     while isOrderAssignable==False:
    #         added[:,stHr:stHr+allOpearationHrs] = added[:,stHr:stHr+allOpearationHrs]+self.totalOrderImg
    #         gray_added = gray_day_img.copy()
    #         gray_added[:,stHr:stHr+allOpearationHrs] = gray_added[:,stHr:stHr+allOpearationHrs]+gray_order_img

    #         # print("np.unique(gray_added)",np.unique(gray_added))
    #         # showImg("convolutioned",added)
    #         # showImg("gray_added",gray_added)
    #         # showImg("gray_order_img",gray_order_img)
    #         # showImg("gray_day_img",gray_day_img)
            
    #         stacked_gray_added = self.break_days_combined_image(gray_added)
            
            


    #         stacked_st_days = stacked_gray_added[:, 0]
    #         stacked_end_days = stacked_gray_added[:, -1]
    #         # print("stacked_st_days",stacked_st_days)
    #         # print("stacked_end_days",stacked_end_days)
            
    #         if GRAY_PLUS_BLUE_GRAY not in stacked_st_days and  GRAY_PLUS_BLUE_GRAY not in stacked_end_days:
    #             isOrderAssignable = True
    #             for i, machine in enumerate(machineSeq):
    #                 machine_img_all_days = gray_added[i:i+1, :]
    #                 stacked_gray_machine = self.break_days_combined_image(machine_img_all_days)
    #                 machineWiseImgAssigned.append(stacked_gray_machine)
                    
    #             break
    #         stHr+=1




    #         cv2.waitKey(-1)

    #     if isOrderAssignable==True:
    #         assigned_values_list = [] # list of operation with values stDate, stHr, endDate, endHr

    #         for i, machineWiseImg in enumerate(machineWiseImgAssigned):
    #             showImg(f'machine {machineSeq[i]}',machineWiseImg)

    #             points = np.argwhere(machineWiseImg>BLACK_PLUS_BLUE_GRAY)
    #             # print(f"machine {machineSeq[i]}", points)
    #             minRow = np.min(points, axis=0)[0]
    #             maxRow = np.max(points, axis=0)[0]
    #             minRowValues =  points[points[:,0]==minRow]
    #             maxRowValues = points[points[:,0]==maxRow]
    #             stHrIndex = np.min(minRowValues,axis=0)[1]
    #             endHrIndex = np.max(maxRowValues, axis=0)[1]
                
    #             stDate, endDate = ScheduleAssigner.cycleTimeHrs[opStartDateIndex+minRow], ScheduleAssigner.cycleTimeHrs[opStartDateIndex+maxRow]
    #             stHr, endHr = 8 + stHrIndex, 8 + endHrIndex
    #             # print(f"minRow {minRow} stHr {stHrIndex} maxRow {maxRow} endHrIndex {endHrIndex}")
    #             print(f"stDate {stDate} stHr {stHr}  endDate {endDate} endHr {endHr}")
    #             assigningList = [stDate, stHr, endDate, endHr]
    #             assigned_values_list.append(assigningList)
    #             # print("minRowValues",minRowValues)
                
    #         order.assign_order(assigned_values_list)
    #         cv2.waitKey(-1)    

    # def break_days_combined_image(self, combinedImg):
      #     st = 0
    #     list_img_8hrs = []
    #     while True:
    #         end = st+8
    #         if st == combinedImg.shape[1]:
    #             break
    #         crop = combinedImg[:, st:end]
    #         list_img_8hrs.append(crop)
    #         st = end
        
    #     vstacked = np.vstack(list_img_8hrs)
        
    #     return vstacked




class Order_or_job:
  # def getOrderOperationImageList(self):
        
        
        
    #     for i, operation in enumerate(self.operationSeq):
    #         imgOp = operation.create_image()
    #         self.orderImageListSeq.append(imgOp)
        
       
    #     widowName = f"Operation {self.id}"
        
    #     return self.orderImageListSeq

    # def getTotalOrderImage(self):
    #     if len(self.orderImageListSeq)==0:
    #         self.getOrderOperationImageList()
        
    #     imageHt = len(self.operationSeq)
    #     imageWd = self.totalMaxTime
    #     self.orderImg = np.zeros((imageHt, imageWd, 3))
        
    #     st = 0
    #     for i, img in enumerate(self.orderImageListSeq):
    #         operationImgWidth = img.shape[1]
    #         end = st + operationImgWidth
    #         self.orderImg[i, st:end] = img

    #         st = end

    #     return self.orderImg 

    # def assign_order(self, assigned_values_list):
    #     """assign all operations the start and end time
    #     param list of list of assigning values ex [[stDate, stHr, endDate, endHr], [stDate, stHr, endDate, endHr]]"""
        
    #     for i, operation in enumerate(self.operationSeq):
    #         # start_day_operation = start_day_first_operation
    #         stDate, stHr, endDate, endHr = assigned_values_list[i]
    #         operation.operationStart_date =stDate
    #         operation.operationStart_time = stHr
    #         operation.operationEnd_date = endDate
    #         operation.operationEnd_time = endHr
        
    #     self.isScheduleAssigned = True
    #     self.isInfeasibleForProduction=False



class DaySCheduls:
       

    # def assignMachineHrs_filled(self, listHrsBooked:List[int]):
    #     """Function takes in list of hrs ex. [10,11,12,13,14] adds them to self.hrs_filled_up"""
    #     for hr in listHrsBooked: 
    #         self.daySlotArray[0,hr] = ASSIGNED
    #     self.get_gray_day_slot_img()

    # def calculate_hrs_available(self):
    #     self.hrs_available = []
    #     for hr in range(1,25):
    #         if hr not in self.hrs_filled_up and hr not in self.hrs_not_working:
    #             self.hrs_available.append(hr)

    # def add_non_working_hrs(self, stHr, endHr):
    #     for hr in range(stHr, endHr):
    #         self.daySlotArray[0,hr] = NOT_AVAILABLE
    #     self.get_gray_day_slot_img()

    # def plot_img(self):
    #     widowName = f"daySchedule {self.machine.name} 1/1/22"
    
    # def get_available_working_slots(self):
    #     self.get_available_hrs_assigned_hrs_count()
    #     ## relative hrs 
    #     relativeHrList = [hr - self.dayStHr for hr in self.hourList_available]
    #     index_to_split_at =  []
    #     hr_list_crop = []
    #     for i, hrAvailable in enumerate(relativeHrList):
    #         if i>0:
    #             if hrAvailable - relativeHrList[i-1] == 1:
    #                 pass
    #             else:
    #                 index_to_split_at.append(i)

    #     if len(index_to_split_at)>0:
    #         ## more than one available block to assign
    #         for j, index in enumerate(index_to_split_at):
    #             if j==0:
    #                 hr_list_crop.append(relativeHrList[0:index])

    #             if j>0:                    
    #                 hr_list_crop.append(relativeHrList[index_to_split_at[j-1]:index_to_split_at[j]])
    #         hr_list_crop.append(relativeHrList[index_to_split_at[1]:]) 

    #     else:
    #         hr_list_crop = [relativeHrList]

    #     return hr_list_crop
