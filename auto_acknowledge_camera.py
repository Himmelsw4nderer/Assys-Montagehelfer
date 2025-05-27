import cv2
import mediapipe as mp
import requests
import time
import os
import sys
import argparse
from typing import Optional, Tuple


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


def send_acknowledge_request(url: str = None) -> bool:
    """Send HTTP POST request to acknowledge endpoint."""
    # Use default URL if none provided
    if url is None:
        # Get from environment variable or use default
        server_url = os.environ.get("ASSYS_SERVER_URL", "http://localhost:5000")
        url = f"{server_url}/auto_acknowledge"

    try:
        payload = {"type": "gesture", "direction": "next"}
        response = requests.post(url, json=payload)
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
    parser.add_argument('--hand-duration', '-d', type=float, default=0.75,
                        help='Duration hand must be visible before acknowledgment (default: 0.75 seconds)')
    return parser.parse_args()

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

    print(f"Starting camera recognition with device {camera_device}")
    print(f"Using acknowledgment URL: {acknowledgment_url}")

    mp_hands, hands, mp_drawing, mp_drawing_styles = initialize_mediapipe_hands()
    cap = cv2.VideoCapture(camera_device)

    hand_detected_start = None
    http_request_sent = False

    # Get hand duration from arguments
    hand_duration = args.hand_duration
    acknowledgment_url = f"{args.server_url}{args.endpoint}"

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        results = process_frame(image, hands)

        if results.multi_hand_landmarks:
            draw_hand_landmarks(image, results, mp_hands, mp_drawing, mp_drawing_styles)

            if hand_detected_start is None:
                hand_detected_start = time.time()
                print("Hand detected")
            elif time.time() - hand_detected_start >= hand_duration and not http_request_sent:
                print(f"Hand steady for {hand_duration} seconds. Sending acknowledgment...")
                http_request_sent = send_acknowledge_request(acknowledgment_url)
                # Reset timer to prevent immediate re-acknowledgment
                hand_detected_start = time.time()
        else:
            if hand_detected_start is not None:
                hand_detected_start = None
                print("Hand lost")
            http_request_sent = False

        cv2.imshow('MediaPipe Hand Detection', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
