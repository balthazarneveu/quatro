import cv2
import numpy as np
from pathlib import Path
from picamera2 import Picamera2
from picamera2.devices.imx500 import IMX500, NetworkIntrinsics
from picamera2.devices.imx500.postprocess_highernet import postprocess_higherhrnet
from picamera2.devices.imx500.postprocess import COCODrawer
from typing import Optional
from quatro.control.camera.base import CameraController


class PiCameraController(CameraController):
    """Controller implementation using Pi Camera with IMX500 AI capabilities."""

    MODEL_PATH = Path("/usr/share/imx500-models/imx500_network_higherhrnet_coco.rpk")
    WINDOW_SIZE_H_W = (480, 640)
    DETECTION_THRESHOLD = 0.3

    def __init__(
        self,
        webcam_show: bool = False,
        allow_hand_control: bool = False,
        allow_body_control: bool = True,
    ):
        """Initialize Pi Camera controller.

        Args:
            webcam_show (bool): Whether to show the webcam feed
            allow_hand_control (bool): Whether to enable hand control
            allow_body_control (bool): Whether to enable body control
        """
        super().__init__(webcam_show, allow_hand_control, allow_body_control)

        # Initialize IMX500 AI Camera
        assert self.MODEL_PATH.exists(), f"Model path {self.MODEL_PATH} does not exist."

        self.imx500 = IMX500(self.MODEL_PATH)
        self.intrinsics = self.imx500.network_intrinsics
        if not self.intrinsics:
            self.intrinsics = NetworkIntrinsics()
            self.intrinsics.task = "pose estimation"
        elif self.intrinsics.task != "pose estimation":
            raise ValueError("Network is not a pose estimation task")

        # Initialize camera with IMX500
        self.picam2 = Picamera2(self.imx500.camera_num)
        config = self.picam2.create_preview_configuration(
            controls={"FrameRate": self.intrinsics.inference_rate},
            buffer_count=12,
        )

        # Setup drawer for visualization
        if self.webcam_show:
            categories = self.intrinsics.labels
            categories = [c for c in categories if c and c != "-"]
            self.drawer = COCODrawer(
                categories, self.imx500, needs_rescale_coords=False
            )
        else:
            self.drawer = None

        # Initialize camera
        self.imx500.show_network_fw_progress_bar()

        # Set up pre-callback for AI processing
        def pre_callback(request):
            metadata = request.get_metadata()
            np_outputs = self.imx500.get_outputs(metadata=metadata, add_batch=True)
            if np_outputs is not None:
                keypoints, scores, boxes = postprocess_higherhrnet(
                    outputs=np_outputs,
                    img_size=self.WINDOW_SIZE_H_W,
                    img_w_pad=(0, 0),
                    img_h_pad=(0, 0),
                    detection_threshold=self.DETECTION_THRESHOLD,
                    network_postprocess=True,
                )
                if scores is not None and len(scores) > 0:
                    self.last_keypoints = np.reshape(
                        np.stack(keypoints, axis=0), (len(scores), 17, 3)
                    )
                    self.last_boxes = [np.array(b) for b in boxes]
                    self.last_scores = np.array(scores)

        self.picam2.pre_callback = pre_callback
        self.picam2.start(config, show_preview=False)
        self.imx500.set_auto_aspect_ratio()

        # Buffer for position data
        self.last_boxes = None
        self.last_scores = None
        self.last_keypoints = None

    def get_frame_from_webcam(self):
        """Get a frame from the camera."""
        if self.webcam_show:
            frame = self.picam2.capture_array()
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            return None

    def process_frame(self, frame: Optional[np.ndarray] = None):
        """Process a frame using IMX500 AI capabilities."""
        if frame is None:
            height, width = self.WINDOW_SIZE_H_W
        else:
            height, width = frame.shape[:2]

        # Process the last available keypoints from the AI callback
        if (
            self.last_keypoints is not None
            and self.last_scores is not None
            and len(self.last_scores) > 0
        ):

            # Process keypoints for position tracking
            xy_array = self.last_keypoints[0, ...]
            weight = xy_array[..., 2:]
            total_weight = weight.sum()

            if total_weight > 0.2:
                xy = np.sum(xy_array * weight, axis=0)
                xy = xy[0:2] / total_weight

                # Update position with normalization
                xy_normed_position = np.array([(width - xy[0]) / width, xy[1] / height])
                self.current_position = xy_normed_position[0]
                self.current_position = 0.5 + 4.0 * (self.current_position - 0.5)

                # Draw pose keypoints if display is enabled
                if self.webcam_show and self.drawer is not None:
                    for kp in self.last_keypoints[0]:
                        x, y, z = kp
                        if z > self.DETECTION_THRESHOLD:
                            cv2.circle(
                                frame,
                                (int(width - x), int(y)),
                                5,
                                (0, 0, 255),  # BGR format for display
                                -1,
                            )
            else:
                self.current_position = None

        return frame

    def get_frame_drop_frequency(self) -> int:
        """Get the frame drop frequency.

        Returns:
            int: Process every frame since we have hardware acceleration
        """
        return 1

    def release_resources(self):
        """Release camera and cleanup resources."""
        # Stop camera preview and cleanup
        if self.picam2 is not None:
            self.picam2.stop()
        cv2.destroyAllWindows()
