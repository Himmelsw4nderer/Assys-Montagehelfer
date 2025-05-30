#!/bin/bash
# Camera-based auto-acknowledge starter script for Assys-Montagehelfer

# Set default server URL if not provided
ASSYS_SERVER_URL=${ASSYS_SERVER_URL:-"http://192.168.178.130:5000"}

# Check for virtual environment
if [ ! -f ".venv/bin/python3" ]; then
    echo "Error: Virtual environment not found in .venv directory"
    echo "Please create the virtual environment using: python3 -m venv .venv"
    exit 1
fi

# Print banner
echo "====================================================="
echo "   Assys-Montagehelfer Camera Recognition Control    "
echo "====================================================="
echo ""
echo "Starting camera recognition service..."
echo "Detecting hand gestures for automatic acknowledgment"
echo ""
echo "Server URL: $ASSYS_SERVER_URL"
echo ""
echo "Swipe gestures: Right->Left = Next, Left->Right = Back"
echo "Press 'q' in the camera window or Ctrl+C to stop"
echo "====================================================="

# Check dependencies
REQUIREMENTS_OK=true
.venv/bin/python3 -c "import cv2" 2>/dev/null || REQUIREMENTS_OK=false
.venv/bin/python3 -c "import mediapipe" 2>/dev/null || REQUIREMENTS_OK=false
.venv/bin/python3 -c "import requests" 2>/dev/null || REQUIREMENTS_OK=false

if [ "$REQUIREMENTS_OK" = false ]; then
    echo "Installing required Python packages in virtual environment..."
    .venv/bin/pip install opencv-python mediapipe requests
fi

# Use camera device 0 by default
CAMERA_ARG="--camera 0"
echo "Using camera device: 0"

# Start the camera recognition script
cd "$(dirname "$0")"
export ASSYS_SERVER_URL

# Pass any additional arguments from the command line
.venv/bin/python3 auto_acknowledge_camera.py $CAMERA_ARG "$@"

# Exit gracefully
echo ""
echo "Camera recognition service stopped."
