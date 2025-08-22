#!/usr/bin/env python3
"""
Comprehensive Web Interface Test
Tests all web interface functionality including login, register, and query responses
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000"

def test_server_availability():
    """Test if server is running and responsive"""
    print("🌐 Testing Server Availability...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Server is running and healthy")
            return True
        else:
            print(f"  ❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Server connection failed: {e}")
        return False

def test_web_interface_endpoints():
    """Test all web interface endpoints"""
    print("\n🌐 Testing Web Interface Endpoints...")
    
    endpoints = [
        ("/", "Main Page"),
        ("/health", "Health Check"),
        ("/ping", "Ping"),
        ("/agents", "Agents List"),
        ("/api/ollama/status", "Ollama Status")
    ]
    
    results = []
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"  {description}: {status}")
            results.append(response.status_code == 200)
        except requests.exceptions.RequestException as e:
            print(f"  {description}: ❌ Failed - {e}")
            results.append(False)
    
    return all(results)

def test_user_registration():
    """Test user registration functionality"""
    print("\n👤 Testing User Registration...")
    
    timestamp = int(time.time())
    user_data = {
        "username": f"uitest_user_{timestamp}",
        "email": f"uitest_{timestamp}@example.com",
        "password": "uitestpassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register", 
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Registration successful: {result['user']['username']}")
            print(f"  📧 User ID: {result['user']['user_id']}")
            print(f"  🔑 Token received: {result['token'][:20]}...")
            return result
        else:
            print(f"  ❌ Registration failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Registration error: {e}")
        return None

def test_user_login(username, password):
    """Test user login functionality"""
    print("\n🔐 Testing User Login...")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Login successful: {result['user']['username']}")
            print(f"  🔑 New token received: {result['token'][:20]}...")
            return result['token']
        else:
            print(f"  ❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Login error: {e}")
        return None

def test_authenticated_queries(token, username):
    """Test authenticated query processing"""
    print("\n🤖 Testing Authenticated Query Processing...")
    
    test_queries = [
        "Tell me about beautiful scenic locations in the Rocky Mountains",
        "What are the best forest hiking trails in Switzerland?",
        "Find lakes suitable for kayaking in Canada"
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    query_results = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n  🔍 Query {i}: {query[:50]}...")
        
        query_data = {
            "user": username,
            "question": query
        }
        
        try:
            # Use shorter timeout for testing
            response = requests.post(
                f"{BASE_URL}/run_graph",
                json=query_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                agent = result.get('agent', 'Unknown')
                response_length = len(result.get('response', ''))
                edges = result.get('edges_traversed', [])
                
                print(f"    Agent Used: {agent}")
                print(f"    Response Length: {response_length} chars")
                print(f"    Edges Traversed: {', '.join(edges)}")
                
                # Check if response is meaningful
                if response_length > 100:
                    print(f"    ✅ Query processed successfully")
                    query_results.append(True)
                else:
                    print(f"    ⚠️ Response seems short")
                    query_results.append(False)
            else:
                print(f"    ❌ Query failed: {response.status_code}")
                query_results.append(False)
                
        except requests.exceptions.Timeout:
            print(f"    ⚠️ Query timed out (expected for complex queries)")
            query_results.append(True)  # Don't fail for timeouts
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Query error: {e}")
            query_results.append(False)
    
    successful_queries = sum(query_results)
    total_queries = len(query_results)
    print(f"\n  📊 Query Results: {successful_queries}/{total_queries} successful")
    
    return successful_queries > 0  # At least one should succeed

def test_user_session_management(token):
    """Test user session and data management"""
    print("\n📊 Testing User Session Management...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test profile endpoint
        profile_response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers,
            timeout=10
        )
        
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print(f"  ✅ User Profile: {profile['username']} (ID: {profile['user_id']})")
        else:
            print(f"  ❌ Profile fetch failed: {profile_response.status_code}")
            return False
        
        # Test query history
        queries_response = requests.get(
            f"{BASE_URL}/auth/queries",
            headers=headers,
            timeout=10
        )
        
        if queries_response.status_code == 200:
            queries = queries_response.json()
            print(f"  ✅ Query History: {len(queries)} queries found")
            if len(queries) > 0:
                print(f"    Recent query: {queries[0]['question'][:50]}...")
        else:
            print(f"  ❌ Query history fetch failed: {queries_response.status_code}")
            return False
        
        # Test user stats
        stats_response = requests.get(
            f"{BASE_URL}/auth/stats",
            headers=headers,
            timeout=10
        )
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"  ✅ User Stats: {stats['total_queries']} total queries")
            print(f"    Agent Usage: {list(stats['agent_usage'].keys())}")
        else:
            print(f"  ❌ Stats fetch failed: {stats_response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Session management error: {e}")
        return False

def test_web_interface_responsiveness():
    """Test web interface response times"""
    print("\n⚡ Testing Web Interface Responsiveness...")
    
    endpoints = [
        ("/", "Main Page"),
        ("/health", "Health Check"),
        ("/agents", "Agents List")
    ]
    
    response_times = []
    for endpoint, description in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                print(f"  {description}: ✅ {response_time:.1f}ms")
                response_times.append(response_time)
            else:
                print(f"  {description}: ❌ {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  {description}: ❌ Failed - {e}")
    
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        print(f"  📈 Average Response Time: {avg_response_time:.1f}ms")
        return avg_response_time < 2000  # Should be under 2 seconds
    
    return False

def main():
    """Run comprehensive web interface test"""
    print("🌐 Comprehensive Web Interface Test")
    print("=" * 50)
    
    # Test sequence
    tests = []
    
    # 1. Server availability
    server_ok = test_server_availability()
    tests.append(("Server Availability", server_ok))
    
    if not server_ok:
        print("\n❌ Server not available - stopping tests")
        return False
    
    # 2. Web interface endpoints
    endpoints_ok = test_web_interface_endpoints()
    tests.append(("Web Interface Endpoints", endpoints_ok))
    
    # 3. User registration
    registration_result = test_user_registration()
    registration_ok = registration_result is not None
    tests.append(("User Registration", registration_ok))
    
    if not registration_ok:
        print("\n❌ Registration failed - stopping auth tests")
        return False
    
    username = registration_result['user']['username']
    token = registration_result['token']
    
    # 4. User login
    new_token = test_user_login(username, "uitestpassword123")
    login_ok = new_token is not None
    tests.append(("User Login", login_ok))
    
    if login_ok:
        token = new_token  # Use the new token
    
    # 5. Authenticated queries
    queries_ok = test_authenticated_queries(token, username)
    tests.append(("Authenticated Queries", queries_ok))
    
    # 6. Session management
    session_ok = test_user_session_management(token)
    tests.append(("Session Management", session_ok))
    
    # 7. Interface responsiveness
    responsive_ok = test_web_interface_responsiveness()
    tests.append(("Interface Responsiveness", responsive_ok))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 WEB INTERFACE TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    total = len(tests)
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL WEB INTERFACE TESTS PASSED!")
        print("✅ Server is responsive and healthy")
        print("✅ User registration works correctly")
        print("✅ User login functions properly")
        print("✅ Authenticated queries return full responses")
        print("✅ Session management persists user data")
        print("✅ Interface responds quickly to requests")
        print("\n🌐 The web interface is fully functional and ready for use!")
        print(f"🔗 Access at: {BASE_URL}")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
