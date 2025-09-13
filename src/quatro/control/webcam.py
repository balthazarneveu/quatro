import cv2
import numpy as np
from pathlib import Path
import traceback

PI_AI_CAMERA_AVAILABLE = False
try:
    from picamera2 import Picamera2

    PI_CAM_AVAILABLE = True
    picam2 = None
except:
    PI_CAM_AVAILABLE = False

try:
    position_buffer = []
    if PI_CAM_AVAILABLE and True:
        DETECTION_THRESHOLD = 0.3
        imx500 = None
        intrinsics = None
        drawer = None

        PI_AI_CAMERA_AVAILABLE = True
        from picamera2 import CompletedRequest, MappedArray
        from picamera2.devices.imx500 import IMX500, NetworkIntrinsics
        from picamera2.devices.imx500.postprocess_highernet import (
            postprocess_higherhrnet,
        )

        MODEL_PATH = Path(
            "/usr/share/imx500-models/imx500_network_higherhrnet_coco.rpk"
        )
        assert MODEL_PATH.exists(), f"Model path {MODEL_PATH} does not exist."
        last_boxes = None
        last_scores = None
        last_keypoints = None
        WINDOW_SIZE_H_W = (480, 640)
        from picamera2.devices.imx500.postprocess import COCODrawer

        def get_drawer():
            global intrinsics
            categories = intrinsics.labels
            categories = [c for c in categories if c and c != "-"]
            return COCODrawer(categories, imx500, needs_rescale_coords=False)

        def ai_output_tensor_parse(metadata: dict):
            """Parse the output tensor into a number of detected objects, scaled to the ISP output."""
            global last_boxes, last_scores, last_keypoints
            global imx500
            np_outputs = imx500.get_outputs(metadata=metadata, add_batch=True)
            if np_outputs is not None:
                keypoints, scores, boxes = postprocess_higherhrnet(
                    outputs=np_outputs,
                    img_size=WINDOW_SIZE_H_W,
                    img_w_pad=(0, 0),
                    img_h_pad=(0, 0),
                    detection_threshold=DETECTION_THRESHOLD,
                    network_postprocess=True,
                )

                if scores is not None and len(scores) > 0:
                    last_keypoints = np.reshape(
                        np.stack(keypoints, axis=0), (len(scores), 17, 3)
                    )
                    last_boxes = [np.array(b) for b in boxes]
                    last_scores = np.array(scores)
            return last_boxes, last_scores, last_keypoints

        def ai_output_tensor_draw(
            request: CompletedRequest, boxes, scores, keypoints, stream="main"
        ):
            """Draw the detections for this request onto the ISP output."""
            if drawer is None:
                return
            with MappedArray(request, stream) as m:
                if boxes is not None and len(boxes) > 0:
                    drawer.annotate_image(
                        m.array,
                        boxes,
                        scores,
                        np.zeros(scores.shape),
                        keypoints,
                        DETECTION_THRESHOLD,
                        DETECTION_THRESHOLD,
                        request.get_metadata(),
                        picam2,
                        stream,
                    )

        def picamera2_pre_callback(request: CompletedRequest):
            """Analyse the detected objects in the output tensor and draw them on the main output image."""
            boxes, scores, keypoints = ai_output_tensor_parse(request.get_metadata())
            global position_buffer
            position_buffer.append((boxes, scores, keypoints))
            ai_output_tensor_draw(request, boxes, scores, keypoints)

except ImportError:
    traceback.print_exc()
    print(
        "Picamera2 not available. Ensure you are running on a Raspberry Pi with Picamera2 installed."
    )
    PI_AI_CAMERA_AVAILABLE = False
if not PI_AI_CAMERA_AVAILABLE:
    import mediapipe as mp

    mp_draw = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    mp_pose = mp.solutions.pose
    keypoints_names = [e for e in mp.solutions.pose.PoseLandmark]
import time
from quatro.control.motion_detection_heuristics import HeuristicsDetector


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
        if not PI_AI_CAMERA_AVAILABLE:
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
            global picam2
            if picam2 is None:
                if not PI_AI_CAMERA_AVAILABLE:
                    picam2 = Picamera2()
                    picam2.preview_configuration.main.size = (800, 800)
                    picam2.preview_configuration.main.format = "RGB888"
                    picam2.preview_configuration.align()
                    picam2.configure("preview")
                    picam2.start()
                else:
                    global imx500
                    imx500 = IMX500(MODEL_PATH)
                    global intrinsics
                    intrinsics = imx500.network_intrinsics
                    if not intrinsics:
                        intrinsics = NetworkIntrinsics()
                        intrinsics.task = "pose estimation"
                    elif intrinsics.task != "pose estimation":
                        print("Network is not a pose estimation task")
                        exit()
                    global drawer

                    # drawer = get_drawer()
                    picam2 = Picamera2(imx500.camera_num)
                    config = picam2.create_preview_configuration(
                        controls={"FrameRate": intrinsics.inference_rate},
                        buffer_count=12,
                    )
                    imx500.show_network_fw_progress_bar()
                    picam2.start(config, show_preview=False)
                    imx500.set_auto_aspect_ratio()
                    picam2.pre_callback = picamera2_pre_callback
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
        self.previous_position = None

    def get_frame_from_webcam(self):
        if not PI_CAM_AVAILABLE:
            _, frame = self.cap.read()
        else:
            frame = self.cap.capture_array()
        return frame

    def process_webcam(self):
        """Process webcam input to detect hands or body."""
        global position_buffer

        if PI_AI_CAMERA_AVAILABLE:
            drop_frequency = (
                1  # Try running at maximum speed since the AI HW accelerator is used
            )
        else:
            drop_frequency = 2
        if self.frame_count % drop_frequency == 0:
            # Reset control flags
            self.hand_control = False
            self.body_control = False
            self.current_position = None
            frame = self.get_frame_from_webcam()
            frame = cv2.flip(frame, 1)

            if PI_AI_CAMERA_AVAILABLE:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width = rgb_frame.shape[-3:-1]
                if len(position_buffer) > 0:
                    boxes, scores, keypoints = position_buffer[-1]
                    xy_array = keypoints[0, ...]
                    weight = xy_array[..., 2:]
                    total_weight = weight.sum()
                    if total_weight <= 0.2:
                        self.current_position = None
                    else:
                        xy = np.sum(xy_array * weight, axis=0)
                        xy = xy[0:2] / total_weight

                        if scores is not None and len(scores) > 0 and self.webcam_show:
                            for kp in keypoints[0]:
                                x, y, z = kp
                                cv2.circle(
                                    rgb_frame,
                                    (int(width - x), int(y)),
                                    5,
                                    (0, 0, 255),
                                    -1,
                                )
                    xy_normed_position = np.array(
                        [(width - xy[0]) / width, xy[1] / height]
                    )
                    self.current_position = xy_normed_position[0]
                    self.current_position = 0.5 + 2.2 * (self.current_position - 0.5)
                    position_buffer = []
                    pass
            else:
                rgb_frame = frame
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
                                frame,
                                results_pose.pose_landmarks,
                                mp_pose.POSE_CONNECTIONS,
                            )
            if self.webcam_show:
                cv2.imshow("Webcam Feed", rgb_frame)
                cv2.waitKey(1)
        if self.current_position is not None:
            if self.previous_position is None:
                self.previous_position = self.current_position
            self.current_position = (
                0.7 * self.current_position + 0.3 * self.previous_position
            )
            self.previous_position = self.current_position
        self.frame_count += 1
        return

    def release_resources(self):
        """Release webcam and cleanup resources."""
        if not PI_CAM_AVAILABLE:
            self.cap.release()
        else:
            # print("Releasing Pi Camera resources.!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # self.cap.stop_preview()
            # time.sleep(1)
            # self.cap.stop()
            # time.sleep(1)
            # del self.cap
            pass
        cv2.destroyAllWindows()


if __name__ == "__main__":
    controller = Controller(webcam_show=True)
    while True:
        controller.process_webcam()
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    controller.release_resources()
