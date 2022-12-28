import matplotlib.pyplot as plt 
import cv2
import numpy as np
import os



def plot_list_images(list_images, list_titles):
    fig = plt.figure(figsize=(10,24))
    for i in range(len(list_images)):
        sub =plt.subplot(len(list_images),1,i+1)
        sub.imshow(list_images[i][:,:,::-1])
        plt.xlim(0,24)
        plt.tick_params(axis='y',left = False, labelleft = False)
        sub.set_xticks(np.arange(0, 24, 1))
        sub.set_ylabel(list_titles[i], rotation=0, labelpad=40)
    
    plt.show()


def get_output_csv_file_path(inputExcelFilePath):
    fileNameInput = os.path.basename(inputExcelFilePath)
    parentDirPath = os.path.dirname(inputExcelFilePath)
    

    ext = fileNameInput.split(".")[-1]
    fileNameWoExt = fileNameInput[:-1 *(len(ext)+1)]
    outputFileName = "assigned_"+fileNameWoExt + ".csv"
    
    outputFilePath = os.path.join(parentDirPath, outputFileName)
    return outputFilePath


