#!/bin/bash
# Start the keyword recognition service for auto-acknowledging commands

# Configuration
# Set these variables in your environment or uncomment and edit here
# export ASSYS_SERVER_URL="http://localhost:5000"
# export SPEECH_ENERGY_THRESHOLD="3000"
# export SPEECH_PAUSE_THRESHOLD="0.8"
# export SPEECH_COOLDOWN="2.0"
# export SPEECH_WAKE_WORDS="next,weiter,continue,nächste,fertig,ok"

# Check if a virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python -m venv .venv

    # Activate virtual environment
    source .venv/bin/activate

    # Install required packages
    echo "Installing required packages..."
    pip install SpeechRecognition requests pyaudio
else
    # Activate virtual environment
    source .venv/bin/activate
fi

# Determine server URL
if [ -z "$ASSYS_SERVER_URL" ]; then
    # Default to localhost if not specified
    export ASSYS_SERVER_URL="http://192.168.178.130:5000"
    echo "Using default server URL: $ASSYS_SERVER_URL"
else
    echo "Using server URL from environment: $ASSYS_SERVER_URL"
fi

# Display configuration
echo "Starting keyword recognition service..."
echo "Energy threshold: ${SPEECH_ENERGY_THRESHOLD:-3000}"
echo "Pause threshold: ${SPEECH_PAUSE_THRESHOLD:-0.8}"
echo "Cooldown period: ${SPEECH_COOLDOWN:-2.0}"
echo "Wake words: ${SPEECH_WAKE_WORDS:-next,weiter,continue,nächste,fertig,ok}"

# Change to script directory
cd "$(dirname "$0")"
export ASSYS_SERVER_URL
.venv/bin/python3 auto_acknowledge_keyword.py

# Exit gracefully
exit 0
