"""Webcam interface module for motion control."""

import cv2
from quatro.control.camera.factory import create_camera_controller

__all__ = ["Controller"]


class Controller:
    """Legacy Controller class for backward compatibility."""

    def __init__(
        self,
        webcam_show: bool = True,
        allow_hand_control: bool = False,
        allow_body_control: bool = True,
    ):
        """Initialize the Controller.

        Args:
            webcam_show (bool): Whether to show the webcam feed
            allow_hand_control (bool): Whether to enable hand control
            allow_body_control (bool): Whether to enable body control
        """
        self._controller = create_camera_controller(
            webcam_show=webcam_show,
            allow_hand_control=allow_hand_control,
            allow_body_control=allow_body_control,
        )

    def process_webcam(self):
        """Process webcam input to detect hands or body."""
        return self._controller.process_webcam()

    def release_resources(self):
        """Release camera and cleanup resources."""
        return self._controller.release_resources()

    @property
    def current_position(self):
        """Current tracked position."""
        return self._controller.current_position

    @property
    def current_action(self):
        """Current detected action."""
        return self._controller.current_action

    @property
    def hand_control(self):
        """Whether hand control is active."""
        return self._controller.hand_control

    @property
    def body_control(self):
        """Whether body control is active."""
        return self._controller.body_control


if __name__ == "__main__":
    controller = Controller(webcam_show=True)
    try:
        while True:
            controller.process_webcam()
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        controller.release_resources()
