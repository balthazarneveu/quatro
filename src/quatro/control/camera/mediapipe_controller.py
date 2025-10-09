import cv2
import mediapipe as mp
import time

from quatro.control.camera.base import CameraController


class MediaPipeController(CameraController):
    """Controller implementation using MediaPipe for pose and hand detection."""

    def __init__(
        self,
        webcam_show: bool = False,
        allow_hand_control: bool = False,
        allow_body_control: bool = True,
    ):
        """Initialize MediaPipe controller.

        Args:
            webcam_show (bool): Whether to show the webcam feed
            allow_hand_control (bool): Whether to enable hand control
            allow_body_control (bool): Whether to enable body control
        """
        super().__init__(webcam_show, allow_hand_control, allow_body_control)

        # Initialize MediaPipe
        self.mp_draw = mp.solutions.drawing_utils
        self.keypoints_names = [e for e in mp.solutions.pose.PoseLandmark]

        # Initialize pose and hands if needed
        if self.allow_hand_control:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7,
            )

        if self.allow_body_control:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False, min_detection_confidence=0.7
            )

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def get_frame_from_webcam(self):
        """Get a frame from the webcam."""
        _, frame = self.cap.read()
        return frame

    def process_frame(self, frame):
        """Process a frame using MediaPipe for hand and pose detection."""
        # Process hand detection if enabled
        if self.allow_hand_control:
            results_hands = self.hands.process(frame)
            if results_hands.multi_hand_landmarks:
                for hand_landmarks in results_hands.multi_hand_landmarks:
                    index_finger_tip = hand_landmarks.landmark[8]
                    wrist = hand_landmarks.landmark[0]
                    self.hand_size = (
                        (index_finger_tip.x - wrist.x) ** 2
                        + (index_finger_tip.y - wrist.y) ** 2
                    ) ** 0.5

                    self.hand_control = self.hand_size > 0.2
                    if self.hand_control:
                        self.current_position = index_finger_tip.x

                    if self.webcam_show:
                        self.mp_draw.draw_landmarks(
                            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )

        # Process pose detection if enabled and hand control is not active
        if not self.hand_control and self.allow_body_control:
            results_pose = self.pose.process(frame)
            if results_pose.pose_landmarks:
                nose = results_pose.pose_landmarks.landmark[
                    self.mp_pose.PoseLandmark.NOSE
                ]
                self.body_control = True
                self.current_position = nose.x
                current_time = time.time()

                # Process all keypoints for motion detection
                positions = {
                    keypoint_name.name: results_pose.pose_landmarks.landmark[
                        keypoint_name
                    ]
                    for keypoint_name in self.keypoints_names
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
                    self.mp_draw.draw_landmarks(
                        frame,
                        results_pose.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                    )

        return frame

    def get_frame_drop_frequency(self) -> int:
        """Get the frame drop frequency.

        Returns:
            int: Process every other frame
        """
        return 2

    def release_resources(self):
        """Release camera and cleanup resources."""
        self.cap.release()
        cv2.destroyAllWindows()
