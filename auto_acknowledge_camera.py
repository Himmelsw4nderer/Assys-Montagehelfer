import cv2
import mediapipe as mp
import requests
import os
import argparse
import math
from typing import Optional, Tuple, Any, NamedTuple
from dataclasses import dataclass


@dataclass
class GestureConfig:
    """Configuration for gesture recognition."""
    camera_device: int
    server_url: str
    acknowledgment_url: str
    swipe_threshold: float
    angle_threshold: float
    min_fingers: int
    show_debug: bool


@dataclass
class GestureState:
    """State for gesture tracking."""
    open_hand_start_pos: Optional[Tuple[float, float]] = None
    open_hand_start_size: Optional[float] = None
    gesture_cooldown: int = 0


class MediaPipeComponents(NamedTuple):
    """MediaPipe components bundle."""
    mp_hands: Any
    hands: Any
    mp_drawing: Any
    mp_drawing_styles: Any


def initialize_mediapipe_hands() -> MediaPipeComponents:
    """Initialize MediaPipe Hands module and return related objects."""
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    return MediaPipeComponents(mp_hands, hands, mp_drawing, mp_drawing_styles)


def process_frame(image, hands) -> Any:
    """Process image frame and detect hands."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return hands.process(image_rgb)


def draw_hand_triangle(image, landmarks, w, h):
    """Draw triangle for hand size calculation."""
    wrist = landmarks[0]
    index_mcp = landmarks[5]
    pinky_mcp = landmarks[17]

    wrist_px = (int(wrist.x * w), int(wrist.y * h))
    index_px = (int(index_mcp.x * w), int(index_mcp.y * h))
    pinky_px = (int(pinky_mcp.x * w), int(pinky_mcp.y * h))

    cv2.line(image, wrist_px, index_px, (255, 0, 0), 2)
    cv2.line(image, wrist_px, pinky_px, (255, 0, 0), 2)
    cv2.line(image, index_px, pinky_px, (255, 0, 0), 2)


def draw_hand_center(image, landmarks, w, h):
    """Draw hand center point."""
    hand_center = calculate_hand_center(landmarks)
    center_px = (int(hand_center[0] * w), int(hand_center[1] * h))
    cv2.circle(image, center_px, 5, (0, 255, 255), -1)


def draw_finger_debug_info(image, landmarks):
    """Draw finger extension debug information."""
    finger_states = check_finger_extensions(landmarks)
    for i, (finger_name, is_extended) in enumerate(finger_states.items()):
        color = (0, 255, 0) if is_extended else (0, 0, 255)
        status = 'Y' if is_extended else 'N'
        cv2.putText(image, f"{finger_name}: {status}",
                   (10, 150 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


def draw_debug_information(image, hand_landmarks, show_debug):
    """Draw debug information for hand tracking."""
    if not show_debug:
        return

    landmarks = hand_landmarks.landmark
    h, w, _ = image.shape

    draw_hand_triangle(image, landmarks, w, h)
    draw_hand_center(image, landmarks, w, h)
    draw_finger_debug_info(image, landmarks)


def draw_basic_landmarks(image, hand_landmarks, mp_hands, mp_drawing, mp_drawing_styles):
    """Draw basic hand landmarks."""
    mp_drawing.draw_landmarks(
        image,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing_styles.get_default_hand_landmarks_style(),
        mp_drawing_styles.get_default_hand_connections_style()
    )


def draw_hand_landmarks(image, results, mp_hands, mp_drawing, mp_drawing_styles, show_debug=False) -> None:
    """Draw landmarks on detected hands with optional debug information."""
    if not results.multi_hand_landmarks:
        return

    for hand_landmarks in results.multi_hand_landmarks:
        draw_basic_landmarks(image, hand_landmarks, mp_hands, mp_drawing, mp_drawing_styles)
        draw_debug_information(image, hand_landmarks, show_debug)


def calculate_euclidean_distance(point1, point2) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def calculate_hand_size(landmarks) -> float:
    """Calculate hand size using triangle formed by wrist and finger bases."""
    wrist = landmarks.landmark[0]
    index_mcp = landmarks.landmark[5]
    pinky_mcp = landmarks.landmark[17]

    distances = [
        calculate_euclidean_distance(wrist, index_mcp),
        calculate_euclidean_distance(wrist, pinky_mcp),
        calculate_euclidean_distance(index_mcp, pinky_mcp)
    ]

    return max(distances)


def check_thumb_extension(landmarks) -> bool:
    """Check if thumb is extended."""
    thumb_tip = landmarks.landmark[4]
    thumb_mcp = landmarks.landmark[2]
    wrist = landmarks.landmark[0]

    thumb_tip_dist = calculate_euclidean_distance(wrist, thumb_tip)
    thumb_mcp_dist = calculate_euclidean_distance(wrist, thumb_mcp)
    return thumb_tip_dist > thumb_mcp_dist * 1.1


def check_finger_extension(landmarks, tip_idx, pip_idx) -> bool:
    """Check if a finger is extended by comparing tip and PIP positions."""
    tip = landmarks.landmark[tip_idx]
    pip = landmarks.landmark[pip_idx]
    return tip.y < pip.y


def check_finger_extensions(landmarks) -> dict:
    """Check which fingers are extended using a more robust method."""
    return {
        'Thumb': check_thumb_extension(landmarks),
        'Index': check_finger_extension(landmarks, 8, 6),
        'Middle': check_finger_extension(landmarks, 12, 10),
        'Ring': check_finger_extension(landmarks, 16, 14),
        'Pinky': check_finger_extension(landmarks, 20, 18)
    }


def is_hand_open(landmarks, min_fingers_extended=3) -> bool:
    """Determine if hand is open by checking finger extensions."""
    finger_states = check_finger_extensions(landmarks)
    extended_count = sum(1 for is_extended in finger_states.values() if is_extended)
    return extended_count >= min_fingers_extended


def calculate_hand_center(landmarks) -> Tuple[float, float]:
    """Calculate the center point of the hand using triangle centroid."""
    wrist = landmarks.landmark[0]
    index_mcp = landmarks.landmark[5]
    pinky_mcp = landmarks.landmark[17]

    center_x = (wrist.x + index_mcp.x + pinky_mcp.x) / 3
    center_y = (wrist.y + index_mcp.y + pinky_mcp.y) / 3
    return center_x, center_y


def calculate_swipe_metrics(start_pos: Tuple[float, float], end_pos: Tuple[float, float],
                          hand_size: float) -> Tuple[float, float, float]:
    """Calculate swipe distance, scaled distance, and angle."""
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]

    distance = math.sqrt(dx**2 + dy**2)
    scaled_distance = distance / hand_size if hand_size > 0 else 0

    angle_rad = math.atan2(abs(dy), abs(dx))
    angle_deg = math.degrees(angle_rad)

    return scaled_distance, angle_deg, dx


def determine_swipe_direction(dx: float, scaled_distance: float, angle_deg: float) -> Optional[str]:
    """Determine swipe direction based on movement."""
    if dx < 0:
        print(f"RIGHT TO LEFT SWIPE: distance={scaled_distance:.2f}, angle={angle_deg:.1f}°")
        return "next"
    else:
        print(f"LEFT TO RIGHT SWIPE: distance={scaled_distance:.2f}, angle={angle_deg:.1f}°")
        return "back"


def detect_swipe_gesture(start_pos: Tuple[float, float], end_pos: Tuple[float, float],
                        hand_size: float, swipe_threshold: float = 2.0,
                        angle_threshold: float = 30.0) -> Optional[str]:
    """Detect swipe gesture from start and end positions."""
    scaled_distance, angle_deg, dx = calculate_swipe_metrics(start_pos, end_pos, hand_size)

    if scaled_distance < swipe_threshold:
        return None

    if angle_deg > angle_threshold:
        return None

    return determine_swipe_direction(dx, scaled_distance, angle_deg)


def test_server_connection(server_url: str) -> bool:
    """Test server connection and return success status."""
    try:
        requests.get(server_url, timeout=2)
        return True
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Server connection test failed: {e}")
        print(f"⚠️ Make sure the server is running at {server_url}")
        return False


def send_http_request(url: str, payload: dict) -> bool:
    """Send HTTP POST request with payload."""
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=5)

        print(f"HTTP request sent with direction '{payload['direction']}'. Response: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            print(f"✅ Successfully sent {payload['direction']} gesture to server")
            return True
        else:
            print(f"❌ Server returned error code: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Request timed out: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to send HTTP request: {e}")
        return False


def get_server_url(url: str) -> str:
    """Get server URL, using default if none provided."""
    if url:
        return url.split('/auto_acknowledge')[0]

    server_url = os.environ.get("ASSYS_SERVER_URL", "http://192.168.178.130:5000")
    return server_url


def send_acknowledge_request(url: str = "", direction: str = "next") -> bool:
    """Send HTTP POST request to acknowledge endpoint with specified direction."""
    server_url = get_server_url(url)

    if not url:
        url = f"{server_url}/auto_acknowledge"
        print(f"Using server URL: {url}")

    if not test_server_connection(server_url):
        return False

    payload = {"type": "gesture", "direction": direction}
    print(f"Sending request to: {url}")
    print(f"Payload: {payload}")

    return send_http_request(url, payload)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Camera-based gesture recognition for auto-acknowledgment')
    parser.add_argument('--camera', '-c', type=int, default=0,
                        help='Camera device number (default: 0)')
    parser.add_argument('--server-url', '-s', type=str,
                        default=os.environ.get('ASSYS_SERVER_URL', 'http://192.168.178.130:5000'),
                        help='Server URL for acknowledgment (default: from ASSYS_SERVER_URL env or http://192.168.178.130:5000)')
    parser.add_argument('--endpoint', '-e', type=str, default='/auto_acknowledge',
                        help='Endpoint for acknowledgment (default: /auto_acknowledge)')
    parser.add_argument('--swipe-threshold', '-t', type=float, default=2.0,
                        help='Minimum scaled movement to detect a swipe (default: 2.0)')
    parser.add_argument('--angle-threshold', '-a', type=float, default=30.0,
                        help='Maximum angle from horizontal for swipe detection (default: 30.0 degrees)')
    parser.add_argument('--min-fingers', '-mf', type=int, default=3,
                        help='Minimum fingers extended for open hand detection (default: 3)')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Show visual debug information (hand landmarks, distances)')
    return parser.parse_args()


def check_module_installation(module_name: str, display_name: str) -> None:
    """Check if a module is installed and print version or error."""
    try:
        module = __import__(module_name)
        print(f"{display_name} version: {module.__version__}")
    except ImportError:
        print(f"❌ {display_name} module not installed! Required for functionality.")


def verify_environment() -> None:
    """Check environment and print diagnostic information."""
    print("\n===== Environment Check =====")
    print(f"ASSYS_SERVER_URL: {os.environ.get('ASSYS_SERVER_URL', '(not set)')}")

    check_module_installation('requests', 'requests')
    check_module_installation('cv2', 'OpenCV')
    check_module_installation('mediapipe', 'MediaPipe')

    print("============================\n")


def get_camera_device(args) -> int:
    """Get camera device from arguments or environment variable."""
    camera_device = args.camera
    if 'CAMERA_DEVICE' in os.environ:
        try:
            camera_device = int(os.environ['CAMERA_DEVICE'])
        except ValueError:
            print(f"Warning: Invalid CAMERA_DEVICE environment variable. Using default: {camera_device}")
    return camera_device


def create_gesture_config(args) -> GestureConfig:
    """Create gesture configuration from arguments."""
    camera_device = get_camera_device(args)
    server_url = args.server_url
    acknowledgment_url = f"{server_url}{args.endpoint}"

    return GestureConfig(
        camera_device=camera_device,
        server_url=server_url,
        acknowledgment_url=acknowledgment_url,
        swipe_threshold=args.swipe_threshold,
        angle_threshold=args.angle_threshold,
        min_fingers=args.min_fingers,
        show_debug=args.debug
    )


def print_startup_info(config: GestureConfig) -> None:
    """Print startup information."""
    print(f"Starting camera recognition with device {config.camera_device}")
    print(f"Using acknowledgment URL: {config.acknowledgment_url}")
    print(f"Environment URL: {os.environ.get('ASSYS_SERVER_URL', '(not set)')}")
    print(f"Swipe threshold: {config.swipe_threshold}")
    print(f"Angle threshold: {config.angle_threshold}°")
    print(f"Minimum fingers for open hand: {config.min_fingers}")
    print(f"Debug mode: {config.show_debug}")


def test_server_connection_at_startup(config: GestureConfig) -> None:
    """Test server connection at startup and print status."""
    print("\nTesting connection to server...")
    try:
        response = requests.get(config.server_url, timeout=2)
        if response.status_code == 200:
            print("✅ Server connection successful!")
        else:
            print(f"⚠️ Server returned status code {response.status_code}")
            print("⚠️ Swipe gestures may not work correctly")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server at {config.server_url}")
        print(f"❌ Error: {e}")
        print("❌ Swipe gestures will not work until server connection is fixed")
        print("ℹ️ To change server URL: export ASSYS_SERVER_URL=http://your-server-ip:5000")


def initialize_camera(camera_device: int) -> Tuple[Optional[cv2.VideoCapture], Optional[Tuple[int, int]]]:
    """Initialize camera and return capture object and frame dimensions."""
    cap = cv2.VideoCapture(camera_device)
    _, first_frame = cap.read()

    if first_frame is None:
        print("Error: Could not read from camera.")
        return None, None

    frame_height, frame_width, _ = first_frame.shape
    return cap, (frame_width, frame_height)


def draw_tracking_line(image, start_pos, current_pos, frame_width, frame_height, color, thickness=3):
    """Draw tracking line between two positions."""
    start_px = (int(start_pos[0] * frame_width), int(start_pos[1] * frame_height))
    current_px = (int(current_pos[0] * frame_width), int(current_pos[1] * frame_height))
    cv2.line(image, start_px, current_px, color, thickness)


def draw_hand_status(image, is_open: bool, hand_center=None, hand_size=None, show_debug=False):
    """Draw hand status information on image."""
    font = cv2.FONT_HERSHEY_SIMPLEX

    if is_open:
        cv2.putText(image, "OPEN HAND", (10, 70), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        if show_debug and hand_center and hand_size:
            cv2.putText(image, f"Size: {hand_size:.3f}", (10, 100), font, 0.6, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f"Center: ({hand_center[0]:.2f}, {hand_center[1]:.2f})",
                       (10, 120), font, 0.6, (255, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(image, "CLOSED HAND", (10, 70), font, 0.8, (0, 0, 255), 2, cv2.LINE_AA)


def handle_open_hand(image, hand_landmarks, state: GestureState, config: GestureConfig,
                    frame_width: int, frame_height: int) -> None:
    """Handle open hand detection and tracking."""
    hand_center = calculate_hand_center(hand_landmarks)
    hand_size = calculate_hand_size(hand_landmarks)

    if state.open_hand_start_pos is None:
        state.open_hand_start_pos = hand_center
        state.open_hand_start_size = hand_size
        print("Open hand detected - starting gesture tracking")

    if state.open_hand_start_pos and config.show_debug:
        draw_tracking_line(image, state.open_hand_start_pos, hand_center,
                          frame_width, frame_height, (0, 255, 255))

    draw_hand_status(image, True, hand_center, hand_size, config.show_debug)


def handle_gesture_detection(image, hand_landmarks, state: GestureState, config: GestureConfig,
                           frame_width: int, frame_height: int) -> None:
    """Handle gesture detection when hand is closed."""
    if not (state.open_hand_start_pos and state.gesture_cooldown <= 0 and state.open_hand_start_size):
        return

    final_hand_center = calculate_hand_center(hand_landmarks)

    if config.show_debug:
        draw_tracking_line(image, state.open_hand_start_pos, final_hand_center,
                          frame_width, frame_height, (255, 0, 255))

    swipe_direction = detect_swipe_gesture(
        state.open_hand_start_pos, final_hand_center, state.open_hand_start_size,
        config.swipe_threshold, config.angle_threshold
    )

    if swipe_direction:
        print(f"Swipe {swipe_direction} detected. Sending acknowledgment...")
        request_success = send_acknowledge_request(config.acknowledgment_url, swipe_direction)
        state.gesture_cooldown = 60

        color = (0, 255, 0) if request_success else (0, 0, 255)
        status_text = "✓" if request_success else "✗"
        direction_text = f"Swipe {swipe_direction.upper()} {status_text}"
        cv2.putText(image, direction_text, (frame_width//2 - 150, frame_height - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)


def handle_closed_hand(image, hand_landmarks, state: GestureState, config: GestureConfig,
                      frame_width: int, frame_height: int) -> None:
    """Handle closed hand detection and gesture processing."""
    draw_hand_status(image, False)
    handle_gesture_detection(image, hand_landmarks, state, config, frame_width, frame_height)

    state.open_hand_start_pos = None
    state.open_hand_start_size = None


def handle_no_hand_detected(state: GestureState) -> None:
    """Handle case when no hand is detected."""
    if state.open_hand_start_pos and state.gesture_cooldown <= 0:
        print("Hand lost - checking for swipe gesture")
        state.open_hand_start_pos = None
        state.open_hand_start_size = None


def draw_cooldown_timer(image, gesture_cooldown: int, frame_height: int) -> None:
    """Draw cooldown timer on image."""
    if gesture_cooldown <= 0:
        return

    remaining_time = gesture_cooldown / 20.0
    cv2.putText(image, f"Cooldown: {remaining_time:.1f}s", (10, frame_height - 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA)


def process_frame_with_hands(image, results, mp_components: MediaPipeComponents,
                           state: GestureState, config: GestureConfig,
                           frame_width: int, frame_height: int) -> None:
    """Process frame when hands are detected."""
    hand_landmarks = results.multi_hand_landmarks[0]
    draw_hand_landmarks(image, results, mp_components.mp_hands,
                       mp_components.mp_drawing, mp_components.mp_drawing_styles, config.show_debug)

    if is_hand_open(hand_landmarks, config.min_fingers):
        handle_open_hand(image, hand_landmarks, state, config, frame_width, frame_height)
    else:
        handle_closed_hand(image, hand_landmarks, state, config, frame_width, frame_height)


def run_main_loop(cap, mp_components: MediaPipeComponents, config: GestureConfig,
                 frame_width: int, frame_height: int) -> None:
    """Run the main processing loop."""
    state = GestureState()
    font = cv2.FONT_HERSHEY_SIMPLEX
    instruction_text = "Open hand and swipe: Left = Next | Right = Back | Q = Quit"

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        results = process_frame(image, mp_components.hands)
        cv2.putText(image, instruction_text, (10, 30), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        if results and results.multi_hand_landmarks:
            process_frame_with_hands(image, results, mp_components, state, config, frame_width, frame_height)
        else:
            handle_no_hand_detected(state)

        state.gesture_cooldown = max(0, state.gesture_cooldown - 1)
        draw_cooldown_timer(image, state.gesture_cooldown, frame_height)

        cv2.imshow('MediaPipe Hand Gesture Recognition', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break


def main() -> None:
    """Main function to run hand detection and tracking."""
    verify_environment()
    args = parse_arguments()
    config = create_gesture_config(args)

    print_startup_info(config)
    test_server_connection_at_startup(config)

    mp_components = initialize_mediapipe_hands()
    cap, frame_dimensions = initialize_camera(config.camera_device)

    if not cap or not frame_dimensions:
        return

    frame_width, frame_height = frame_dimensions

    try:
        run_main_loop(cap, mp_components, config, frame_width, frame_height)
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
