import cv2
import numpy as np
import config
import matplotlib.pyplot as plt 
from required_classes.scheduler_new import ScheduleAssigner

def showImg(title, img):
    resized = cv2.resize(img, None, fx=10, fy=10, interpolation=cv2.INTER_AREA)
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.imshow(title, resized)

def get_operation_work_and_delay_masks(self, operation_gray_img):
    """function to return mask_working and mask_delay from the operation_gray_img"""
    mask_operation_work = np.zeros_like(operation_gray_img)
    mask_operation_delay = np.zeros_like(operation_gray_img)
    print(mask_operation_work.shape)
    print(mask_operation_work)
    print(np.argwhere(operation_gray_img==config.OPERATION_COLOR))
    mask_operation_work[operation_gray_img==config.OPERATION_COLOR] = 255
    mask_operation_delay[operation_gray_img==config.DELAY_COLOR] = 255

    return mask_operation_work, mask_operation_delay

def get_starting_hr_operation_working(mask_allowable_work):

    if mask_allowable_work.size==0:
        min_x = 1
    else:
        coordinates = np.argwhere(mask_allowable_work==255)
        if coordinates.size==0:
            min_x=-1
            print("No whites found means no working hours available in the day")
        else:
            min_values = np.min(np.argwhere(mask_allowable_work==255), axis=0)
            if len(min_values.shape) == 0:
                print("No whites found means no working hours available in the day")
                min_x = -1
            else:    
                min_x = min_values[1]
                print('min start working hr ', min_x)

    return min_x

def check_if_it_has_more_than_1_white_blocks(mask_img):
    """returns count and start_end of the white blocks"""
    start_end_list = []

    contours, heirarchy = cv2.findContours(mask_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        
        min_x = np.min(cnt, axis=0)[0][0]
        max_x = np.max(cnt, axis=0)[0][0]
        start_end_list.append([min_x, max_x])

    return len(contours), start_end_list

def plot_3_images(img1,img2,img3):
    fig = plt.figure(figsize=(10,24))
    plt.subplot(311)
    plt.imshow(img1)
    plt.subplot(312)
    plt.imshow(img2)
    plt.subplot(313)
    plt.imshow(img3)
    plt.show()

def get_day_machine_sch_img(dayIndex, machineName):
    return ScheduleAssigner.get_day_machine_sch_img(dayIndex=dayIndex, machineName=machineName)

def plot_list_images(list_images, list_titles):
    fig = plt.figure(figsize=(10,24))
    for i in range(len(list_images)):
        sub =plt.subplot(len(list_images),1,i+1)
        sub.imshow(list_images[i])
        plt.xlim(0,24)
        plt.tick_params(axis='y',left = False, labelleft = False, )
        sub.set_xticks(np.arange(0, 24, 1))
        sub.set_ylabel(list_titles[i], rotation=0, labelpad=40)

    plt.show()