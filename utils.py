import cv2


def showImg(title, img):
    resized = cv2.resize(img, None, fx=10, fy=10, interpolation=cv2.INTER_AREA)
    # cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.imshow(title, resized)
    