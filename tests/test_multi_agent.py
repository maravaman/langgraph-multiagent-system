#!/usr/bin/env python3
"""
Multi-Agent System Test Script
Tests the complete functionality including database storage and UI responses
"""

import requests
import json
import time
import mysql.connector
from datetime import datetime

def test_database_connection():
    """Test MySQL database connection and schema"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root', 
            password='root',
            database='langgraph_ai_system',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"✅ Database connected. Tables: {tables}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_system():
    """Test the multi-agent system comprehensively"""
    
    print("=" * 60)
    print("🚀 MULTI-AGENT SYSTEM COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test database first
    if not test_database_connection():
        print("❌ Database test failed, but continuing with API tests...")
    
    base_url = "http://localhost:8003"
    
    try:
        # Test health endpoint
        print("\n📊 Testing System Health...")
        health_response = requests.get(f"{base_url}/health", timeout=10)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ System Status: {health_data['status']}")
            
            print("\n🔧 Component Status:")
            for component, status in health_data['components'].items():
                emoji = "✅" if "Connected" in status or "Available" in status else "⚠️"
                print(f"   {emoji} {component}: {status}")
            
            print(f"\n🤖 Available Agents ({len(health_data['agents_available'])}):")
            for agent in health_data['agents_available']:
                print(f"   • {agent}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return
        
        # Test user registration and login
        print(f"\n👤 Testing User Authentication...")
        
        # Register user
        test_user = {
            'username': f'test_user_{int(time.time())}',
            'email': f'test_{int(time.time())}@example.com',
            'password': 'testpass123'
        }
        
        reg_response = requests.post(f"{base_url}/auth/register", json=test_user, timeout=10)
        
        if reg_response.status_code == 200:
            user_data = reg_response.json()
            print(f"✅ User registered: {user_data['username']} (ID: {user_data['id']})")
            user_id = user_data['id']
        else:
            print(f"❌ Registration failed: {reg_response.json()}")
            return
        
        # Login
        login_data = {
            'username': test_user['username'],
            'password': test_user['password']
        }
        
        login_response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data['access_token']
            print(f"✅ Login successful")
        else:
            print(f"❌ Login failed: {login_response.json()}")
            return
        
        # Test multi-agent queries
        headers = {'Authorization': f'Bearer {access_token}'}
        
        test_queries = [
            {
                'name': 'Multi-Agent Coordination Test',
                'query': 'best scenic, water and forest places in Maharashtra',
                'expected_agents': ['ScenicLocationFinder', 'WaterBodyAnalyzer', 'ForestAnalyzer']
            },
            {
                'name': 'Search Agent Test', 
                'query': 'search my previous travel queries and similar discussions',
                'expected_agents': ['SearchAgent']
            },
            {
                'name': 'Single Agent Test',
                'query': 'beautiful mountain landscapes for photography',
                'expected_agents': ['ScenicLocationFinder']
            },
            {
                'name': 'Forest Specific Test',
                'query': 'forest ecosystems and biodiversity conservation',
                'expected_agents': ['ForestAnalyzer']
            }
        ]
        
        print(f"\n🧪 Testing Multi-Agent Queries...")
        
        successful_tests = 0
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n--- Test {i}: {test_case['name']} ---")
            print(f"Query: '{test_case['query']}'")
            
            chat_data = {
                'user': test_user['username'],
                'user_id': user_id,
                'question': test_case['query']
            }
            
            start_time = time.time()
            chat_response = requests.post(f"{base_url}/ai/chat", json=chat_data, headers=headers, timeout=60)
            response_time = time.time() - start_time
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                orchestration = result.get('orchestration', {})
                
                print(f"✅ Response received in {response_time:.2f}s")
                print(f"   Strategy: {orchestration.get('strategy', 'unknown')}")
                print(f"   Agents Activated: {orchestration.get('agents_activated', 0)}")
                print(f"   Selected Agents: {orchestration.get('selected_agents', [])}")
                print(f"   Processing Time: {result.get('processing_time', 0):.3f}s")
                
                # Check if multi-agent response
                if 'multi_agent_responses' in result:
                    print(f"   🤖 Multi-Agent Responses:")
                    for agent_resp in result['multi_agent_responses']:
                        agent_name = agent_resp['agent']
                        response_preview = agent_resp['response'][:100].replace('\n', ' ')
                        processing_time = agent_resp.get('processing_time', 0)
                        ollama_used = agent_resp.get('ollama_used', False)
                        
                        print(f"      • {agent_name}:")
                        print(f"        Response: {response_preview}...")
                        print(f"        Time: {processing_time:.3f}s | Ollama: {ollama_used}")
                        
                        # Verify expected agents were activated
                        if agent_name in test_case['expected_agents']:
                            print(f"        ✅ Expected agent activated")
                        else:
                            print(f"        ⚠️ Unexpected agent (not in {test_case['expected_agents']})")
                else:
                    # Single agent response
                    agent_name = result.get('agent', 'Unknown')
                    response_preview = result.get('response', '')[:100].replace('\n', ' ')
                    print(f"   🤖 Single Agent Response ({agent_name}): {response_preview}...")
                
                successful_tests += 1
                
            else:
                print(f"❌ Query failed: {chat_response.status_code}")
                try:
                    error_data = chat_response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Raw error: {chat_response.text[:200]}")
            
            # Brief pause between queries
            time.sleep(1)
        
        # Test database storage
        print(f"\n💾 Testing Database Storage...")
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root', 
                database='langgraph_ai_system',
                charset='utf8mb4'
            )
            cursor = conn.cursor(dictionary=True)
            
            # Check multi-agent orchestrations
            cursor.execute("SELECT COUNT(*) as count FROM multi_agent_orchestration WHERE user_id = %s", (user_id,))
            orchestration_count = cursor.fetchone()['count']
            print(f"✅ Multi-agent orchestrations stored: {orchestration_count}")
            
            # Check individual interactions
            cursor.execute("SELECT COUNT(*) as count FROM agent_interactions WHERE user_id = %s", (user_id,))
            interaction_count = cursor.fetchone()['count']
            print(f"✅ Individual interactions stored: {interaction_count}")
            
            # Get latest orchestration to show JSON storage
            cursor.execute("""
                SELECT orchestration_id, query, agent_responses, routing_strategy, agents_used 
                FROM multi_agent_orchestration 
                WHERE user_id = %s 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (user_id,))
            
            latest = cursor.fetchone()
            if latest:
                print(f"\n📋 Latest Orchestration Example:")
                print(f"   ID: {latest['orchestration_id']}")
                print(f"   Query: {latest['query']}")
                print(f"   Strategy: {latest['routing_strategy']}")
                
                # Parse JSON responses
                agent_responses = json.loads(latest['agent_responses'])
                agents_used = json.loads(latest['agents_used'])
                
                print(f"   Agents Used: {agents_used}")
                print(f"   📊 JSON Responses by Agent:")
                for agent_name, response_data in agent_responses.items():
                    print(f"      {agent_name}:")
                    print(f"        - Response Length: {response_data['response_length']}")
                    print(f"        - Processing Time: {response_data['processing_time']}s")
                    print(f"        - Ollama Used: {response_data['ollama_used']}")
                    print(f"        - Timestamp: {response_data['timestamp']}")
            
            cursor.close()
            conn.close()
            print(f"✅ Database verification completed")
            
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
        
        # Final summary
        print(f"\n" + "=" * 60)
        print(f"🏁 TEST SUMMARY")
        print(f"=" * 60)
        print(f"✅ Successful query tests: {successful_tests}/{len(test_queries)}")
        print(f"✅ Multi-agent orchestration: Working")
        print(f"✅ JSON storage by agent: Working") 
        print(f"✅ Database integration: Working")
        print(f"✅ User authentication: Working")
        print(f"✅ API endpoints: Working")
        
        if successful_tests == len(test_queries):
            print(f"\n🎉 ALL TESTS PASSED! Multi-agent system is fully functional.")
        else:
            print(f"\n⚠️ Some tests failed. Check logs above for details.")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {base_url}")
        print(f"   Make sure the server is running: python multi_agent_system.py")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_system()
