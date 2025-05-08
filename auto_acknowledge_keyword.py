import speech_recognition as sr
import requests
import os
import time
import argparse
from typing import List, Optional
import sys


def send_acknowledge_request(url: str = None) -> bool:
    """Send HTTP POST request to acknowledge endpoint."""
    # Use default URL if none provided
    if url is None:
        # Get from environment variable or use default
        server_url = os.environ.get("ASSYS_SERVER_URL", "http://localhost:5000")
        url = f"{server_url}/auto_acknowledge"

    try:
        response = requests.post(url)
        print(f"HTTP request sent. Response: {response.status_code}")
        return True
    except Exception as e:
        print(f"Failed to send HTTP request: {e}")
        return False


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Keyword-based recognition for auto-acknowledgment')
    parser.add_argument('--server-url', '-s', type=str,
                        default=os.environ.get('ASSYS_SERVER_URL', 'http://localhost:5000'),
                        help='Server URL for acknowledgment (default: from ASSYS_SERVER_URL env or localhost:5000)')
    parser.add_argument('--endpoint', '-e', type=str, default='/auto_acknowledge',
                        help='Endpoint for acknowledgment (default: /auto_acknowledge)')
    parser.add_argument('--energy-threshold', '-t', type=int, 
                        default=int(os.environ.get('SPEECH_ENERGY_THRESHOLD', '3000')),
                        help='Energy threshold for speech detection (default: 3000)')
    parser.add_argument('--pause-threshold', '-p', type=float, 
                        default=float(os.environ.get('SPEECH_PAUSE_THRESHOLD', '0.8')),
                        help='Pause threshold for speech detection (default: 0.8 seconds)')
    parser.add_argument('--cooldown', '-c', type=float, 
                        default=float(os.environ.get('SPEECH_COOLDOWN', '2.0')),
                        help='Cooldown period between acknowledgments (default: 2.0 seconds)')
    return parser.parse_args()


def get_wake_words() -> List[str]:
    """Return list of wake words that trigger acknowledgment."""
    # Default wake words in German and English
    wake_words = [
        "next",
        "weiter",
        "continue",
        "nächste",
        "fertig",
        "ok"
    ]
    
    # Allow customizing wake words through environment variable
    custom_words = os.environ.get('SPEECH_WAKE_WORDS', '')
    if custom_words:
        wake_words.extend(custom_words.lower().split(','))
        
    return wake_words


def main() -> None:
    """Main function to run keyword recognition."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure speech recognition
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = args.energy_threshold
    recognizer.pause_threshold = args.pause_threshold
    
    # Prepare URLs
    acknowledgment_url = f"{args.server_url}{args.endpoint}"
    
    # Get wake words
    wake_words = get_wake_words()
    
    print(f"Starting keyword recognition")
    print(f"Using acknowledgment URL: {acknowledgment_url}")
    print(f"Wake words: {', '.join(wake_words)}")
    print(f"Energy threshold: {recognizer.energy_threshold}")
    print(f"Pause threshold: {recognizer.pause_threshold}")
    print(f"Cooldown period: {args.cooldown} seconds")
    
    # Track last acknowledgment time to prevent rapid-fire triggers
    last_acknowledgment_time = 0
    
    # Main recognition loop
    while True:
        with sr.Microphone() as source:
            print("Listening for keywords...")
            try:
                audio = recognizer.listen(source)
                
                # Try to recognize speech
                try:
                    text = recognizer.recognize_google(audio).lower()
                    print(f"Recognized: '{text}'")
                    
                    # Check if any wake word is in the recognized text
                    if any(word in text for word in wake_words):
                        # Check cooldown period
                        current_time = time.time()
                        if current_time - last_acknowledgment_time >= args.cooldown:
                            print(f"Wake word detected. Sending acknowledgment...")
                            if send_acknowledge_request(acknowledgment_url):
                                last_acknowledgment_time = current_time
                        else:
                            cooldown_remaining = args.cooldown - (current_time - last_acknowledgment_time)
                            print(f"Wake word detected but in cooldown period. {cooldown_remaining:.1f}s remaining.")
                            
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    pass
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                    
            except KeyboardInterrupt:
                print("\nKeyword recognition stopped by user.")
                break
            except Exception as e:
                print(f"Error in recognition loop: {e}")
                time.sleep(1)  # Prevent CPU-intensive crash loops


if __name__ == "__main__":
    main()