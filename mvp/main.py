import cv2
import numpy as np
import time
from ultralytics import YOLO
from risk_engine import calculate_risk, risk_level
from firebase_logger import log_event

# ================= CONFIG =================
VIDEOS = [
    {"path": "video/day.mp4", "night": False, "label": "DAY MODE"},
    {"path": "video/night.mp4", "night": True, "label": "NIGHT MODE"}
]

DAY_FRAME_SKIP = 6
NIGHT_FRAME_SKIP = 2

DAY_RES = (480, 270)
NIGHT_RES = (640, 360)

DAY_DELAY = 1
NIGHT_DELAY = 30

ROAD_ID = "NH-48 | KM 32–36"

LOG_COOLDOWN_SECONDS = 5  # Prevent log spam

model = YOLO("yolov8n.pt")

# ================= UTILS =================
def is_dark(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) < 90


def enhance_night_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    clahe = cv2.createCLAHE(3.0, (8, 8))
    enhanced = clahe.apply(gray)
    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)


def auto_tune_thresholds(cap, night):
    cow_confs = []

    for _ in range(30):
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (480, 270))
        results = model(frame, conf=0.1, verbose=False)[0]

        for box in results.boxes:
            if model.names[int(box.cls[0])] == "cow":
                cow_confs.append(float(box.conf[0]))

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    avg_conf = np.mean(cow_confs) if cow_confs else 0.1
    return max(0.05, avg_conf * 0.6) if night else max(0.4, avg_conf * 0.8)


# ================= MAIN LOOP =================
for video in VIDEOS:
    cap = cv2.VideoCapture(video["path"])
    if not cap.isOpened():
        continue

    cow_conf_thresh = auto_tune_thresholds(cap, video["night"])

    frame_count = 0
    prev_vehicle_center = None
    speed = 0

    last_logged_time = 0
    last_logged_risk = None
    last_logged_warning = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        skip = NIGHT_FRAME_SKIP if video["night"] else DAY_FRAME_SKIP
        if frame_count % skip != 0:
            continue

        draw_frame = frame.copy()

        infer_frame = (
            enhance_night_frame(frame)
            if video["night"] and is_dark(frame)
            else frame
        )

        target_res = NIGHT_RES if video["night"] else DAY_RES
        infer_frame = cv2.resize(infer_frame, target_res)
        draw_frame = cv2.resize(draw_frame, target_res)

        base_conf = 0.15 if video["night"] else 0.45
        results = model(infer_frame, conf=base_conf, verbose=False)[0]

        cattle = 0
        distance = 1.0

        for box in results.boxes:
            label = model.names[int(box.cls[0])]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label == "cow" and conf >= cow_conf_thresh:
                cattle += 1
                area = max((x2 - x1) * (y2 - y1), 1)
                distance = min(distance, 1 / area)

                cv2.rectangle(draw_frame, (x1, y1), (x2, y2),
                              (0, 255, 0), 2)
                cv2.putText(draw_frame, "COW",
                            (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 1)

            if label in ["car", "bus", "truck", "motorcycle"] and conf > 0.3:
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                if prev_vehicle_center:
                    speed = int(np.hypot(cx - prev_vehicle_center[0],
                                          cy - prev_vehicle_center[1]))
                prev_vehicle_center = (cx, cy)

        if video["night"]:
            speed = int(speed * 0.7)

        score = calculate_risk(speed, distance, cattle, video["night"])
        level = risk_level(score)

        if level == "HIGH":
            cv2.putText(draw_frame,
                        "CATTLE AHEAD - SLOW DOWN",
                        (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 0, 255), 2)

        # -------- SMART LOGGING --------
        current_time = time.time()
        should_log = False

        if level != last_logged_risk:
            should_log = True

        if level == "HIGH" and not last_logged_warning:
            should_log = True

        if current_time - last_logged_time >= LOG_COOLDOWN_SECONDS:
            should_log = True

        if should_log:
            log_event({
                "road_segment": ROAD_ID,
                "mode": video["label"],
                "risk_score": score,
                "risk_level": level,
                "cattle_count": cattle,
                "warning_issued": level == "HIGH"
            })

            last_logged_time = current_time
            last_logged_risk = level
            last_logged_warning = (level == "HIGH")

        cv2.putText(draw_frame,
                    f"{video['label']} | Risk: {score} ({level})",
                    (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 1)

        cv2.imshow("Cattle Collision Prevention – MVP", draw_frame)

        delay = NIGHT_DELAY if video["night"] else DAY_DELAY
        if cv2.waitKey(delay) & 0xFF == ord("q"):
            break

    cap.release()

cv2.destroyAllWindows()
