#!/usr/bin/env python3
import requests
import time

def test_auth():
    base_url = "http://localhost:8000"
    
    # Test registration
    print("Testing registration...")
    user_data = {
        'username': f'quicktest_{int(time.time())}',
        'email': f'quicktest_{int(time.time())}@test.com', 
        'password': 'testpass123'
    }
    
    try:
        r = requests.post(f"{base_url}/auth/register", json=user_data, timeout=10)
        print(f"Registration: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"Success: {result.get('success')}")
            print(f"Token received: {'token' in result}")
            token = result.get('token')
            
            # Test user info with token
            if token:
                print("\nTesting authenticated request...")
                headers = {'Authorization': f'Bearer {token}'}
                user_info = requests.get(f"{base_url}/auth/me", headers=headers, timeout=10)
                print(f"User info: {user_info.status_code}")
                if user_info.status_code == 200:
                    print("✅ Authentication working!")
                else:
                    print(f"❌ Auth failed: {user_info.text}")
        else:
            print(f"❌ Registration failed: {r.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_auth()
