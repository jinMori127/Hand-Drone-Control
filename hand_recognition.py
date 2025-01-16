""" Define tools for hand gesture recognition"""


def process_hand_features(lm_list: list, used_hand: str, finger_tips: list):
    up_fingers = []
    down_fingers = []
    horizontal_fingers = []

    # Up thumb means that the hand is horizontal and the thumb is up.
    up_thumb = lm_list[4].y < lm_list[3].y and lm_list[3].y < lm_list[2].y and lm_list[2].y < lm_list[1].y
    down_thumb = lm_list[4].y > lm_list[3].y and lm_list[3].y > lm_list[2].y and lm_list[2].y > lm_list[1].y

    # Detect up thumb and horizontal fingers differently
    if used_hand == "Right":
        # thumb needs special case, uses X
        up_fingers.append(lm_list[4].x > lm_list[3].x and lm_list[3].x > lm_list[2].x and lm_list[2].x > lm_list[1].x)
        down_fingers.append(up_fingers[0])

        for tip in finger_tips:  # Detect folded fingers when right hand is pointing left, used for Up and Down
            horizontal_fingers.append(lm_list[tip].x > lm_list[tip - 2].x)

    elif used_hand == "Left":
        # thumb needs special case, uses X
        up_fingers.append(lm_list[4].x < lm_list[3].x and lm_list[3].x < lm_list[2].x and lm_list[2].x < lm_list[1].x)
        down_fingers.append(up_fingers[0])

        for tip in finger_tips:  # Detect folded fingers when left hand is pointing right, used for Up and Down
            horizontal_fingers.append(lm_list[tip].x < lm_list[tip - 2].x)

    for tip in finger_tips:  # Add every other finger pointing up
        up_fingers.append(
            lm_list[tip].y < lm_list[tip - 1].y and lm_list[tip - 1].y < lm_list[tip - 2].y and lm_list[tip - 2].y <lm_list[tip - 3].y)

        down_fingers.append(
            lm_list[tip].y > lm_list[tip - 1].y and lm_list[tip - 1].y > lm_list[tip - 2].y and lm_list[tip - 2].y >lm_list[tip - 3].y)

    return horizontal_fingers, up_thumb, down_thumb, up_fingers, down_fingers


def right_hand_recognition(lm_list: list, horizontal_fingers: list, up_thumb: bool, down_thumb: bool, up_fingers: list,
                           down_fingers: list) -> str:
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


def left_hand_recognition(lm_list: list, horizontal_fingers: list, up_thumb: bool, down_thumb: bool, up_fingers: list,
                          down_fingers: list) -> str:
    current_gesture = None

    # Stop
    if up_fingers[1] and up_fingers[2] and up_fingers[3] and up_fingers[4]:
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
