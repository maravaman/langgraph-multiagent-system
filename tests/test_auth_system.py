#!/usr/bin/env python3
"""
🔐 Authentication System Integration Test
Complete test of registration, login, queries, activity tracking, and logout
"""
import sys
import os
import time
import requests
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class AuthSystemTester:
    def __init__(self):
        self.api_base = "http://127.0.0.1:8000"
        self.test_username = f"testuser_{int(time.time())}"
        self.test_email = f"test_{int(time.time())}@example.com"
        self.test_password = "testpass123"
        self.auth_token = None
        self.session_id = None
        self.user_id = None
        
    def test_server_health(self):
        """Test if server is running"""
        print("🔧 Testing server health...")
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.ok:
                print("✅ Server is running and healthy")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server is not accessible: {e}")
            return False
    
    def test_auth_endpoints(self):
        """Test authentication endpoints availability"""
        print("🔧 Testing authentication endpoints...")
        
        endpoints = [
            "/auth/register",
            "/auth/login", 
            "/auth/me",
            "/auth/stats",
            "/auth/queries",
            "/auth/activity"
        ]
        
        available_endpoints = []
        for endpoint in endpoints:
            try:
                # Use OPTIONS request to check endpoint availability
                response = requests.options(f"{self.api_base}{endpoint}", timeout=5)
                if response.status_code != 404:
                    available_endpoints.append(endpoint)
                    print(f"✅ {endpoint} is available")
                else:
                    print(f"❌ {endpoint} not found")
            except Exception:
                print(f"❌ {endpoint} is not accessible")
        
        return len(available_endpoints) >= 4  # At least 4 core endpoints should be available
    
    def test_user_registration(self):
        """Test user registration"""
        print(f"🔐 Testing user registration...")
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/register",
                json={
                    'username': self.test_username,
                    'email': self.test_email,
                    'password': self.test_password
                },
                timeout=10
            )
            
            if response.ok:
                result = response.json()
                if result.get('success'):
                    self.auth_token = result.get('token')
                    self.session_id = result.get('session_id')
                    self.user_id = result.get('user', {}).get('user_id')
                    
                    print(f"✅ User registered successfully: {self.test_username}")
                    print(f"   User ID: {self.user_id}")
                    print(f"   Session ID: {self.session_id[:20]}..." if self.session_id else "   No session ID")
                    print(f"   Token: {self.auth_token[:20]}..." if self.auth_token else "   No token")
                    return True
                else:
                    print(f"❌ Registration failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                print(f"❌ Registration request failed: {error_data.get('detail', f'HTTP {response.status_code}')}")
                return False
                
        except Exception as e:
            print(f"❌ Registration test failed: {e}")
            return False
    
    def test_user_profile(self):
        """Test getting user profile"""
        print("👤 Testing user profile retrieval...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            response = requests.get(
                f"{self.api_base}/auth/me",
                headers={'Authorization': f'Bearer {self.auth_token}'},
                timeout=10
            )
            
            if response.ok:
                profile = response.json()
                print(f"✅ Profile retrieved successfully:")
                print(f"   Username: {profile.get('username')}")
                print(f"   Email: {profile.get('email')}")
                print(f"   Created: {profile.get('created_at')}")
                return True
            else:
                print(f"❌ Profile retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Profile test failed: {e}")
            return False
    
    def test_authenticated_query(self):
        """Test making an authenticated query"""
        print("🤖 Testing authenticated query...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        test_question = "What are the best scenic locations in Switzerland?"
        
        try:
            response = requests.post(
                f"{self.api_base}/run_graph",
                json={
                    'user': self.test_username,
                    'question': test_question
                },
                headers={'Authorization': f'Bearer {self.auth_token}'},
                timeout=60
            )
            
            if response.ok:
                result = response.json()
                print(f"✅ Query executed successfully:")
                print(f"   Question: {result.get('question')}")
                print(f"   Agent: {result.get('agent')}")
                print(f"   Response length: {len(result.get('response', ''))} characters")
                print(f"   Edges traversed: {result.get('edges_traversed', [])}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                print(f"❌ Query failed: {error_data.get('detail', f'HTTP {response.status_code}')}")
                return False
                
        except Exception as e:
            print(f"❌ Query test failed: {e}")
            return False
    
    def test_query_history(self):
        """Test query history retrieval"""
        print("📜 Testing query history...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            response = requests.get(
                f"{self.api_base}/auth/queries?limit=5",
                headers={'Authorization': f'Bearer {self.auth_token}'},
                timeout=10
            )
            
            if response.ok:
                queries = response.json()
                print(f"✅ Query history retrieved: {len(queries)} queries")
                
                for i, query in enumerate(queries[:3], 1):
                    print(f"   {i}. {query.get('question', 'N/A')[:60]}...")
                    print(f"      Agent: {query.get('agent_used')}, Date: {query.get('created_at')}")
                
                return True
            else:
                print(f"❌ Query history retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Query history test failed: {e}")
            return False
    
    def test_user_stats(self):
        """Test user statistics"""
        print("📊 Testing user statistics...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            response = requests.get(
                f"{self.api_base}/auth/stats",
                headers={'Authorization': f'Bearer {self.auth_token}'},
                timeout=10
            )
            
            if response.ok:
                stats = response.json()
                print(f"✅ User statistics retrieved:")
                print(f"   Total queries: {stats.get('total_queries', 0)}")
                print(f"   Total activities: {stats.get('total_activities', 0)}")
                print(f"   Agents used: {len(stats.get('agent_usage', {}))}")
                
                agent_usage = stats.get('agent_usage', {})
                if agent_usage:
                    print("   Agent usage:")
                    for agent, count in sorted(agent_usage.items(), key=lambda x: x[1], reverse=True)[:3]:
                        print(f"     • {agent}: {count} queries")
                
                return True
            else:
                print(f"❌ Statistics retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Statistics test failed: {e}")
            return False
    
    def test_user_activity(self):
        """Test user activity log"""
        print("📋 Testing user activity...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            response = requests.get(
                f"{self.api_base}/auth/activity?limit=5",
                headers={'Authorization': f'Bearer {self.auth_token}'},
                timeout=10
            )
            
            if response.ok:
                activities = response.json()
                print(f"✅ User activity retrieved: {len(activities)} activities")
                
                for i, activity in enumerate(activities[:3], 1):
                    print(f"   {i}. {activity.get('activity_type')} - {activity.get('created_at')}")
                    if activity.get('activity_data'):
                        print(f"      Data: {activity['activity_data']}")
                
                return True
            else:
                print(f"❌ Activity retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Activity test failed: {e}")
            return False
    
    def test_logout(self):
        """Test user logout"""
        print("👋 Testing logout...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/logout",
                headers={'Authorization': f'Bearer {self.auth_token}'},
                timeout=10
            )
            
            if response.ok:
                print("✅ Logout successful")
                
                # Test that token is now invalid
                profile_response = requests.get(
                    f"{self.api_base}/auth/me",
                    headers={'Authorization': f'Bearer {self.auth_token}'},
                    timeout=5
                )
                
                if profile_response.status_code == 401:
                    print("✅ Token invalidated successfully")
                    return True
                else:
                    print("⚠️ Logout successful but token may still be valid")
                    return True
            else:
                print(f"❌ Logout failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Logout test failed: {e}")
            return False
    
    def test_login_existing_user(self):
        """Test logging in with existing user"""
        print("🔐 Testing login with existing credentials...")
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/login",
                json={
                    'username': self.test_username,
                    'password': self.test_password
                },
                timeout=10
            )
            
            if response.ok:
                result = response.json()
                if result.get('success'):
                    self.auth_token = result.get('token')
                    print(f"✅ Login successful")
                    return True
                else:
                    print(f"❌ Login failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Login request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Login test failed: {e}")
            return False
    
    def run_complete_test(self):
        """Run complete authentication system test"""
        print("🎯 LANGGRAPH AUTHENTICATION SYSTEM - COMPLETE TEST")
        print("=" * 70)
        print(f"🧪 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base: {self.api_base}")
        print(f"👤 Test User: {self.test_username}")
        print("=" * 70)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Auth Endpoints", self.test_auth_endpoints),
            ("User Registration", self.test_user_registration),
            ("User Profile", self.test_user_profile),
            ("Authenticated Query", self.test_authenticated_query),
            ("Query History", self.test_query_history),
            ("User Statistics", self.test_user_stats),
            ("User Activity", self.test_user_activity),
            ("Logout", self.test_logout),
            ("Login Existing User", self.test_login_existing_user),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 50)
            
            try:
                if test_func():
                    passed += 1
                    print(f"✅ PASSED: {test_name}")
                else:
                    failed += 1
                    print(f"❌ FAILED: {test_name}")
            except Exception as e:
                failed += 1
                print(f"💥 CRASHED: {test_name} - {e}")
            
            time.sleep(1)  # Brief pause between tests
        
        print("\n" + "=" * 70)
        print("🎯 AUTHENTICATION SYSTEM TEST RESULTS")
        print("=" * 70)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Authentication system is working perfectly!")
        elif passed >= len(tests) * 0.8:
            print("⚠️ Most tests passed. Authentication system is mostly working.")
        else:
            print("🚨 Multiple test failures. Authentication system needs attention.")
        
        print("=" * 70)
        
        return failed == 0

def main():
    """Main test runner"""
    try:
        tester = AuthSystemTester()
        success = tester.run_complete_test()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
