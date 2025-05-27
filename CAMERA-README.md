# Camera Recognition Control for Assys-Montagehelfer

This extension adds camera-based gesture control to the Assys-Montagehelfer system, allowing you to navigate through assembly steps using hand gestures and swipe motions.

## Features

- Hands-free navigation through assembly steps
- Real-time hand tracking and gesture detection
- Swipe gesture recognition (left to right = back, right to left = next)
- Visual feedback with overlay of detected hand landmarks
- Configurable sensitivity and timing parameters

## Usage

1. Make sure your system has a camera connected and properly configured
2. Install the required Python packages:
   ```
   pip install opencv-python mediapipe requests
   ```

3. Start the camera recognition service:
   ```
   ./start_camera_control.sh
   ```

4. Begin your assembly process in the web application
5. Use swipe gestures to navigate through steps:
   - Swipe your hand from right to left to move to the next step
   - Swipe your hand from left to right to go back to the previous step
   - The system will detect your swipe direction and respond accordingly

## Configuration

You can customize the camera recognition behavior using environment variables or command-line arguments:

- `ASSYS_SERVER_URL`: The URL of your Assys-Montagehelfer server
  ```
  export ASSYS_SERVER_URL="http://192.168.178.130:5000"
  ```

- `CAMERA_DEVICE`: Which camera to use (default: 0)
  ```
  export CAMERA_DEVICE=1  # Use the second camera
  ```

- `--swipe-threshold` or `-t`: Minimum pixel movement to detect a swipe (default: 100)
  ```
  ./start_camera_control.sh --swipe-threshold 150
  ```

## Troubleshooting

- **Camera not detected**: 
  - Make sure your camera is properly connected and functioning
  - Try specifying a different camera device using the `CAMERA_DEVICE` environment variable

- **Hand detection issues**:
  - Ensure adequate lighting for better detection
  - Position your hand clearly in the camera's field of view
  - Avoid complex backgrounds that might confuse the detection

- **"Connection refused" errors**:
  - Check that the Assys-Montagehelfer server is running
  - Verify the server URL is correct in your configuration

## Technical Details

The camera recognition system uses MediaPipe Hands for real-time hand tracking and gesture detection:

- When a horizontal swipe gesture is detected, the system determines its direction:
  - Right-to-left swipes trigger "next" step navigation
  - Left-to-right swipes trigger "back" step navigation

- The system tracks hand position over time to detect swipe motions and sends the appropriate direction command to the server.

- The visual window shows the camera feed with hand landmarks overlaid and instructions for available gestures.