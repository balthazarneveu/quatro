import cv2
import logging

try:
    from picamera2 import Picamera2

    PI_CAM_AVAILABLE = True
except Exception as e:
    logging.info(f"Picamera2 not available: {e} , falling back to cv2.VideoCapture")
    PI_CAM_AVAILABLE = False
import mediapipe as mp
import time
from quatro.control.motion_detection_heuristics import HeuristicsDetector

mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
keypoints_names = [e for e in mp.solutions.pose.PoseLandmark]


class Controller:
    def __init__(
        self,
        webcam_show: bool = True,
        allow_hand_control: bool = False,
        allow_body_control: bool = True,
    ):
        self.allow_body_control = allow_body_control
        self.allow_hand_control = allow_hand_control
        assert (
            allow_hand_control or allow_body_control
        ), "At least one control mode must be enabled."
        self.frame_count = 0
        self.motion_detector = HeuristicsDetector()
        # Initialize MediaPipe hands and pose
        if allow_hand_control:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7,
            )
        if allow_body_control:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False, min_detection_confidence=0.7
            )

        # OpenCV webcam setup
        if not PI_CAM_AVAILABLE:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        else:
            picam2 = Picamera2()
            picam2.preview_configuration.main.size = (800, 800)
            picam2.preview_configuration.main.format = "RGB888"
            picam2.preview_configuration.align()
            picam2.configure("preview")
            picam2.start()
            self.cap = picam2

        # Control variables
        self.hand_position = None
        self.hand_position_y = None
        self.hand_size = None
        self.nose_position = None
        self.hand_control = False
        self.body_control = False
        self.webcam_show = webcam_show
        self.current_position = None
        self.current_action = None

    def get_frame_from_webcam(self):
        if not PI_CAM_AVAILABLE:
            _, frame = self.cap.read()
        else:
            frame = self.cap.capture_array()
        return frame

    def process_webcam(self):
        """Process webcam input to detect hands or body."""
        if True:
            # Reset control flags
            self.hand_control = False
            self.body_control = False
            self.current_position = None
            frame = self.get_frame_from_webcam()
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Hand detection
            if self.allow_hand_control:
                results_hands = self.hands.process(rgb_frame)
                if results_hands.multi_hand_landmarks:
                    for hand_landmarks in results_hands.multi_hand_landmarks:
                        index_finger_tip = hand_landmarks.landmark[8]
                        wrist = hand_landmarks.landmark[0]
                        hand_position = index_finger_tip.x
                        self.hand_size = (
                            (index_finger_tip.x - wrist.x) ** 2
                            + (index_finger_tip.y - wrist.y) ** 2
                        ) ** 0.5
                        self.hand_control = self.hand_size > 0.2
                        if self.hand_control:
                            self.current_position = hand_position
                        if self.webcam_show:
                            mp_draw.draw_landmarks(
                                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                            )

            if not self.hand_control and self.allow_body_control:
                # Body detection
                results_pose = self.pose.process(rgb_frame)
                if results_pose.pose_landmarks:

                    nose = results_pose.pose_landmarks.landmark[
                        mp.solutions.pose.PoseLandmark.NOSE
                    ]
                    # Body control only if hand control is inactive
                    self.body_control = not self.hand_control
                    self.current_position = nose.x
                    current_time = time.time()

                    positions = {
                        keypoint_name.name: results_pose.pose_landmarks.landmark[
                            keypoint_name
                        ]
                        for keypoint_name in keypoints_names
                    }

                    converted_positions = {
                        keypoint_name: (
                            position.x,
                            position.y,
                            position.z,
                            position.visibility,
                        )
                        for keypoint_name, position in positions.items()
                    }
                    self.motion_detector.infer_action(
                        converted_positions, capture_time=current_time
                    )
                    self.current_action = self.motion_detector.current_action
                    if self.webcam_show:
                        mp_draw.draw_landmarks(
                            frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS
                        )
            if self.webcam_show:
                cv2.imshow("Webcam Feed", frame)
                cv2.waitKey(1)
        self.frame_count += 1
        return

    def release_resources(self):
        """Release webcam and cleanup resources."""
        self.cap.release()
        cv2.destroyAllWindows()
