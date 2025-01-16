import cv2

'''
    mode 1 : for the hand detection 
    mode 2 : for the face tracking
    mode 3 : for the hand and face detection
'''
import mediapipe as mp
from djitellopy import Tello
from time import sleep
from utility import *


def right_hand_recognition(lm_list: list) -> str:
    pass


def left_hand_recognition(lm_list: list) -> str:
    pass


if __name__ == "__main__":

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(  # Parameters for the hand model
        static_image_mode=False,
        max_num_hands=1,  # Increase if multiple hands might be detected
        min_detection_confidence=0.3,  # Lower this value if far hands are hard to detect
        min_tracking_confidence=0.3  # Lower this for better tracking at a distance
    )
    mp_draw = mp.solutions.drawing_utils

    # General variables
    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4
    steps_x, steps_y = 0, 0  # to center the face
    current_mode = 0
    w, h = 640, 480
    pid = [0.35, 0.3, 0]
    p_error = 0

    # Debounce variables
    debounce_counts = {"Mode": 0}  # Track how many consecutive frames a gesture is detected
    debounce_threshold = 10  # Minimum frames for stable recognition
    mode_change_threshold = 10  # Minimum frames for stable mode change
    detected_gesture = None
    modes = ["Hand Detection", "Face Tracking", "Hand and Face Detection"]

    tello = Tello()
    try:

        tello.connect()
        tello.streamon()  # turn the camera on
        tello.takeoff()

        # Go up to the height of the person
        tello.send_rc_control(0, 0, 25, 0)
        sleep(2.2)

        while True:
            img = tello.get_frame_read().frame
            img = cv2.resize(img, (w, h))
            img = cv2.flip(img, 1)

            # Display current mode
            cv2.putText(img, f"Mode: {modes[current_mode]}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Mode logic
            if current_mode == 0:
                movement = mode_1(tello=tello, detected_gesture=detected_gesture)
                detected_gesture = None

            elif current_mode == 1:
                detected_gesture = None
                img, info = findFace(img)
                p_error = mode_2(tello=tello, info=info, width=w, pid=pid, p_error=p_error)

            elif current_mode == 2:
                img, info = findFace(img)
                mode_3(tello=tello, info=info, width=w, pid=pid, p_error=p_error, detected_gesture=detected_gesture)

            results = hands.process(img)

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmark, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):  # REMOVE FOR
                    # Process the data
                    used_hand = hand_handedness.classification[0].label  # Left or Right
                    horizontal_fingers = []
                    up_fingers = []
                    lm_list = []

                    current_gesture = None


                    '''
                        Finger detection and folded state detection
                    '''

                    for id, lm in enumerate(hand_landmark.landmark):
                        lm_list.append(lm)

                    # Detect folded fingers when left hand is pointing right, used for Up and Down
                    for tip in finger_tips:
                        horizontal_fingers.append(lm_list[tip].x < lm_list[tip - 2].x)

                    # Detect folded fingers when hand is pointing up, used for Mode Change
                    up_fingers.append(lm_list[4].x < lm_list[3].x and lm_list[3].x < lm_list[2].x and lm_list[2].x < lm_list[1].x) # thumb needs special case, uses X
                    for tip in finger_tips:
                        up_fingers.append(lm_list[tip].y < lm_list[tip-1].y and lm_list[tip-1].y < lm_list[tip-2].y and lm_list[tip-2].y < lm_list[tip-3].y)

                    up_thumb = lm_list[4].y < lm_list[3].y and lm_list[3].y < lm_list[2].y and lm_list[2].y < lm_list[1].y
                    down_thumb = lm_list[4].y > lm_list[3].y and lm_list[3].y > lm_list[2].y and lm_list[2].y > lm_list[1].y


                    '''
                        Gesture processing
                    '''

                    if lm_list[4].y < lm_list[2].y and lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and \
                            lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y and lm_list[17].x < lm_list[
                        0].x < lm_list[5].x:
                        current_gesture = "Stop"

                    # Forward
                    if lm_list[3].x > lm_list[4].x and lm_list[8].y < lm_list[6].y and lm_list[12].y > lm_list[10].y and \
                            lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
                        current_gesture = "Forward"

                    # Backward
                    if lm_list[3].x > lm_list[4].x and lm_list[3].y < lm_list[4].y and lm_list[8].y > lm_list[6].y and \
                            lm_list[12].y < lm_list[10].y and \
                            lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y:
                        current_gesture = "Backward"

                    # Left
                    if lm_list[4].y < lm_list[2].y and lm_list[8].x < lm_list[6].x and lm_list[12].x > lm_list[10].x and \
                            lm_list[16].x > lm_list[14].x and lm_list[20].x > lm_list[18].x and lm_list[5].x < lm_list[
                        0].x:
                        current_gesture = "Right"  # drone's right

                    # Right
                    if lm_list[4].y < lm_list[2].y and lm_list[8].x > lm_list[6].x and lm_list[12].x < lm_list[10].x and \
                            lm_list[16].x < lm_list[14].x and lm_list[20].x < lm_list[18].x:
                        current_gesture = "Left"  # drone's left

                    # Up - Down
                    if all(horizontal_fingers):

                        if up_thumb:
                            current_gesture = "Up"

                        if down_thumb:
                            current_gesture = "Down"

                    # Mode
                    if not up_fingers[0] and up_fingers[1] and not up_fingers[2] and not up_fingers[3] and up_fingers[4]:
                        current_gesture = "Mode"


                    '''
                        Command processing
                    '''

                    # Debouncing logic
                    if current_gesture: # Increment the corresponding gesture count, decrement the rest
                        debounce_counts[current_gesture] = debounce_counts.get(current_gesture, 0) + 1
                        if current_gesture == "Mode":
                            print("Mode before dec", debounce_counts[current_gesture])

                        for gesture in list(debounce_counts):
                            if gesture != current_gesture:
                                debounce_counts[gesture] = max(0, debounce_counts[gesture] - 1)

                    else: # No gesture, decrement all the gesture counts
                        for gesture in list(debounce_counts):
                            debounce_counts[gesture] = max(0, debounce_counts[gesture] - 1)
                    if current_gesture == "Mode":
                        print("Mode after dec", debounce_counts[current_gesture])
                        print()

                    # Recognize gesture if it exceeds debounce threshold
                    for gesture, count in debounce_counts.items():
                        if gesture == "Mode" and count >= mode_change_threshold:
                            print("Changing Mode")
                            current_mode = (current_mode + 1) % 3
                            debounce_counts["Mode"] = 0
                            detected_gesture = gesture

                        elif count >= debounce_threshold:
                            detected_gesture = gesture
                            debounce_counts[gesture] = debounce_threshold - 1


                    '''
                        Add info to the screen
                    '''
                    # Display recognized gesture
                    if detected_gesture:
                        cv2.putText(img, detected_gesture, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                    mp_draw.draw_landmarks(img, hand_landmark,
                                           mp_hands.HAND_CONNECTIONS,
                                           mp_draw.DrawingSpec((0, 0, 255), 2, 2),
                                           mp_draw.DrawingSpec((0, 255, 0), 2, 2)
                                           )


            cv2.imshow("Hand Sign Detection", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on 'q'
                print("Exiting...")
                tello.land()
                tello.streamoff()
                break

    ## when exit land the drone
    except Exception as e:
        print(f"An error occurred: {e}")
        tello.land()

    finally:
        cv2.destroyAllWindows()
        tello.land()
