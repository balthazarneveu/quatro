from abc import ABC, abstractmethod
import cv2
from quatro.control.motion_detection_heuristics import HeuristicsDetector


class CameraController(ABC):
    def __init__(
        self,
        webcam_show: bool = False,
        allow_hand_control: bool = False,
        allow_body_control: bool = True,
    ):
        """Base camera controller class.

        Args:
            webcam_show (bool): Whether to show the webcam feed
            allow_hand_control (bool): Whether to enable hand control
            allow_body_control (bool): Whether to enable body control
        """
        self.allow_body_control = allow_body_control
        self.allow_hand_control = allow_hand_control
        assert (
            allow_hand_control or allow_body_control
        ), "At least one control mode must be enabled."

        self.frame_count = 0
        self.webcam_show = webcam_show
        self.motion_detector = HeuristicsDetector()

        # Control variables
        self.hand_position = None
        self.hand_position_y = None
        self.hand_size = None
        self.nose_position = None
        self.hand_control = False
        self.body_control = False
        self.current_position = None
        self.current_action = None
        self.previous_position = None

    @abstractmethod
    def get_frame_from_webcam(self):
        """Get a frame from the camera."""
        pass

    @abstractmethod
    def process_frame(self, frame):
        """Process a frame to detect hands/body and update control variables.

        Args:
            frame: The frame to process

        Returns:
            processed_frame: The processed frame with annotations if webcam_show is True
        """
        pass

    def process_webcam(self):
        """Process webcam input to detect hands or body."""
        if self.frame_count % self.get_frame_drop_frequency() == 0:
            # Reset control flags
            self.hand_control = False
            self.body_control = False
            self.current_position = None

            frame = self.get_frame_from_webcam()
            if frame is not None:
                frame = cv2.flip(frame, 1)

            processed_frame = self.process_frame(frame)

            if frame is not None and self.webcam_show:
                cv2.imshow("Webcam Feed", processed_frame)
                cv2.waitKey(1)

        self._update_position()
        self.frame_count += 1

    def _update_position(self):
        """Update the current position with smoothing."""
        if self.current_position is not None:
            if self.previous_position is None:
                self.previous_position = self.current_position
            self.current_position = (
                0.7 * self.current_position + 0.3 * self.previous_position
            )
            self.previous_position = self.current_position

    @abstractmethod
    def get_frame_drop_frequency(self) -> int:
        """Get the frame drop frequency for the controller.

        Returns:
            int: Number of frames to skip between processing
        """
        pass

    @abstractmethod
    def release_resources(self):
        """Release camera and cleanup resources."""
        pass
