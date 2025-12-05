import cv2
import mediapipe as mp
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)
def count_simple_fingers(hand_landmarks):
    lm = hand_landmarks.landmark

    count = 0

    if (lm[4].y)*1.1 < lm[3].y:
        count += 1

    if lm[8].y*1.1 < lm[6].y:
        count += 1

    if lm[12].y*1.1 < lm[10].y:
        count += 1

    if lm[16].y*1.1 < lm[14].y:
        count += 1

    if lm[20].y*1.1 < lm[18].y:
        count += 1

    return count
while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame,1)

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(img_rgb)
    hand_results = hands.process(img_rgb)
    if hand_results.multi_hand_landmarks:
        cnt = count_simple_fingers(hand_results.multi_hand_landmarks[0])
        cv2.putText(frame,f"{cnt}", (30,70),cv2.FONT_HERSHEY_SIMPLEX,
    1.5,
    (0, 255, 0),
    3,
    cv2.LINE_AA)
    if results.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    cv2.imshow("Pose", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
