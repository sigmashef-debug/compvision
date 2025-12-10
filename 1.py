import cv2
import mediapipe as mp
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose()
mode_list = ["push ups", "squats"]
mode_index = 0
current_mode = mode_list[mode_index]
counter_data_pushups = {"count": 0, "stage": "up", "plank_ok": False}
counter_data_squats = {"count": 0, "stage": "up"}
cap = cv2.VideoCapture(0)
def count_pushups(results, counter_data):
    lm = results.pose_landmarks.landmark
    shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    elbow = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]
    hip = lm[mp_pose.PoseLandmark.LEFT_HIP.value]

    if abs(shoulder.y - hip.y) > 0.11:
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

    # Push‑up logic
    if angle < 70 and counter_data["stage"] == "up":
        counter_data["stage"] = "down"
    if angle > 160 and counter_data["stage"] == "down":
        counter_data["stage"] = "up"
        counter_data["count"] += 1

    return counter_data
while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame,1)

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(img_rgb)
    if results.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    cv2.putText(frame, f"Current mode: {current_mode}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    if current_mode == "push ups" and results.pose_landmarks:
        counter_data_pushups = count_pushups(results, counter_data_pushups)
        cv2.putText(frame, f"Reps: {counter_data_pushups['count']}", (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        if not counter_data_pushups.get("plank_ok", True):
            cv2.putText(frame, "Get into plank", (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    if current_mode == "squats" and results.pose_landmarks:
        pass
    cv2.imshow("Pose", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        if mode_index == 0:
            counter_data_pushups["count"] = 0
        mode_index = (mode_index + 1) % len(mode_list)
        current_mode = mode_list[mode_index]
    elif key == ord('q'):
        break
    if mode_index == 0:
        pass
cap.release()
cv2.destroyAllWindows()