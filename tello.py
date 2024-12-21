import cv2
import mediapipe as mp


def findFace(img):
    faceCaseade = cv2.CascadeClassifier('resources/haarcascade_frontalface_default.xml')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCaseade.detectMultiScale(imgGray, 1.2, 8)

    myFaces = []
    myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        myFaceListArea.append(area)
        myFaces.append((cx, cy))

    if len(myFaces) > 0:
        index = myFaceListArea.index(max(myFaceListArea))

        return img, [myFaces[index], myFaceListArea[index]]
    else:
        return img, [[0, 0], 0]


if __name__ == "__main__":
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,  # Increase if multiple hands might be detected
        min_detection_confidence=0.3,  # Lower this value if far hands are hard to detect
        min_tracking_confidence=0.3  # Lower this for better tracking at a distance
    )

    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(1)

    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4

    # Debounce variables
    debounce_counts = {}  # Track how many consecutive frames a gesture is detected
    debounce_threshold = 10  # Minimum frames for stable recognition
    detected_gesture = None

    while True:
        ret, img = cap.read()
        img = cv2.flip(img, 1)
        if not ret:
            print("Failed to grab frame. Check if the camera is connected.")
            continue
        # get the faces in the Image
        findFace(img)

        img = cv2.resize(img, (640, 480))
        h, w, c = img.shape
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

                print(finger_fold_status)

                x, y = int(lm_list[8].x * w), int(lm_list[8].y * h)
                print(x, y)

                # Gesture recognition logic
                current_gesture = None

                # stop
                if lm_list[4].y < lm_list[2].y and lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and \
                        lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y and lm_list[17].x < lm_list[
                    0].x < \
                        lm_list[5].x:
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
                    current_gesture = "Left"

                # Right
                if lm_list[4].y < lm_list[2].y and lm_list[8].x > lm_list[6].x and lm_list[12].x < lm_list[10].x and \
                        lm_list[16].x < lm_list[14].x and lm_list[20].x < lm_list[18].x:
                    current_gesture = "Right"

                if all(finger_fold_status):
                    # like
                    if lm_list[thumb_tip].y < lm_list[thumb_tip - 1].y < lm_list[thumb_tip - 2].y and lm_list[0].x < \
                            lm_list[3].y:
                        current_gesture = "Up"
                    # Dislike
                    if lm_list[thumb_tip].y > lm_list[thumb_tip - 1].y > lm_list[thumb_tip - 2].y and lm_list[0].x < \
                            lm_list[3].y:
                        current_gesture = "Down"

                # Debouncing logic
                if current_gesture:
                    debounce_counts[current_gesture] = debounce_counts.get(current_gesture, 0) + 1
                    for gesture in list(debounce_counts):
                        if gesture != current_gesture:
                            debounce_counts[gesture] = max(0, debounce_counts[gesture] - 1)
                else:
                    for gesture in list(debounce_counts):
                        debounce_counts[gesture] = max(0, debounce_counts[gesture] - 1)

                # Recognize gesture if it exceeds debounce threshold
                for gesture, count in debounce_counts.items():
                    if count >= debounce_threshold:
                        detected_gesture = gesture
                        debounce_counts[gesture] = 0  # Reset count after recognition

                # Display recognized gesture
                if detected_gesture:
                    cv2.putText(img, detected_gesture, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                mp_draw.draw_landmarks(img, hand_landmark,
                                       mp_hands.HAND_CONNECTIONS,
                                       mp_draw.DrawingSpec((0, 0, 255), 2, 2),
                                       mp_draw.DrawingSpec((0, 255, 0), 2, 2)
                                       )

        cv2.imshow("Hand Sign Detection", img)
        cv2.waitKey(1)
