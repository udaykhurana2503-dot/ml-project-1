import cv2
import mediapipe as mp
import urllib.request
import os
import pyautogui
import time
import pygetwindow as gw

# ============================================================
# SETTINGS
# ============================================================

last_action_time = 0
COOLDOWN = 1.5

# PowerPoint window keyword
POWERPOINT_KEYWORD = "PowerPoint"


# ============================================================
# FUNCTION: ACTIVATE POWERPOINT
# ============================================================

def activate_powerpoint():

    windows = gw.getWindowsWithTitle(POWERPOINT_KEYWORD)

    if not windows:
        print("PowerPoint window not found.")
        return False

    try:
        powerpoint_window = windows[0]

        if powerpoint_window.isMinimized:
            powerpoint_window.restore()

        powerpoint_window.activate()

        time.sleep(0.2)

        return True

    except Exception as e:
        print("Could not activate PowerPoint:", e)

        return False


# ============================================================
# FUNCTION: NEXT SLIDE
# ============================================================

def next_slide():

    if activate_powerpoint():

        pyautogui.press("right")

        print(">>> NEXT SLIDE")


# ============================================================
# FUNCTION: PREVIOUS SLIDE
# ============================================================

def previous_slide():

    if activate_powerpoint():

        pyautogui.press("left")

        print("<<< PREVIOUS SLIDE")


# ============================================================
# 1. DOWNLOAD MEDIAPIPE HAND LANDMARKER MODEL
# ============================================================

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

MODEL_PATH = "hand_landmarker.task"


if not os.path.exists(MODEL_PATH):

    print("Downloading hand tracking model...")

    urllib.request.urlretrieve(
        MODEL_URL,
        MODEL_PATH
    )

    print("Model downloaded successfully.")


# ============================================================
# 2. INITIALIZE MEDIAPIPE
# ============================================================

BaseOptions = mp.tasks.BaseOptions

VisionRunningMode = mp.tasks.vision.RunningMode

HandLandmarker = mp.tasks.vision.HandLandmarker

HandLandmarkerOptions = (
    mp.tasks.vision.HandLandmarkerOptions
)


options = HandLandmarkerOptions(

    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),

    running_mode=VisionRunningMode.VIDEO,

    num_hands=1,

    min_hand_detection_confidence=0.7,

    min_hand_presence_confidence=0.7,

    min_tracking_confidence=0.7
)


# ============================================================
# 3. GESTURE DETECTION
# ============================================================

def detect_gesture(landmarks, handedness):

    # --------------------------------------------------------
    # Finger landmarks
    # --------------------------------------------------------

    index_tip = landmarks[8]
    index_pip = landmarks[6]

    middle_tip = landmarks[12]
    middle_pip = landmarks[10]

    ring_tip = landmarks[16]
    ring_pip = landmarks[14]

    pinky_tip = landmarks[20]
    pinky_pip = landmarks[18]


    # --------------------------------------------------------
    # Check whether fingers are raised
    # --------------------------------------------------------

    index_up = index_tip.y < index_pip.y

    middle_up = middle_tip.y < middle_pip.y

    ring_up = ring_tip.y < ring_pip.y

    pinky_up = pinky_tip.y < pinky_pip.y


    # ========================================================
    # FIST
    # ========================================================

    if (
        not index_up
        and not middle_up
        and not ring_up
        and not pinky_up
    ):

        return "Fist"


    # ========================================================
    # OPEN PALM
    # ========================================================

    if (
        index_up
        and middle_up
        and ring_up
        and pinky_up
    ):

        return "Open Palm"


    # ========================================================
    # POINTING UP
    # ========================================================

    if (
        index_up
        and not middle_up
        and not ring_up
        and not pinky_up
    ):

        # ----------------------------------------------------
        # Check vertical direction
        # ----------------------------------------------------

        dy = index_tip.y - index_pip.y

        # MediaPipe Y increases downward.
        # Negative dy means the finger points upward.

        if dy < -0.05:

            return "Pointing Up"

        else:

            return "Pointing"


    # ========================================================
    # OTHER HAND SHAPE
    # ========================================================

    return "Custom Hand Shape"


# ============================================================
# 4. DRAW HAND
# ============================================================

def draw_hand(frame, landmarks):

    h, w, _ = frame.shape


    # --------------------------------------------------------
    # Draw landmarks
    # --------------------------------------------------------

    for landmark in landmarks:

        x = int(landmark.x * w)

        y = int(landmark.y * h)

        cv2.circle(
            frame,
            (x, y),
            5,
            (0, 255, 0),
            -1
        )


    # --------------------------------------------------------
    # Hand connections
    # --------------------------------------------------------

    connections = [

        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),

        (0, 5),
        (5, 6),
        (6, 7),
        (7, 8),

        (5, 9),
        (9, 10),
        (10, 11),
        (11, 12),

        (9, 13),
        (13, 14),
        (14, 15),
        (15, 16),

        (13, 17),
        (17, 18),
        (18, 19),
        (19, 20),

        (0, 17)
    ]


    # --------------------------------------------------------
    # Draw connections
    # --------------------------------------------------------

    for start, end in connections:

        x1 = int(landmarks[start].x * w)

        y1 = int(landmarks[start].y * h)

        x2 = int(landmarks[end].x * w)

        y2 = int(landmarks[end].y * h)

        cv2.line(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 255, 255),
            2
        )


# ============================================================
# 5. START CAMERA
# ============================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("ERROR: Could not open webcam.")

    exit()


# ============================================================
# PROGRAM INFORMATION
# ============================================================

print("----------------------------------------")
print("HAND GESTURE POWERPOINT CONTROLLER")
print("----------------------------------------")
print()

print("Fist         = NEXT SLIDE")
print("Pointing Up  = PREVIOUS SLIDE")

print()

print("Press Q to exit.")

print()


# ============================================================
# 6. CREATE HAND LANDMARKER
# ============================================================

with HandLandmarker.create_from_options(options) as landmarker:

    frame_timestamp_ms = 0


    # ========================================================
    # MAIN LOOP
    # ========================================================

    while cap.isOpened():

        success, frame = cap.read()


        # ----------------------------------------------------
        # Check camera frame
        # ----------------------------------------------------

        if not success:

            print("Could not read camera frame.")

            continue


        # ----------------------------------------------------
        # Mirror camera
        # ----------------------------------------------------

        frame = cv2.flip(frame, 1)


        # ----------------------------------------------------
        # BGR → RGB
        # ----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # ----------------------------------------------------
        # Create MediaPipe image
        # ----------------------------------------------------

        mp_image = mp.Image(

            image_format=mp.ImageFormat.SRGB,

            data=rgb_frame
        )


        # ----------------------------------------------------
        # Timestamp
        # ----------------------------------------------------

        frame_timestamp_ms += 33


        # ----------------------------------------------------
        # Detect hand
        # ----------------------------------------------------

        result = landmarker.detect_for_video(

            mp_image,

            frame_timestamp_ms
        )


        # Default gesture

        gesture_text = "Scanning..."


        # ====================================================
        # PROCESS HAND
        # ====================================================

        if result.hand_landmarks:

            for i, hand_landmarks in enumerate(
                result.hand_landmarks
            ):


                # ------------------------------------------------
                # Draw hand
                # ------------------------------------------------

                draw_hand(
                    frame,
                    hand_landmarks
                )


                # ------------------------------------------------
                # Handedness
                # ------------------------------------------------

                if result.handedness:

                    handedness = (
                        result.handedness[i][0].category_name
                    )

                else:

                    handedness = "Unknown"


                # ------------------------------------------------
                # Detect gesture
                # ------------------------------------------------

                gesture_text = detect_gesture(

                    hand_landmarks,

                    handedness
                )


                # =================================================
                # POWERPOINT CONTROL
                # =================================================

                current_time = time.time()


                if (
                    current_time - last_action_time
                    > COOLDOWN
                ):


                    # ---------------------------------------------
                    # FIST → NEXT SLIDE
                    # ---------------------------------------------

                    if gesture_text == "Fist":

                        next_slide()

                        last_action_time = current_time


                    # ---------------------------------------------
                    # POINTING UP → PREVIOUS SLIDE
                    # ---------------------------------------------

                    elif gesture_text == "Pointing Up":

                        previous_slide()

                        last_action_time = current_time


        # ====================================================
        # DISPLAY GESTURE
        # ====================================================

        cv2.rectangle(

            frame,

            (10, 10),

            (570, 115),

            (0, 0, 0),

            -1
        )


        # ----------------------------------------------------
        # Gesture text
        # ----------------------------------------------------

        cv2.putText(

            frame,

            f"Gesture: {gesture_text}",

            (25, 65),

            cv2.FONT_HERSHEY_SIMPLEX,

            1.2,

            (0, 255, 0),

            3,

            cv2.LINE_AA
        )


        # ----------------------------------------------------
        # Instructions
        # ----------------------------------------------------

        cv2.putText(

            frame,

            "Fist = Next | Point Up = Previous",

            (25, 98),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (255, 255, 255),

            2,

            cv2.LINE_AA
        )


        # ====================================================
        # CAMERA WINDOW
        # ====================================================

        cv2.imshow(

            "Hand Gesture Detection System",

            frame
        )


        # ====================================================
        # Q = EXIT
        # ====================================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()


print()

print("Hand Gesture PowerPoint Controller Stopped.")