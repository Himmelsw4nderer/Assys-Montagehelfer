import cv2
import mediapipe as mp
import requests
import time
import os
import argparse
from typing import Optional, Tuple, Any, List, Dict


def initialize_mediapipe_hands() -> Tuple:
    """Initialize MediaPipe Hands module and return related objects."""
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,  # Just track one hand for swipe gesture
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    return mp_hands, hands, mp_drawing, mp_drawing_styles


def process_frame(image, hands) -> Any:
    """Process image frame and detect hands."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return hands.process(image_rgb)


def draw_hand_landmarks(image, results, mp_hands, mp_drawing, mp_drawing_styles) -> None:
    """Draw landmarks on detected hands."""
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )


def send_acknowledge_request(url: str = "", direction: str = "next") -> bool:
    """Send HTTP POST request to acknowledge endpoint with specified direction."""
    # Use default URL if none provided
    if not url:
        # Get from environment variable or default to the known IP address
        server_url = os.environ.get("ASSYS_SERVER_URL", "http://192.168.178.130:5000")
        url = f"{server_url}/auto_acknowledge"
        print(f"Using server URL: {url}")

    try:
        # First try to connect to the server to see if it's reachable
        try:
            # Timeout after 2 seconds to avoid hanging
            requests.get(server_url.split('/auto_acknowledge')[0], timeout=2)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Server connection test failed: {e}")
            print(f"⚠️ Make sure the server is running at {server_url}")
            return False

        # Send gesture-specific payload with direction
        payload = {"type": "gesture", "direction": direction}
        headers = {"Content-Type": "application/json"}
        print(f"Sending request to: {url}")
        print(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=headers, timeout=5)
        print(f"HTTP request sent with direction '{direction}'. Response: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            print(f"✅ Successfully sent {direction} gesture to server")
            return True
        else:
            print(f"❌ Server returned error code: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print(f"⚠️ Check if the server is running at {url}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Request timed out: {e}")
        print(f"⚠️ Server may be slow to respond at {url}")
        return False
    except Exception as e:
        print(f"❌ Failed to send HTTP request: {e}")
        print(f"⚠️ Server URL: {url}")
        return False


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
    parser.add_argument('--hand-duration', '-d', type=float, default=0.75,
                        help='Duration hand must be visible before acknowledgment (default: 0.75 seconds)')
    parser.add_argument('--swipe-threshold', '-t', type=int, default=100,
                        help='Minimum horizontal movement to detect a swipe (default: 100 pixels)')
    return parser.parse_args()

def get_hand_position(landmarks) -> Tuple[float, float]:
    """Extract the average position of the hand from landmarks."""
    if not landmarks:
        return 0, 0

    # Get the palm center as average of certain landmarks
    index_base = landmarks.landmark[5]  # Index finger MCP
    wrist = landmarks.landmark[0]       # Wrist

    x = (index_base.x + wrist.x) / 2
    y = (index_base.y + wrist.y) / 2

    print(f"Hand position: x={x:.2f}, y={y:.2f}")
    return x, y

def detect_swipe(positions: List[Dict], swipe_threshold: int, frame_width: int) -> Optional[str]:
    """Detect horizontal swipe gesture from a series of hand positions.

    Args:
        positions: List of hand position dictionaries with x,y coordinates
        swipe_threshold: Minimum horizontal movement to be considered a swipe
        frame_width: Width of the camera frame for calculating relative movement

    Returns:
        "next" for right-to-left swipe, "back" for left-to-right swipe, None if no swipe detected
    """
    if len(positions) < 5:  # Need enough points to detect a swipe
        return None

    # Convert relative x positions (0-1) to pixel coordinates
    start_x = positions[0]["x"] * frame_width
    end_x = positions[-1]["x"] * frame_width

    # Calculate horizontal movement
    x_movement = end_x - start_x

    print(f"Swipe detection: movement={x_movement:.2f}px, threshold={swipe_threshold}px")

    # Check if the movement exceeds the threshold
    if abs(x_movement) >= swipe_threshold:
        if x_movement < 0:  # Moving right to left
            print(f"RIGHT TO LEFT SWIPE DETECTED: {x_movement:.2f}px")
            return "next"
        else:               # Moving left to right
            print(f"LEFT TO RIGHT SWIPE DETECTED: {x_movement:.2f}px")
            return "back"

    return None

def verify_environment() -> None:
    """Check environment and print diagnostic information."""
    print("\n===== Environment Check =====")
    print(f"ASSYS_SERVER_URL: {os.environ.get('ASSYS_SERVER_URL', '(not set)')}")

    # Check if Python requests module is properly installed
    try:
        import requests
        print(f"requests version: {requests.__version__}")
    except ImportError:
        print("❌ requests module not installed! Required for HTTP communication.")

    # Check if OpenCV is properly installed
    try:
        import cv2
        print(f"OpenCV version: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV (cv2) module not installed! Required for camera access.")

    # Check if MediaPipe is properly installed
    try:
        import mediapipe as mp
        print(f"MediaPipe version: {mp.__version__}")
    except ImportError:
        print("❌ MediaPipe module not installed! Required for hand tracking.")

    print("============================\n")
    
def main() -> None:
    # Run environment check at startup
    verify_environment()
    """Main function to run hand detection and tracking."""
    # Parse command line arguments
    args = parse_arguments()

    # Get camera device from arguments or environment variable
    camera_device = args.camera
    if 'CAMERA_DEVICE' in os.environ:
        try:
            camera_device = int(os.environ['CAMERA_DEVICE'])
        except ValueError:
            print(f"Warning: Invalid CAMERA_DEVICE environment variable. Using default: {camera_device}")

    # Get acknowledgment URL and parameters
    server_url = args.server_url
    acknowledgment_url = f"{server_url}{args.endpoint}"
    hand_duration = args.hand_duration
    swipe_threshold = args.swipe_threshold

    print(f"Starting camera recognition with device {camera_device}")
    print(f"Using acknowledgment URL: {acknowledgment_url}")
    print(f"Environment URL: {os.environ.get('ASSYS_SERVER_URL', '(not set)')}")
    print(f"Hand duration threshold: {hand_duration} seconds")
    print(f"Swipe threshold: {swipe_threshold} pixels")

    # Test server connection at startup
    print("\nTesting connection to server...")
    try:
        response = requests.get(server_url, timeout=2)
        if response.status_code == 200:
            print(f"✅ Server connection successful!")
        else:
            print(f"⚠️ Server returned status code {response.status_code}")
            print(f"⚠️ Swipe gestures may not work correctly")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server at {server_url}")
        print(f"❌ Error: {e}")
        print(f"❌ Swipe gestures will not work until server connection is fixed")
        print(f"ℹ️ To change server URL: export ASSYS_SERVER_URL=http://your-server-ip:5000")

    # Initialize MediaPipe components
    mp_hands, hands, mp_drawing, mp_drawing_styles = initialize_mediapipe_hands()
    cap = cv2.VideoCapture(camera_device)

    # Get frame dimensions
    _, first_frame = cap.read()
    if first_frame is None:
        print("Error: Could not read from camera.")
        return
    frame_height, frame_width, _ = first_frame.shape

    # Track hand positions over time for swipe detection
    hand_positions = []
    last_position_time = None
    hand_detected_start = None
    http_request_sent = False
    swipe_detected = False
    swipe_cooldown = 0  # Cooldown timer to prevent multiple swipes

    # Draw some instructions on screen
    font = cv2.FONT_HERSHEY_SIMPLEX
    instruction_text = "Swipe left = Next | Swipe right = Back | Q = Quit"

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        results = process_frame(image, hands)

        # Add instructions to the image
        cv2.putText(image, instruction_text, (10, 30), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        if results and results.multi_hand_landmarks:
            draw_hand_landmarks(image, results, mp_hands, mp_drawing, mp_drawing_styles)

            # Get the main hand
            hand_landmarks = results.multi_hand_landmarks[0]
            x, y = get_hand_position(hand_landmarks)

            current_time = time.time()

            # Initialize tracking when hand is first detected
            if hand_detected_start is None:
                hand_detected_start = current_time
                hand_positions = []
                print("Hand detected")

            # Track hand position for swipe detection
            if last_position_time is None or current_time - last_position_time > 0.05:  # 50ms sampling
                hand_positions.append({"x": x, "y": y, "time": current_time})
                last_position_time = current_time

                # Keep only the last 10 positions to detect recent movement
                if len(hand_positions) > 10:
                    hand_positions = hand_positions[-10:]

            # Check if we should look for swipe gestures
            time_condition = current_time - hand_detected_start >= hand_duration
            state_condition = not http_request_sent and not swipe_detected
            cooldown_condition = swipe_cooldown <= 0

            if time_condition and state_condition and cooldown_condition:
                # Detect swipe direction
                swipe_direction = detect_swipe(hand_positions, swipe_threshold, frame_width)

                if swipe_direction:
                    print(f"Swipe {swipe_direction} detected. Sending acknowledgment...")
                    http_request_sent = send_acknowledge_request(acknowledgment_url, swipe_direction)
                    swipe_detected = True
                    swipe_cooldown = 20  # ~1 second cooldown at 20fps

                    # Display the detected swipe direction with additional status
                    color = (0, 255, 0) if http_request_sent else (0, 0, 255)  # Green if successful, red if failed
                    status_text = "✓" if http_request_sent else "✗"
                    direction_text = f"Swipe {swipe_direction.upper()} detected! {status_text}"
                    cv2.putText(image, direction_text, (frame_width//2 - 150, frame_height - 50),
                                font, 1, color, 2, cv2.LINE_AA)
        else:
            if hand_detected_start is not None:
                hand_detected_start = None
                hand_positions = []
                last_position_time = None
                print("Hand lost")
            http_request_sent = False
            swipe_detected = False

        # Decrement cooldown timer
        if swipe_cooldown > 0:
            swipe_cooldown -= 1

        cv2.imshow('MediaPipe Hand Detection', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
