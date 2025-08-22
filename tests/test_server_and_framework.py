#!/usr/bin/env python3
"""
Test server startup and LangGraph framework endpoint
"""
import subprocess
import time
import requests
import json
import sys
import os
from threading import Thread

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_server():
    """Start the FastAPI server in background"""
    try:
        # Start server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", "--host", "127.0.0.1", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("🚀 Starting server...")
        time.sleep(5)  # Give server time to start
        
        return process
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_server():
    """Test server health and endpoints"""
    try:
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server health check passed")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
        
        # Test LangGraph endpoint
        test_data = {
            "user": "test_user",
            "question": "What is artificial intelligence?"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/run_graph",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LangGraph endpoint test passed")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ LangGraph endpoint test failed: {response.status_code}")
            print(f"📋 Error: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Testing LangGraph Framework Server")
    print("=" * 50)
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Could not start server")
        return
    
    try:
        # Test server
        if test_server():
            print("\n✅ All tests passed! LangGraph framework is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the implementation.")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    
    finally:
        # Clean up
        if server_process:
            print("🧹 Shutting down server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server shutdown complete")

if __name__ == "__main__":
    main()
