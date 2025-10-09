"""Factory module for camera controllers."""

from typing import Optional, Type

from quatro.control.camera.base import CameraController

# Lazy imports to avoid import errors on systems without specific dependencies
_MediaPipeController = None
_PiCameraController = None


def _get_mediapipe_controller() -> Optional[Type[CameraController]]:
    """Get the MediaPipe controller class if available."""
    global _MediaPipeController
    if _MediaPipeController is None:
        try:
            import mediapipe as mp  # noqa: F401
            from quatro.control.camera.mediapipe_controller import MediaPipeController

            _MediaPipeController = MediaPipeController
        except ImportError:
            return None
    return _MediaPipeController


def _get_picamera_controller() -> Optional[Type[CameraController]]:
    """Get the Pi Camera controller class if available."""
    global _PiCameraController
    if _PiCameraController is None:
        try:
            # These imports are just to check availability
            from picamera2 import Picamera2  # type: ignore # noqa: F401
            from picamera2.devices.imx500 import IMX500  # type: ignore # noqa: F401
            from quatro.control.camera.picamera_controller import PiCameraController

            _PiCameraController = PiCameraController
        except ImportError:
            return None
    return _PiCameraController


def create_camera_controller(
    webcam_show: bool = False,
    allow_hand_control: bool = False,
    allow_body_control: bool = True,
    force_mediapipe: bool = False,
) -> CameraController:
    """Create a camera controller based on available hardware and dependencies.

    Args:
        webcam_show (bool): Whether to show the webcam feed
        allow_hand_control (bool): Whether to enable hand control
        allow_body_control (bool): Whether to enable body control
        force_mediapipe (bool): Whether to force using MediaPipe even if Pi Camera is available

    Returns:
        CameraController: The appropriate camera controller instance

    Raises:
        RuntimeError: If no suitable camera controller is available
    """
    # Try Pi Camera first unless forced to use MediaPipe
    if not force_mediapipe:
        picam_controller = _get_picamera_controller()
        if picam_controller is not None:
            return picam_controller(
                webcam_show=webcam_show,
                allow_hand_control=allow_hand_control,
                allow_body_control=allow_body_control,
            )

    # Fall back to MediaPipe
    mediapipe_controller = _get_mediapipe_controller()
    if mediapipe_controller is not None:
        return mediapipe_controller(
            webcam_show=webcam_show,
            allow_hand_control=allow_hand_control,
            allow_body_control=allow_body_control,
        )

    raise RuntimeError(
        "No suitable camera controller available. Please ensure either MediaPipe "
        "or Pi Camera with IMX500 support is installed."
    )
