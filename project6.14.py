import cv2
import numpy as np
import sys
import RPi.GPIO as GPIO
import socket

client = socket.socket()  # 声明socket类型，同时生成socket连接对象
client.connect(('192.168.123.26', 50007))  # 开始连接，ip地址为本地，端口号为6961

# open a camera with certain index
frameWidth = 1280
frameHeight = 720
cap = cv2.VideoCapture(0)
cap.set(3, frameWidth)  # 宽度
cap.set(4, frameHeight)  # 高度
# cap.set(10, 150)  # 亮度
# whether the camera is successfully opened
if cap.isOpened():
    print("camera ready.")
else:
    print("camera open failed. close.")
    # stop prg.
    sys.exit()

Type = ["WHITE", "YELLOW", "GREEN", "STEM"]
Color = [(255, 255, 255), (51, 255, 255), (0, 204, 0), (0, 204, 0)]
h_min = [68, 39, 68, 40]
h_max = [91, 71, 96, 98]
s_min = [0, 18, 50, 13]
s_max = [21, 82, 255, 69]
v_min = [255, 217, 124, 0]
v_max = [255, 255, 255, 255]

maskleave = cv2.imread("/home/pi/Desktop/maskl0508.jpg")
maskleaveHSV = cv2.cvtColor(maskleave, cv2.COLOR_BGR2HSV)
maskstem = cv2.imread("/home/pi/Desktop/masks0509.jpg")
maskstemHSV = cv2.cvtColor(maskstem, cv2.COLOR_BGR2HSV)
masktarget = cv2.imread("/home/pi/Desktop/target.jpg")  # 取包括桩在内的小长方形区域
masktargetHSV = cv2.cvtColor(masktarget, cv2.COLOR_BGR2HSV)
lowermask = np.array([0, 0, 100])
uppermask = np.array([0, 0, 255])
mask_leave = cv2.inRange(maskleaveHSV, lowermask, uppermask)
mask_stem = cv2.inRange(maskstemHSV, lowermask, uppermask)
mask_target = cv2.inRange(masktargetHSV, lowermask, uppermask)


# what if put all of the process into the definition?
def getLeaves(img, i):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_leave = cv2.bitwise_and(imgHSV, imgHSV, mask=mask_leave)
    lower = np.array([h_min[i], s_min[i], v_min[i]])
    upper = np.array([h_max[i], s_max[i], v_max[i]])
    maskcolor = cv2.inRange(img_leave, lower, upper)
    kernel = np.ones((3, 3), np.uint8)
    maskerode = cv2.erode(maskcolor, kernel, iterations=2)
    maskdilate = cv2.dilate(maskerode, kernel, iterations=4)
    contours, hierarchy = cv2.findContours(maskdilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    count = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(area)
        if area > 14000:
            # print(area)
            cv2.drawContours(imgContour, cnt, -1, (120, 100, 100), 3)
            peri = cv2.arcLength(cnt, True)
            # print(peri)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # print(len(approx))
            objCor = len(approx)
            x, y, w, h = cv2.boundingRect(approx)
            if objCor > 5:
                if area > 28000:
                    count = count + 2
                else:
                    count = count + 1
                cv2.rectangle(imgContour, (x, y), (x + w, y + h), Color[i], 2)
                cv2.putText(imgContour, Type[i],
                            (x + (w // 2) - 10, y + (h // 2) - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, Color[i],
                            2)
    # cv2.putText(imgContour, number, (500, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
    # print("end")
    return count


def getStems(img, i):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    count = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(area)
        if area > 900:
            # print(area)
            cv2.drawContours(imgContour, cnt, -1, (120, 100, 100), 3)
            peri = cv2.arcLength(cnt, True)
            # print(peri)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # print(len(approx))
            objCor = len(approx)
            # print(objCor)
            x, y, w, h = cv2.boundingRect(approx)
            # if objCor > 5:
            count = count + 1
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), Color[i], 2)
    return count


def StopTarget(image):
    imgHSVtarget = cv2.bitwise_and(image, image, mask=mask_target)
    lower = np.array([40, 30, 135])
    upper = np.array([90, 210, 255])
    mask = cv2.inRange(imgHSVtarget, lower, upper)  # 取绿色阈值区域
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)  # 膨胀
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        print(area)
        if area > 2000:
            # peri = cv2.arcLength(cnt, True)
            # print(peri)
            # approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # print(len(approx))
            return True
    else:
        return False


def StopStems(image, i):
    lower = np.array([h_min[i], s_min[i], v_min[i]])
    upper = np.array([h_max[i], s_max[i], v_max[i]])
    imgHSVstem = cv2.bitwise_and(image, image, mask=mask_stem)
    mask = cv2.inRange(imgHSVstem, lower, upper)
    kernel = np.ones((3, 3), np.uint8)
    maskerode = cv2.erode(mask, kernel, iterations=0)
    maskdilate = cv2.dilate(maskerode, kernel, iterations=2)
    contours, hierarchy = cv2.findContours(maskdilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    count = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(area)
        if area > 900:
            # print(area)
            # cv2.drawContours(imgContour, cnt, -1, (120, 100, 100), 3)
            # peri = cv2.arcLength(cnt, True)
            # print(peri)
            # approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # print(len(approx))
            # objCor = len(approx)
            # print(objCor)
            # x, y, w, h = cv2.boundingRect(approx)
            # if objCor > 5:
            count = count + 1
            # cv2.rectangle(imgContour, (x, y), (x + w, y + h), Color[i], 2)
    if count >= 6:
        return True
    else:
        return False


message = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
           '0', '0']
x1 = -2
x2 = -1
complete = 0
while True:
    success, img = cap.read()
    imgContour = img.copy()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(33, GPIO.IN)
    GPIO.setup(35, GPIO.IN)
    GPIO.setup(37, GPIO.OUT)
    GPIO.output(37, 0)

    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    if StopTarget(imgHSV) and StopStems(imgHSV, 3):
        GPIO.output(37, 1)  # stop
        sum_allleaves = sum_stems = sum_whiteleaves = 0
        x1 += 2
        x2 += 2
        index = 0
        while index < 5:
            success, img = cap.read()
            imgContour = img.copy()
            imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            img_leave = cv2.bitwise_and(imgHSV, imgHSV, mask=mask_leave)
            img_stem = cv2.bitwise_and(imgHSV, imgHSV, mask=mask_stem)

            # get all the leaves
            count_allleaves = 0
            for i in range(0, 3):
                lower = np.array([h_min[i], s_min[i], v_min[i]])
                upper = np.array([h_max[i], s_max[i], v_max[i]])
                mask = cv2.inRange(img_leave, lower, upper)
                kernel = np.ones((3, 3), np.uint8)
                newmask1 = cv2.erode(mask, kernel, iterations=2)
                newmask2 = cv2.dilate(newmask1, kernel, iterations=4)
                count_leaves = getLeaves(newmask2)
                count_allleaves += count_leaves

            # get white leaves
            i = 0
            lower = np.array([h_min[i], s_min[i], v_min[i]])
            upper = np.array([h_max[i], s_max[i], v_max[i]])
            mask = cv2.inRange(img_leave, lower, upper)
            kernel = np.ones((3, 3), np.uint8)
            newmask3 = cv2.erode(mask, kernel, iterations=2)
            newmask4 = cv2.dilate(newmask3, kernel, iterations=4)
            count_whiteleaves = getLeaves(newmask4)

            # get stems
            i = 3
            lower = np.array([h_min[i], s_min[i], v_min[i]])
            upper = np.array([h_max[i], s_max[i], v_max[i]])
            mask = cv2.inRange(img_stem, lower, upper)
            kernel = np.ones((3, 3), np.uint8)
            newmask5 = cv2.erode(mask, kernel, iterations=0)
            newmask6 = cv2.dilate(newmask5, kernel, iterations=2)
            count_stems = getStems(newmask6)

            sum_allleaves += count_allleaves
            sum_whiteleaves += count_whiteleaves
            sum_stems += count_stems
            index += 1

        result_allleaves = round(sum_allleaves/index)
        result_whiteleaves = round(sum_whiteleaves/index)
        result_stems = round(sum_stems/index)
        # if result_stems < 6:
        #     result_stems = 6
        # elif result_stems > 8:
        #     result_stems = 8
        result_flowers = result_stems - result_allleaves
        # if result_whiteleaves >= 3:
        #     result_whiteleaves = 3
        #     result_flowers = 0
        # if result_flowers < 0:
        #     result_flowers = 0
        # elif result_flowers > 4:
        #     result_flowers = 4
        result_text = 'whitelaves: ' + str(result_whiteleaves) + 'flowers: ' + str(result_flowers)
        cv2.putText(imgContour, result_text, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 2)

        message[x1] = str(result_whiteleaves)
        message[x2] = str(result_flowers)
        cv2.imwrite('/home/pi/' + 'image' + str(x1/2 + 1) + '.png', imgContour)
        msg = ''.join(message)
        print(msg)
        client.send(msg.encode("utf-8"))  # 发送信息到服务器

        GPIO.output(37, 0)
        print("wait for next task")

    client.send(msg.encode("utf-8"))  # 发送信息到服务器
    cv2.imshow("imgContour", imgContour)
    cv2.waitKey(1)

    if x1 == 22:
        cv2.waitKey(1500)
        data = client.recv(1024)  # 接收服务器发过来的信息
        print('client_recv:', data.decode())  # 打印服务器发来的信息
        break

    GPIO.cleanup()

client.close()  # 最后，关闭客户端
