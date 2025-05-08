import cv2
import mediapipe as mp
import requests
import time
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


def send_acknowledge_request(url: str = 'http://192.168.178.130:5000/auto_acknowledge') -> bool:
    """Send HTTP POST request to acknowledge endpoint."""
    try:
        response = requests.post(url)
        print(f"HTTP request sent. Response: {response.status_code}")
        return True
    except Exception as e:
        print(f"Failed to send HTTP request: {e}")
        return False


def main() -> None:
    """Main function to run hand detection and tracking."""
    mp_hands, hands, mp_drawing, mp_drawing_styles = initialize_mediapipe_hands()
    cap = cv2.VideoCapture(2)

    hand_detected_start = None
    http_request_sent = False

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        results = process_frame(image, hands)
        print(results)

        if results.multi_hand_landmarks:
            draw_hand_landmarks(image, results, mp_hands, mp_drawing, mp_drawing_styles)

            if hand_detected_start is None:
                hand_detected_start = time.time()
            elif time.time() - hand_detected_start >= 0.75 and not http_request_sent:
                http_request_sent = send_acknowledge_request()
        else:
            hand_detected_start = None
            http_request_sent = False

        cv2.imshow('MediaPipe Hand Detection', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
