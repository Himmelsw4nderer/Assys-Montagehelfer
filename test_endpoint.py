#!/usr/bin/env python3
import requests
import argparse
import sys
import os
import json
from typing import Dict, Any, Optional

def test_connection(url: str, endpoint: str = "/auto_acknowledge", verbose: bool = False) -> bool:
    """Test connection to the server and specifically to the auto_acknowledge endpoint."""
    full_url = f"{url}{endpoint}"
    
    if verbose:
        print(f"Testing connection to {full_url}...")
    
    try:
        response = requests.get(url)
        if verbose:
            print(f"Server connection: {'SUCCESS' if response.status_code == 200 else 'FAILED'} (Status {response.status_code})")
        
        response = requests.get(full_url)
        if verbose:
            print(f"Endpoint connection: {'SUCCESS' if response.status_code == 200 else 'FAILED'} (Status {response.status_code})")
            if response.status_code == 200:
                print(f"Response: {response.text}")
        
        return response.status_code == 200
    except requests.exceptions.ConnectionError as e:
        if verbose:
            print(f"Connection error: {e}")
        return False

def send_gesture(url: str, direction: str = "next", verbose: bool = False) -> Optional[Dict[str, Any]]:
    """Send a gesture request to the auto_acknowledge endpoint."""
    full_url = f"{url}/auto_acknowledge"
    payload = {"type": "gesture", "direction": direction}
    headers = {"Content-Type": "application/json"}
    
    if verbose:
        print(f"Sending gesture request to {full_url}")
        print(f"Payload: {json.dumps(payload)}")
    
    try:
        response = requests.post(full_url, json=payload, headers=headers)
        
        if verbose:
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"Error: {e}")
        return None

def main() -> None:
    """Main function to test the auto_acknowledge endpoint."""
    parser = argparse.ArgumentParser(description='Test auto_acknowledge endpoint')
    parser.add_argument('--url', '-u', type=str,
                        default=os.environ.get('ASSYS_SERVER_URL', 'http://192.168.178.130:5000'),
                        help='Server URL (default: from ASSYS_SERVER_URL env or http://192.168.178.130:5000)')
    parser.add_argument('--direction', '-d', type=str, choices=['next', 'back'], default='next',
                        help='Direction to send (default: next)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--test-only', '-t', action='store_true',
                        help='Only test connection without sending gesture')
    
    args = parser.parse_args()
    
    # Test basic connection first
    connection_ok = test_connection(args.url, verbose=args.verbose)
    
    if not connection_ok:
        print(f"\n❌ ERROR: Cannot connect to server at {args.url}")
        print("Please check:")
        print("1. The server is running")
        print("2. The URL is correct")
        print("3. Network connectivity")
        print(f"\nCurrent URL: {args.url}")
        print(f"To change the URL, set the ASSYS_SERVER_URL environment variable or use --url")
        sys.exit(1)
    
    if args.test_only:
        print(f"\n✅ Connection test successful: {args.url} is reachable")
        sys.exit(0)
    
    # Send the gesture
    print(f"\nSending {args.direction} gesture...")
    result = send_gesture(args.url, args.direction, verbose=args.verbose)
    
    if result:
        print(f"\n✅ Gesture sent successfully!")
        print(f"Server response: {json.dumps(result, indent=2)}")
    else:
        print(f"\n❌ Failed to send gesture")
        sys.exit(1)

if __name__ == "__main__":
    main()