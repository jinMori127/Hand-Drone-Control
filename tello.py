import cv2
import mediapipe as mp
from djitellopy import Tello
from time import sleep
from utility import *

if __name__ == "__main__":
    tello = Tello()

    try:
        tello.connect()
        tello.streamon()
        # print(tello.get_battery())
        tello.takeoff()

        # Go up to the height of the person
        tello.send_rc_control(0, 0, 25, 0)
        sleep(2.7)
        # turn the camera on

        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Increase if multiple hands might be detected
            min_detection_confidence=0.3,  # Lower this value if far hands are hard to detect
            min_tracking_confidence=0.3  # Lower this for better tracking at a distance
        )

        '''
            mode 1 : for the hand detection 
            mode 2 : for the face tracking
            mode 3 : for the hand and face detection
        '''
        mp_draw = mp.solutions.drawing_utils

        finger_tips = [8, 12, 16, 20]
        thumb_tip = 4
        steps_x, steps_y = 0, 0  # to center the face
        current_mode = 0

        """
            Define constants for mode 2 (face detection).
        """
        w, h = 640, 480
        pid = [0.35, 0.3, 0]
        p_error = 0

        # Debounce variables
        debounce_counts = {"mode": 0}  # Track how many consecutive frames a gesture is detected
        debounce_threshold = 10  # Minimum frames for stable recognition
        mode_change_threshold = 20  # Minimum frames for stable mode change
        detected_gesture = None
        modes = ["Hand Detection", "Face Tracking", "Hand and Face Detection"]

        while True:
            img = tello.get_frame_read().frame
            img = cv2.resize(img, (w, h))
            img = cv2.flip(img, 1)

            # Display current mode
            cv2.putText(img, f"Mode: {modes[current_mode]}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 0, 255), 2)

            info = None
            # Only get the face info in mode 1 and 2.
            if current_mode in [1, 2]:
                img, info = findFace(img)

            # Mode logic
            if current_mode == 0:
                movement = mode_1(tello=tello, detected_gesture=detected_gesture)
                detected_gesture = None

            elif current_mode == 1:
                p_error = mode_2(tello=tello, info=info, width=w, pid=pid, p_error=p_error)
                detected_gesture = None

            elif current_mode == 2:
                mode_3(tello=tello, info=info, width=w, pid=pid, p_error=p_error, detected_gesture=detected_gesture)

            results = hands.process(img)

            if results.multi_hand_landmarks:
                for hand_landmark in results.multi_hand_landmarks:
                    lm_list = []
                    for id, lm in enumerate(hand_landmark.landmark):
                        lm_list.append(lm)
                    finger_fold_status = []
                    for tip in finger_tips:
                        x, y = int(lm_list[tip].x * w), int(lm_list[tip].y * h)
                        # print(id, ":", x, y)
                        # cv2.circle(img, (x, y), 15, (255, 0, 0), cv2.FILLED)

                        if lm_list[tip].x < lm_list[tip - 2].x:
                            # cv2.circle(img, (x, y), 15, (0, 255, 0), cv2.FILLED)
                            finger_fold_status.append(True)
                        else:
                            finger_fold_status.append(False)

                    # print(finger_fold_status)

                    x, y = int(lm_list[8].x * w), int(lm_list[8].y * h)
                    # print(x, y)

                    # Gesture recognition logic
                    current_gesture = None

                    # Stop
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
                            lm_list[16].x > lm_list[14].x and lm_list[20].x > lm_list[18].x and lm_list[5].x < lm_list[0].x:
                        current_gesture = "Right" # drone's right

                    # Right
                    if lm_list[4].y < lm_list[2].y and lm_list[8].x > lm_list[6].x and lm_list[12].x < lm_list[10].x and \
                            lm_list[16].x < lm_list[14].x and lm_list[20].x < lm_list[18].x:
                        current_gesture = "Left" # drone's left

                    up_thumb = lm_list[4].y < lm_list[3].y and lm_list[3].y < lm_list[2].y and lm_list[2].y < lm_list[1].y
                    down_thumb = lm_list[4].y > lm_list[3].y and lm_list[3].y > lm_list[2].y and lm_list[2].y > lm_list[1].y

                    if all(finger_fold_status):

                        if up_thumb:
                        # if lm_list[thumb_tip].y < lm_list[thumb_tip - 1].y < lm_list[thumb_tip - 2].y and lm_list[0].x < \
                        #         lm_list[3].y:
                            current_gesture = "Up"

                        if down_thumb:
                        # if lm_list[thumb_tip].y > lm_list[thumb_tip - 1].y > lm_list[thumb_tip - 2].y and lm_list[0].x < \
                        #         lm_list[3].y:
                            current_gesture = "Down"

                    # Change mode
                    up_finger1 = lm_list[4].x <  lm_list[3].x and lm_list[3].x <  lm_list[2].x and lm_list[2].x <  lm_list[1].x
                    up_finger2 = lm_list[8].y <  lm_list[7].y and lm_list[7].y <  lm_list[6].y and lm_list[6].y <  lm_list[5].y
                    up_finger3 = lm_list[12].y <  lm_list[11].y and lm_list[11].y <  lm_list[10].y and lm_list[10].y <  lm_list[9].y
                    up_finger4 = lm_list[16].y <  lm_list[15].y and lm_list[15].y <  lm_list[14].y and lm_list[14].y <  lm_list[13].y
                    up_finger5 = lm_list[20].y <  lm_list[19].y and lm_list[19].y <  lm_list[18].y and lm_list[18].y <  lm_list[17].y

                    up_fingers = [up_finger1, up_finger2, up_finger3, up_finger4, up_finger5]
                    for i, finger in enumerate(up_fingers):
                        if finger:
                            print(f"Finger{i}")

                    if not up_finger1 and up_finger2 and not up_finger3 and not up_finger4 and up_finger5:
                    #if lm_list[3].x > lm_list[4].x and lm_list[8].y < lm_list[6].y and lm_list[12].y > lm_list[
                        # 10].y and \
                        #     lm_list[16].y > lm_list[14].y and lm_list[20].y < lm_list[18].y:

                        debounce_counts["mode"] += 1
                        if debounce_counts["mode"] >= mode_change_threshold:
                            current_mode = (current_mode + 1) % 3
                            debounce_counts["mode"] = 0

                    # Debouncing logic
                    if current_gesture:
                        debounce_counts[current_gesture] = debounce_counts.get(current_gesture, 0) + 1
                        for gesture in list(debounce_counts):
                            if gesture != current_gesture:
                                debounce_counts[gesture] = max(0, debounce_counts[gesture] - 1)
                    else:
                        for gesture in list(debounce_counts):
                            if gesture == "mode":
                                continue
                            debounce_counts[gesture] = max(0, debounce_counts[gesture] - 1)

                    # Recognize gesture if it exceeds debounce threshold
                    for gesture, count in debounce_counts.items():
                        if gesture == "mode":
                            continue
                        if count >= debounce_threshold:
                            detected_gesture = gesture
                            # Remove 3 from counter for faster detection
                            debounce_counts[gesture] = debounce_threshold - 1

                    # Display recognized gesture
                    if detected_gesture:
                        cv2.putText(img, detected_gesture, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                    (0, 0, 255), 2)

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
