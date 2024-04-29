import cv2
import cvzone
import numpy as np
import pyautogui
from cvzone.FPS import FPS
from mss import mss

fpsReader = FPS()

def caputure_screen_region_opencv(x, y, desired_width, desired_height):
    screenshot = pyautogui.screenshot(region=(x, y, desired_width, desired_height))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot

def caputure_screen_region_opencv_mss(x, y, width, height):
    with mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

def pre_process(_imgCrop):
    gray_frame = cv2.cvtColor(_imgCrop, cv2.COLOR_BGR2GRAY)
    _, binary_frame = cv2.threshold(gray_frame, 127,255, cv2.THRESH_BINARY_INV)
    canny_frame = cv2.Canny(binary_frame, 50, 50)
    kernel = np.ones((5,5))
    dilated_frame = cv2.dilate(canny_frame, kernel, iterations=1)
    return dilated_frame

def find_obstacles(_imgCrop, imgPre):
    imgContours, conFound = cvzone.findContours(_imgCrop, imgPre, minArea=100, filter=None)
    return imgContours, conFound

def game_logic(conFound, _imgContours, jump_distance=63 ):
    if conFound:
        left_most_contour = sorted(conFound, key=lambda x: x["bbox"][0])

        cv2.line(_imgContours,
                 (0, left_most_contour[0]["bbox"][1] + 10),
                 (left_most_contour[0]["bbox"][0], left_most_contour[0]["bbox"][1] + 10), (0, 200, 0), 10)

        if left_most_contour[0]["bbox"][0] < jump_distance:
            pyautogui.press("space")
            print("jump      ", left_most_contour[0]["bbox"][0])

    return _imgContours

while True:
    # Capture the screen region of the game
    # imgGame = caputure_screen_region_opencv(200, 200, 800, 300)
    imgGame = caputure_screen_region_opencv_mss(200, 200, 800, 300)

    # Crop the image to the desired region
    #cp = 110, 200, 200 # mss not in use
    cp = 200, 300, 300 # mss in use
    imgCrop = imgGame[cp[0]:cp[1], cp[2]:]

    # Preprocess the image
    imgPre = pre_process(imgCrop)

    # Find obstacles
    imgContours, conFound = find_obstacles(imgCrop, imgPre)

    # Apply game logic
    imgContours = game_logic(conFound, imgContours)

    # Display the result
    imgGame[cp[0]:cp[1], cp[2]:] = imgContours
    fps, imgGame = fpsReader.update(imgGame)

    cv2.imshow("Game", imgGame)
    #cv2.imshow("imgCrop", imgCrop)
    #cv2.imshow("imgPre", imgPre)
    #cv2.imshow("imContours", imgContours)
    cv2.waitKey(1)
