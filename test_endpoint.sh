#!/bin/bash
# Test script for auto_acknowledge endpoint

# Set default server URL if not provided
ASSYS_SERVER_URL=${ASSYS_SERVER_URL:-"http://192.168.178.130:5000"}

# Check for virtual environment
if [ ! -f ".venv/bin/python3" ]; then
    echo "Error: Virtual environment not found in .venv directory"
    echo "Please create the virtual environment using: python3 -m venv .venv"
    exit 1
fi

# Print banner
echo "========================================The issue is with the api endpoint============="
echo "   Auto Acknowledge Endpoint Test Tool               "
echo "====================================================="
echo ""
echo "Testing connection to server..."
echo "Server URL: $ASSYS_SERVER_URL"
echo ""

# Start the test script
cd "$(dirname "$0")"
export ASSYS_SERVER_URL

# Pass any additional arguments from the command line
.venv/bin/python3 test_endpoint.py "$@"

# Exit with the same code as the Python script
exit $?
