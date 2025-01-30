import cv2
from time import sleep
from dataclasses import dataclass
import numpy as np

FORWARD_BACKWARD_RANGE = [22000, 24000]


# FORWARD_BACKWARD_RANGE = [12330, 14500]


@dataclass
class Movement:
    left_right: int = 0
    forward_backward: int = 0
    up_down: int = 0
    yaw_velocity: int = 0


def findFace(img):
    faceCaseade = cv2.CascadeClassifier('resources/haarcascade_frontalface_default.xml')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCaseade.detectMultiScale(imgGray, 1.1, 10)

    myFaces = []
    myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        myFaceListArea.append(area)
        myFaces.append((cx, cy))

    if len(myFaces) != 0:
        index = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaces[index], myFaceListArea[index]]
    else:
        return img, [[0, 0], 0]


def mode_1(tello, detected_gesture: str, do_sleep: bool = True):
    """
    :param do_sleep: tells the drone if to sleep or not when move
    :param tello: the Drone object
    :param detected_gesture: the detected gesture from the hand detection
    brief: this function will move the drone according to the detected gesture
    """
    movement = Movement()
    speed = 50

    if detected_gesture == "Forward":
        movement.forward_backward += speed
    elif detected_gesture == "Backward":
        movement.forward_backward -= speed

    elif detected_gesture == "Left":
        movement.left_right -= speed
    elif detected_gesture == "Right":
        movement.left_right += speed

    elif detected_gesture == "Up":
        movement.up_down += speed
    elif detected_gesture == "Down":
        movement.up_down -= speed

    elif detected_gesture == "Stop":
        movement.yaw_velocity = tello.land()

    if do_sleep:
        tello.send_rc_control(movement.left_right,
                              movement.forward_backward,
                              movement.up_down,
                              movement.yaw_velocity)
        sleep(0.05)
    return movement


def mode_2(tello, info, width, pid, p_error):
    """
    :param info: the info of the face detected [center of the face, area of the face]
    brief: this function will track the face and keep the drone in the center of the face
    """
    x, y = info[0]
    area = info[1]

    # How far away is the object of the center.
    error = x - width // 2
    speed = pid[0] * error + pid[1] * (error - p_error)
    speed = int(np.clip(speed, -100, 100))

    print(area)
    forward_backward = 0
    if FORWARD_BACKWARD_RANGE[0] < area < FORWARD_BACKWARD_RANGE[1]:
        forward_backward = 0
    # Check that the face area is in the wanted range
    elif area > FORWARD_BACKWARD_RANGE[1]:
        forward_backward = -20  # move backward
    elif area < FORWARD_BACKWARD_RANGE[0] and area != 0:
        forward_backward = 20  # move forward

    if x == 0:
        speed = 0
        error = 0

    # if forward_backward is not None:
    print(f"({0}, {forward_backward}, {0}, {speed})")
    tello.send_rc_control(0, forward_backward, 0, -speed)
    return error


def mode_3(tello, info, width, pid, p_error, detected_gesture: str):
    """Center the face and then apply the detected gesture according to the detected_gesture"""

    # now move the yaw to keep the face always in the middle of hte picture.
    x, y = info[0]

    # How far away is the object of the center.
    error = x - width // 2
    speed = pid[0] * error + pid[1] * (error - p_error)
    speed = int(np.clip(speed, -100, 100))
    if x == 0:
        speed = 0
        error = 0

    movement = Movement(left_right=0, forward_backward=0, up_down=0, yaw_velocity=-speed)
    if detected_gesture is not None:
        movee2 = mode_1(tello=tello, detected_gesture=detected_gesture, do_sleep=False)
        movement.left_right = movee2.left_right
        movement.forward_backward = movee2.forward_backward
        movement.up_down = movee2.up_down

    tello.send_rc_control(movement.left_right, movement.forward_backward, movement.up_down, movement.yaw_velocity)
    sleep(0.05)

    return error
