""" Define tools for hand gesture recognition"""


def right_hand_recognition(lm_list: list, horizontal_fingers: list, up_thumb: bool, down_thumb: bool, up_fingers: list, down_fingers:list) -> str:
    current_gesture = None

    # Stop
    if up_fingers[1] and up_fingers[2] and up_fingers[3] and up_fingers[4]:
        current_gesture = "Stop"

    # Forward
    elif lm_list[3].x < lm_list[4].x and lm_list[8].y < lm_list[6].y and \
            lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y and up_fingers[2]:
        current_gesture = "Forward"

    # Backward
    elif lm_list[3].x < lm_list[4].x and lm_list[3].y < lm_list[4].y and lm_list[8].y > lm_list[6].y and \
            lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y and down_fingers[2]:
        current_gesture = "Backward"

    # Left
    elif lm_list[4].y < lm_list[2].y and lm_list[8].x < lm_list[6].x and lm_list[12].x > lm_list[10].x and \
            lm_list[16].x > lm_list[14].x and lm_list[20].x > lm_list[18].x and lm_list[5].x < lm_list[0].x:
        current_gesture = "Right"  # drone's right

    # Right
    elif lm_list[4].y < lm_list[2].y and lm_list[8].x > lm_list[6].x and lm_list[12].x < lm_list[10].x and \
            lm_list[16].x < lm_list[14].x and lm_list[20].x < lm_list[18].x:
        current_gesture = "Left"  # drone's left

    # Up - Down
    elif all(horizontal_fingers):

        if up_thumb:
            current_gesture = "Up"

        if down_thumb:
            current_gesture = "Down"

    return current_gesture


def left_hand_recognition(lm_list: list, horizontal_fingers: list, up_thumb: bool, down_thumb: bool, up_fingers:list, down_fingers:list)-> str:
    current_gesture = None

    # Stop
    if  up_fingers[1] and up_fingers[2] and up_fingers[3] and up_fingers[4]:
        current_gesture = "Stop"

    # Forward
    elif lm_list[3].x > lm_list[4].x and lm_list[8].y < lm_list[6].y and \
            lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y and up_fingers[2]:
        current_gesture = "Forward"

    # Backward
    elif lm_list[3].x > lm_list[4].x and lm_list[3].y < lm_list[4].y and lm_list[8].y > lm_list[6].y and \
            lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y and down_fingers[2]:
        current_gesture = "Backward"

    # Left
    elif lm_list[4].y < lm_list[2].y and lm_list[8].x < lm_list[6].x and lm_list[12].x > lm_list[10].x and \
            lm_list[16].x > lm_list[14].x and lm_list[20].x > lm_list[18].x and lm_list[5].x < lm_list[0].x:
        current_gesture = "Right"  # drone's right

    # Right
    elif lm_list[4].y < lm_list[2].y and lm_list[8].x > lm_list[6].x and lm_list[12].x < lm_list[10].x and \
            lm_list[16].x < lm_list[14].x and lm_list[20].x < lm_list[18].x:
        current_gesture = "Left"  # drone's left

    # Up - Down
    elif all(horizontal_fingers):

        if up_thumb:
            current_gesture = "Up"

        if down_thumb:
            current_gesture = "Down"

    return current_gesture
