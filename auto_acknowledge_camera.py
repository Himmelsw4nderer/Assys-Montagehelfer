import cv2
import mediapipe as mp
import requests
import time
import os
import argparse
import json
from typing import Optional, Tuple, List


def initialize_mediapipe_hands() -> Tuple:
    """Initialize MediaPipe Hands module and return related objects."""
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    return mp_hands, hands, mp_drawing, mp_drawing_styles


def process_frame(image, hands) -> Optional[mp.solutions.hands.Hands]:
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


def send_acknowledge_request(url: str = "") -> bool:
    """Send HTTP POST request to acknowledge endpoint."""
    # Use default URL if none provided
    if not url:
        # Get from environment variable or use default
        server_url = os.environ.get("ASSYS_SERVER_URL", "http://localhost:5000")
        url = f"{server_url}/auto_acknowledge"

    try:
        # Add the type of acknowledgment as "gesture"
        payload = {"type": "gesture"}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"HTTP request sent. Response: {response.status_code}")
        return True
    except Exception as e:
        print(f"Failed to send HTTP request: {e}")
        return False


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Camera-based gesture recognition for auto-acknowledgment')
    parser.add_argument('--camera', '-c', type=int, default=0,
                        help='Camera device number (default: 0)')
    parser.add_argument('--server-url', '-s', type=str,
                        default=os.environ.get('ASSYS_SERVER_URL', 'http://localhost:5000'),
                        help='Server URL for acknowledgment (default: from ASSYS_SERVER_URL env or localhost:5000)')
    parser.add_argument('--endpoint', '-e', type=str, default='/auto_acknowledge',
                        help='Endpoint for acknowledgment (default: /auto_acknowledge)')
    parser.add_argument('--swipe-threshold', '-t', type=float, default=0.3,
                        help='How far the hand needs to move horizontally for a valid swipe (default: 0.3)')
    parser.add_argument('--swipe-time', '-d', type=float, default=1.0,
                        help='Maximum time for a swipe gesture to be completed (default: 1.0 seconds)')
    return parser.parse_args()


def get_hand_position(hand_landmarks) -> Tuple[float, float]:
    """Get the average x, y position of a hand."""
    x_positions = []
    y_positions = []

    for landmark in hand_landmarks.landmark:
        x_positions.append(landmark.x)
        y_positions.append(landmark.y)

    # Return average position of the hand
    return sum(x_positions) / len(x_positions), sum(y_positions) / len(y_positions)


def detect_right_to_left_swipe(hand_positions: List[Tuple[float, float]],
                              swipe_threshold: float,
                              swipe_time: float) -> bool:
    """Detect if a right-to-left swipe gesture occurred."""
    if len(hand_positions) < 2:
        return False

    # Get the first and last recorded positions
    start_pos = hand_positions[0]
    end_pos = hand_positions[-1]

    # Calculate horizontal movement (negative means right to left)
    x_movement = end_pos[0] - start_pos[0]

    # Check if movement is from right to left and exceeds threshold
    if x_movement < -swipe_threshold:
        # Check if the gesture was completed within the specified time
        start_time, _ = hand_positions[0]
        end_time, _ = hand_positions[-1]
        if end_time - start_time <= swipe_time:
            return True

    return False


def main() -> None:
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

    # Get acknowledgment URL
    server_url = args.server_url
    acknowledgment_url = f"{server_url}{args.endpoint}"
    swipe_threshold = args.swipe_threshold
    swipe_time = args.swipe_time

    print(f"Starting camera recognition with device {camera_device}")
    print(f"Using acknowledgment URL: {acknowledgment_url}")
    print(f"Swipe threshold: {swipe_threshold}, Swipe time: {swipe_time} seconds")

    mp_hands, hands, mp_drawing, mp_drawing_styles = initialize_mediapipe_hands()
    cap = cv2.VideoCapture(camera_device)

    hand_positions = []
    tracking_hand = False
    http_request_sent = False
    start_time = None

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Flip the image horizontally for a selfie-view display
        image = cv2.flip(image, 1)

        # Process the already flipped image
        results = process_frame(image, hands)

        # Draw hand landmarks
        if results.multi_hand_landmarks:
            draw_hand_landmarks(image, results, mp_hands, mp_drawing, mp_drawing_styles)

            # Use the first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]
            current_position = get_hand_position(hand_landmarks)

            if not tracking_hand:
                tracking_hand = True
                start_time = time.time()
                hand_positions = [(start_time, current_position)]
                print("Started tracking hand")
            else:
                # Add the current position with timestamp
                hand_positions.append((time.time(), current_position))

                # Keep only positions from the last 2 seconds
                current_time = time.time()
                hand_positions = [(t, pos) for t, pos in hand_positions if current_time - t <= 2.0]

                # Check for right-to-left swipe
                if not http_request_sent and len(hand_positions) >= 2:
                    # Extract just positions for swipe detection
                    positions_only = [pos for _, pos in hand_positions]
                    time_positions = [(t, pos) for t, pos in hand_positions]

                    # Check horizontal movement (right to left)
                    if positions_only[0][0] - positions_only[-1][0] > swipe_threshold:
                        # Check if movement happened within the time threshold
                        if time_positions[-1][0] - time_positions[0][0] <= swipe_time:
                            # Print to console for swipe detection
                            print("-" * 50)
                            print("GESTURE DETECTED: Right to left swipe!")
                            print(f"Movement: {positions_only[0][0] - positions_only[-1][0]:.3f} (threshold: {swipe_threshold})")
                            print(f"Time: {time_positions[-1][0] - time_positions[0][0]:.2f}s (limit: {swipe_time}s)")
                            print("-" * 50)

                            print("Right to left swipe detected! Sending acknowledgment...")
                            http_request_sent = send_acknowledge_request(acknowledgment_url)
                            # Reset tracking after successful detection
                            hand_positions = []
                            tracking_hand = False
        else:
            if tracking_hand:
                tracking_hand = False
                hand_positions = []
                print("Lost hand tracking")
            http_request_sent = False

        # Add visual cue showing current direction
        if len(hand_positions) >= 2:
            # Extract just positions (without timestamps)
            positions_only = [pos for _, pos in hand_positions]

            # Get screen dimensions
            h, w, _ = image.shape

            # Draw arrow indicating movement direction
            if len(positions_only) >= 2:
                start_x, start_y = int(positions_only[0][0] * w), int(positions_only[0][1] * h)
                end_x, end_y = int(positions_only[-1][0] * w), int(positions_only[-1][1] * h)
                cv2.arrowedLine(image, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

        # Add instructions
        cv2.putText(image, "Swipe hand right to left", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('MediaPipe Hand Detection - Right to Left Swipe', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
