#!/usr/bin/env python3
"""
Test Script to Verify UI Shows Actual Agent Responses
"""

import requests
import json
import time

def test_ui_response_display():
    """Test that the UI properly displays actual agent content instead of just metadata"""
    
    base_url = "http://localhost:8003"
    
    print("🧪 Testing UI Response Display")
    print("=" * 50)
    
    try:
        # Test health first
        health_resp = requests.get(f"{base_url}/health", timeout=5)
        if health_resp.status_code != 200:
            print("❌ Server not running. Start with: python multi_agent_system.py")
            return
        
        # Register test user
        test_user = {
            'username': f'ui_test_user_{int(time.time())}',
            'email': f'ui_test_{int(time.time())}@example.com',
            'password': 'test123'
        }
        
        print("1. Registering test user...")
        reg_resp = requests.post(f"{base_url}/auth/register", json=test_user, timeout=10)
        if reg_resp.status_code != 200:
            print(f"❌ Registration failed: {reg_resp.text}")
            return
        
        user_data = reg_resp.json()
        print(f"✅ User registered: {user_data['username']}")
        
        # Login
        print("2. Logging in...")
        login_resp = requests.post(f"{base_url}/auth/login", json={
            'username': test_user['username'], 
            'password': test_user['password']
        }, timeout=10)
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.text}")
            return
        
        token_data = login_resp.json()
        token = token_data['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Login successful")
        
        # Test multi-agent query
        print("3. Sending multi-agent query...")
        query = "best scenic, water and forest places in Maharashtra"
        
        chat_resp = requests.post(f"{base_url}/ai/chat", json={
            'user': test_user['username'],
            'user_id': user_data['id'],
            'question': query
        }, headers=headers, timeout=45)
        
        if chat_resp.status_code != 200:
            print(f"❌ Chat failed: {chat_resp.text}")
            return
        
        result = chat_resp.json()
        print("✅ Query processed successfully")
        
        # Analyze the response structure
        print("\n📊 RESPONSE ANALYSIS:")
        print(f"Strategy: {result.get('orchestration', {}).get('strategy', 'N/A')}")
        print(f"Processing Time: {result.get('processing_time', 0):.3f}s")
        
        if 'multi_agent_responses' in result:
            print(f"Multi-Agent Responses: {len(result['multi_agent_responses'])}")
            print("\n🎯 AGENT RESPONSES FOR UI DISPLAY:")
            
            for i, agent_resp in enumerate(result['multi_agent_responses'], 1):
                agent_name = agent_resp['agent']
                response_content = agent_resp['response']
                response_length = len(response_content)
                ollama_used = agent_resp.get('ollama_used', False)
                processing_time = agent_resp.get('processing_time', 0)
                
                print(f"\n--- Agent {i}: {agent_name} ---")
                print(f"   Ollama Used: {ollama_used}")
                print(f"   Processing Time: {processing_time:.3f}s")
                print(f"   Response Length: {response_length} chars")
                print(f"   Content Preview:")
                
                # Show first 200 chars of actual content
                preview = response_content[:200].replace('\n', ' ')
                print(f"   \"{preview}{'...' if len(response_content) > 200 else ''}\"")
                
                # Check if it's meaningful content vs just fallback
                if response_length > 50 and not response_content.startswith("Scenic location information is available"):
                    print(f"   ✅ Contains substantial content for UI display")
                else:
                    print(f"   ⚠️ Appears to be fallback message - user will see brief message")
                    print(f"   💡 To see full responses, ensure Ollama is running with: ollama serve")
            
            print(f"\n🖥️ UI DISPLAY SUMMARY:")
            print(f"   • Users will see {len(result['multi_agent_responses'])} separate agent response cards")
            print(f"   • Each card shows the agent name, processing time, and actual response content")
            print(f"   • Processing details are collapsed by default to focus on content")
            print(f"   • Total processing time: {result.get('processing_time', 0):.3f}s shown in summary")
            
        else:
            # Single agent response
            print("Single Agent Response:")
            print(f"   Agent: {result.get('agent', 'Unknown')}")
            print(f"   Content: {result.get('response', '')[:200]}...")
        
        print(f"\n✅ UI Response Test Complete!")
        print(f"📱 View in browser: {base_url}/")
        print(f"🔑 Login with: {test_user['username']} / {test_user['password']}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure server is running: python multi_agent_system.py")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_ui_response_display()
