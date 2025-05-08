# Camera Recognition Control for Assys-Montagehelfer

This extension adds camera-based gesture control to the Assys-Montagehelfer system, allowing you to navigate through assembly steps using hand gestures.

## Features

- Hands-free navigation through assembly steps
- Real-time hand tracking and gesture detection
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
5. When you want to move to the next step, simply show your hand to the camera
   - Hold your hand steady for about 0.75 seconds
   - The system will automatically acknowledge and move to the next step

## Configuration

You can customize the camera recognition behavior using environment variables:

- `ASSYS_SERVER_URL`: The URL of your Assys-Montagehelfer server
  ```
  export ASSYS_SERVER_URL="http://192.168.178.130:5000"
  ```

- `CAMERA_DEVICE`: Which camera to use (default: 0)
  ```
  export CAMERA_DEVICE=1  # Use the second camera
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

The camera recognition system uses MediaPipe Hands for real-time hand tracking. When a hand is detected and remains in view for a short period (default: 0.75 seconds), it sends an HTTP request to the server to advance to the next step, just as if the user had clicked the "Next Step" button.

The visual window shows the camera feed with hand landmarks overlaid, allowing you to verify that your hand is being properly detected.