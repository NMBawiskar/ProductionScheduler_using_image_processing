import numpy as np
import cv2
from matplotlib import pyplot as plt

images = []

a = np.zeros((1,24),dtype='uint8')
img = cv2.merge((a,a,a))

img1 = img.copy()
img2 = img.copy()
img3 = img.copy()
img1[:,3:15] = (94,25,68)
img2[:,8:16] = (255,162,173)
img3[:,3:15] = (225,248,255)
images.append(img1)
images.append(img2)
images.append(img3)

titles = ["01-03-22","01-04-22","01-05-22"]



def plot_list_images(list_images, list_titles):
    fig = plt.figure(figsize=(10,24))
    for i in range(len(list_images)):
        sub =plt.subplot(len(list_images),1,i+1)
        sub.imshow(list_images[i])
        plt.xlim(0,24)
        plt.tick_params(axis='y',left = False, labelleft = False, )
        sub.set_xticks(np.arange(0, 24, 1))
        sub.set_ylabel(list_titles[i], rotation=0, labelpad=40)
        # sub.set_yticks(None)

        # plt.title(list_titles[i])
        # ax = plt.axis()
    plt.show()


plot_list_images(images,titles)