# Speech Recognition Control for Assys-Montagehelfer

This extension adds voice control to the Assys-Montagehelfer system, allowing you to navigate through assembly steps using voice commands.

## Features

- Hands-free navigation through assembly steps
- Recognizes commands in both German and English
- Works alongside the existing camera-based auto-acknowledge system
- Customizable wake words and sensitivity settings

## Usage

1. Make sure your system has a microphone connected and properly configured
2. Install the required Python packages:
   ```
   pip install SpeechRecognition requests pyaudio
   ```
   Note: `pyaudio` may require additional system libraries. On Ubuntu/Debian:
   ```
   sudo apt-get install python3-pyaudio portaudio19-dev
   ```

3. Start the speech recognition service:
   ```
   ./start_speech_control.sh
   ```

4. Begin your assembly process in the web application
5. When you want to move to the next step, say one of the wake words:
   - "next"
   - "weiter"
   - "continue"
   - "nächste"
   - "fertig"
   - "ok"

## Configuration

You can customize the speech recognition behavior using environment variables:

- `ASSYS_SERVER_URL`: The URL of your Assys-Montagehelfer server
  ```
  export ASSYS_SERVER_URL="http://192.168.178.130:5000"
  ```

- `SPEECH_ENERGY_THRESHOLD`: Sensitivity for speech detection (default: 3000)
  ```
  export SPEECH_ENERGY_THRESHOLD=4000
  ```

- `SPEECH_PAUSE_THRESHOLD`: How long to wait for a pause before processing (default: 0.8)
  ```
  export SPEECH_PAUSE_THRESHOLD=1.0
  ```

- `SPEECH_COOLDOWN`: Time to wait between acknowledgments (default: 2.0)
  ```
  export SPEECH_COOLDOWN=1.5
  ```

## Troubleshooting

- **Service doesn't respond to voice commands**: 
  - Try adjusting the `SPEECH_ENERGY_THRESHOLD` value. Lower values increase sensitivity.
  - Make sure your microphone is working by testing it with another application.

- **Service keeps acknowledging ambient noise**:
  - Increase the `SPEECH_ENERGY_THRESHOLD` value.
  - Increase the `SPEECH_COOLDOWN` period.

- **"Could not request results from Google Speech Recognition service"**:
  - Check your internet connection.
  - Google's speech recognition service has usage limits. Consider switching to an offline recognition engine if this happens frequently.

## Technical Details

The speech recognition runs as a separate process from the main application. When it detects a wake word, it sends an HTTP request to the `/auto_acknowledge` endpoint of the Assys-Montagehelfer server, which then automatically advances to the next step, just as if the user had clicked the "Next Step" button.