import cv2
import mediapipe as mp
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose()
mode_list = ["push ups", "squats"]
mode_index = 0
current_mode = mode_list[mode_index]
counter_data_pushups = {"count": 0, "stage": "up", "plank_ok": False}
counter_data_squats = {"count": 0, "stage": "up", "head_pos": 0}
cap = cv2.VideoCapture(0)
def all_landmarks_on_screen(landmarks):
    for lm in landmarks:
        if not (0 <= lm.x <= 1 and 0 <= lm.y <= 1):
            return False
    return True

def count_pushups(results, counter_data):
    lm = results.pose_landmarks.landmark
    shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    elbow = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]
    knee = lm[mp_pose.PoseLandmark.LEFT_KNEE.value]

    if abs(elbow.y - knee.y) > 0.11 or shoulder.y > wrist.y:
        counter_data["plank_ok"] = False
        return counter_data
    else:
        counter_data["plank_ok"] = True

    import math
    def calc_angle(a, b, c):
        ax, ay = a.x, a.y
        bx, by = b.x, b.y
        cx, cy = c.x, c.y
        ang = math.degrees(
            math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx)
        )
        return abs(ang)

    angle = calc_angle(shoulder, elbow, wrist)

    if angle < 80 and counter_data["stage"] == "up":
        counter_data["stage"] = "down"
    if angle > 160 and counter_data["stage"] == "down":
        counter_data["stage"] = "up"
        counter_data["count"] += 1

    return counter_data

def count_squats(results, counter_data):
    lm = results.pose_landmarks.landmark
    hip = lm[mp_pose.PoseLandmark.LEFT_HIP.value]
    knee = lm[mp_pose.PoseLandmark.LEFT_KNEE.value]
    ankle = lm[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    head = lm[mp_pose.PoseLandmark.LEFT_EYE.value]

    import math
    def calc_angle(a, b, c):
        ax, ay = a.x, a.y
        bx, by = b.x, b.y
        cx, cy = c.x, c.y
        ang = math.degrees(
            math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx)
        )
        return abs(ang)

    angle = calc_angle(hip, knee, ankle)

    if angle < 90 and counter_data["stage"] == "up" and (counter_data["head_pos"])*1.1 < head.y:
        counter_data["stage"] = "down"
        counter_data["head_pos"] = head.y

    if angle > 160 and counter_data["stage"] == "down" and (counter_data["head_pos"])*1.1 > head.y:
        counter_data["stage"] = "up"
        counter_data["count"] += 1
        counter_data["head_pos"] = head.y

    return counter_data


state = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    if state == 0:
        dark_overlay = cv2.addWeighted(frame, 0.3, frame, 0, 0)
        cv2.putText(dark_overlay, "It's an app that counts reps of pushups/squats", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2,
                    (255, 255, 255), 3)
        cv2.putText(dark_overlay, "Press space to continue", (100, 400), cv2.FONT_HERSHEY_SIMPLEX, 2,
                    (255, 255, 255), 3)
        cv2.imshow("exersice_counter", dark_overlay)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):
            state = 1
    elif state == 1:

        frame = cv2.flip(frame,1)

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = pose.process(img_rgb)
        if results.pose_landmarks:
            mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        cv2.putText(frame, f"Current mode: {current_mode}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 3)
        if all_landmarks_on_screen(results.pose_landmarks.landmark):

            if current_mode == "push ups" and results.pose_landmarks:
                counter_data_pushups = count_pushups(results, counter_data_pushups)
                cv2.putText(frame, f"Reps: {counter_data_pushups['count']}", (20, 115),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
                if not counter_data_pushups.get("plank_ok", True):
                    cv2.putText(frame, "Get into plank", (20, 190),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            if current_mode == "squats" and results.pose_landmarks:
                counter_data_squats = count_squats(results, counter_data_squats)
                cv2.putText(frame, f"Reps: {counter_data_squats['count']}", (20, 115),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
        else:
            cv2.putText(frame, f"Your body need to be fully in the screen", (20, 115),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
        cv2.imshow("exercise_counter", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            if mode_index == 0:
                counter_data_pushups["count"] = 0
            elif mode_index == 1:
                counter_data_squats["count"] = 0
            mode_index = (mode_index + 1) % len(mode_list)
            current_mode = mode_list[mode_index]
        elif key == ord('q'):
            break
        if mode_index == 0:
            pass
cap.release()
cv2.destroyAllWindows()
