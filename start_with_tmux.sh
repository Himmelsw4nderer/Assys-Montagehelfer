#!/bin/bash
# Tmux-based starter script for Assys-Montagehelfer
# This script starts both camera and speech recognition in a tmux session

# Set default server URL if not provided
ASSYS_SERVER_URL=${ASSYS_SERVER_URL:-"http://192.168.178.130:5000"}
export ASSYS_SERVER_URL

# Print banner
echo "====================================================="
echo "   Assys-Montagehelfer Smart Recognition Control     "
echo "====================================================="
echo "Starting both camera and speech recognition systems..."
echo "Server URL: $ASSYS_SERVER_URL"
echo "====================================================="

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "Error: tmux is not installed. Please install it with your package manager."
    echo "For example: sudo apt install tmux"
    exit 1
fi

# Check for virtual environment
if [ ! -f ".venv/bin/python3" ]; then
    echo "Error: Virtual environment not found in .venv directory"
    echo "Please create the virtual environment using: python3 -m venv .venv"
    exit 1
fi

# Make scripts executable
chmod +x ./start_camera_control.sh ./start_keyword_control.sh

# Change to script directory
cd "$(dirname "$0")"

# Kill any existing tmux session with the same name
tmux kill-session -t assys 2>/dev/null

# Create a new tmux session named "assys" with camera control in the first pane
tmux new-session -d -s assys -n "Assys-Montagehelfer" "./start_camera_control.sh"

# Create a second pane with speech control
tmux split-window -t assys:0 -v "./start_keyword_control.sh"

# Set the layout to even vertical split
tmux select-layout -t assys:0 even-vertical

# Attach to the tmux session
echo "Starting tmux session with both recognition systems..."
echo "Press Ctrl+B then D to detach from the session without stopping it"
echo "You can reattach later with: tmux attach -t assys"
echo ""

tmux attach -t assys

# If user detached, inform them how to reattach
echo ""
echo "You've detached from the tmux session, but the recognition systems are still running."
echo "To reattach to the session: tmux attach -t assys"
echo "To terminate the session: tmux kill-session -t assys"
