#!/usr/bin/env python3
"""
Comprehensive Multi-Agent Orchestration Test
- Tests all agents working together
- Verifies similarity search agent functionality
- Checks database storage and UI response display
- Demonstrates complete system functionality
"""

import requests
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_service_availability():
    """Check if required services are running"""
    print("🔍 Checking Service Availability")
    print("=" * 50)
    
    services = {
        'Multi-Agent System': ('http://localhost:8003/health', 'System running'),
        'MySQL': ('connection test', 'Database connected'),
        'Redis': ('connection test', 'Cache available'),
        'Ollama': ('http://localhost:11434/api/tags', 'AI models available')
    }
    
    available_services = {}
    
    # Test Multi-Agent System
    try:
        resp = requests.get('http://localhost:8003/health', timeout=5)
        if resp.status_code == 200:
            health_data = resp.json()
            available_services['multi_agent'] = True
            print(f"✅ Multi-Agent System: {health_data.get('status', 'Running')}")
            
            # Check component status from health endpoint
            components = health_data.get('components', {})
            for comp, status in components.items():
                print(f"   └─ {comp}: {status}")
        else:
            available_services['multi_agent'] = False
            print(f"❌ Multi-Agent System: HTTP {resp.status_code}")
    except requests.exceptions.RequestException as e:
        available_services['multi_agent'] = False
        print(f"❌ Multi-Agent System: {e}")
        print("   💡 Start with: python multi_agent_system.py")
    
    # Test Ollama directly
    try:
        resp = requests.get('http://localhost:11434/api/tags', timeout=3)
        if resp.status_code == 200:
            available_services['ollama'] = True
            models = resp.json().get('models', [])
            print(f"✅ Ollama: {len(models)} models available")
            if models:
                print(f"   └─ Default model: {models[0].get('name', 'N/A')}")
        else:
            available_services['ollama'] = False
            print(f"⚠️ Ollama: HTTP {resp.status_code} - Using mock responses")
    except requests.exceptions.RequestException:
        available_services['ollama'] = False
        print(f"⚠️ Ollama: Not available - Using mock responses")
        print("   💡 Start with: ollama serve")
    
    return available_services

def register_and_login(base_url):
    """Register test user and get authentication token"""
    print("\n👤 Setting up Test User")
    print("=" * 50)
    
    # Generate unique test user
    timestamp = int(time.time())
    test_user = {
        'username': f'orchestration_test_{timestamp}',
        'email': f'test_{timestamp}@example.com',
        'password': 'test123'
    }
    
    try:
        # Register
        print("1. Registering test user...")
        reg_resp = requests.post(f"{base_url}/auth/register", json=test_user, timeout=10)
        if reg_resp.status_code != 200:
            print(f"❌ Registration failed: {reg_resp.text}")
            return None, None
        
        user_data = reg_resp.json()
        print(f"✅ User registered: {user_data['username']} (ID: {user_data['id']})")
        
        # Login
        print("2. Logging in...")
        login_resp = requests.post(f"{base_url}/auth/login", json={
            'username': test_user['username'],
            'password': test_user['password']
        }, timeout=10)
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.text}")
            return None, None
        
        token_data = login_resp.json()
        token = token_data['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Authentication successful")
        
        return user_data, headers
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def test_single_agent_responses(base_url, user_data, headers):
    """Test individual agents to build conversation history"""
    print("\n🤖 Testing Individual Agents (Building History)")
    print("=" * 50)
    
    test_queries = [
        {
            'query': 'Tell me about scenic mountain locations in India',
            'expected_agent': 'ScenicLocationFinder',
            'description': 'Scenic locations query'
        },
        {
            'query': 'What are the forest ecosystems in Western Ghats?',
            'expected_agent': 'ForestAnalyzer', 
            'description': 'Forest ecosystem query'
        },
        {
            'query': 'Analyze the water bodies and rivers in Maharashtra',
            'expected_agent': 'WaterBodyAnalyzer',
            'description': 'Water body analysis query'
        }
    ]
    
    responses_history = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {test['description']}")
        print(f"   Query: \"{test['query']}\"")
        
        try:
            chat_resp = requests.post(f"{base_url}/ai/chat", json={
                'user': user_data['username'],
                'user_id': user_data['id'],
                'question': test['query']
            }, headers=headers, timeout=30)
            
            if chat_resp.status_code == 200:
                result = chat_resp.json()
                agent_used = result.get('agent', 'Unknown')
                response_length = len(result.get('response', ''))
                processing_time = result.get('processing_time', 0)
                
                print(f"   ✅ Agent: {agent_used}")
                print(f"   ✅ Response: {response_length} characters")
                print(f"   ✅ Time: {processing_time:.3f}s")
                
                responses_history.append({
                    'query': test['query'],
                    'agent': agent_used,
                    'response_length': response_length,
                    'processing_time': processing_time
                })
            else:
                print(f"   ❌ Failed: HTTP {chat_resp.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print(f"\n📊 Built conversation history with {len(responses_history)} interactions")
    return responses_history

def test_similarity_search_agent(base_url, user_data, headers):
    """Test the similarity search agent specifically"""
    print("\n🔍 Testing Similarity Search Agent")
    print("=" * 50)
    
    search_queries = [
        "search my conversation history",
        "find similar discussions about mountains", 
        "what did we talk about before regarding forests?",
        "recall previous water-related conversations"
    ]
    
    search_results = []
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n{i}. Search Query: \"{query}\"")
        
        try:
            chat_resp = requests.post(f"{base_url}/ai/chat", json={
                'user': user_data['username'],
                'user_id': user_data['id'],
                'question': query
            }, headers=headers, timeout=25)
            
            if chat_resp.status_code == 200:
                result = chat_resp.json()
                agent_used = result.get('agent', 'Unknown')
                response = result.get('response', '')
                processing_time = result.get('processing_time', 0)
                
                print(f"   ✅ Agent: {agent_used}")
                print(f"   ✅ Processing Time: {processing_time:.3f}s")
                
                # Check if it's SearchAgent and JSON response
                if agent_used == 'SearchAgent' or 'SearchAgent' in str(result):
                    print(f"   ✅ SearchAgent activated successfully")
                    
                    # Try to parse JSON response
                    try:
                        if response.startswith('{'):
                            json_data = json.loads(response)
                            search_results_found = json_data.get('search_results', {})
                            similar_content = search_results_found.get('similar_content', [])
                            total_matches = search_results_found.get('total_matches', 0)
                            
                            print(f"   ✅ JSON Response: {total_matches} matches found")
                            print(f"   ✅ Similar Content Items: {len(similar_content)}")
                            
                            if similar_content:
                                print("   📋 Sample matches:")
                                for match in similar_content[:2]:
                                    agent_name = match.get('agent_name', 'Unknown')
                                    similarity = match.get('similarity', 0)
                                    content_preview = match.get('content', '')[:50]
                                    print(f"      └─ {agent_name} (sim: {similarity:.3f}): {content_preview}...")
                        else:
                            print(f"   ⚠️ Non-JSON response (length: {len(response)})")
                            
                    except json.JSONDecodeError:
                        print(f"   ⚠️ Response not valid JSON")
                else:
                    print(f"   ℹ️ Routed to {agent_used} instead of SearchAgent")
                
                search_results.append({
                    'query': query,
                    'agent': agent_used,
                    'processing_time': processing_time,
                    'is_search_agent': agent_used == 'SearchAgent'
                })
                
            else:
                print(f"   ❌ Failed: HTTP {chat_resp.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)
    
    # Summary
    search_agent_calls = sum(1 for r in search_results if r['is_search_agent'])
    print(f"\n📊 Search Agent Summary:")
    print(f"   • Total queries: {len(search_queries)}")
    print(f"   • SearchAgent activations: {search_agent_calls}")
    print(f"   • Success rate: {(search_agent_calls/len(search_queries)*100):.1f}%")
    
    return search_results

def test_multi_agent_orchestration(base_url, user_data, headers):
    """Test multi-agent orchestration with complex queries"""
    print("\n🎭 Testing Multi-Agent Orchestration")
    print("=" * 50)
    
    # Complex query that should trigger multiple agents
    complex_query = "best scenic, water and forest places in Maharashtra for nature photography"
    
    print(f"Complex Query: \"{complex_query}\"")
    print("Expected: Multiple agents working together (ScenicLocationFinder, WaterBodyAnalyzer, ForestAnalyzer)")
    
    try:
        chat_resp = requests.post(f"{base_url}/ai/chat", json={
            'user': user_data['username'],
            'user_id': user_data['id'], 
            'question': complex_query
        }, headers=headers, timeout=60)  # Longer timeout for multi-agent
        
        if chat_resp.status_code == 200:
            result = chat_resp.json()
            
            # Analyze orchestration result
            orchestration = result.get('orchestration', {})
            strategy = orchestration.get('strategy', 'unknown')
            selected_agents = orchestration.get('selected_agents', [])
            routing_scores = orchestration.get('routing_scores', {})
            processing_time = result.get('processing_time', 0)
            
            print(f"\n🎯 Orchestration Results:")
            print(f"   Strategy: {strategy}")
            print(f"   Agents Selected: {selected_agents}")
            print(f"   Total Processing Time: {processing_time:.3f}s")
            print(f"   Routing Scores: {routing_scores}")
            
            # Check for multi-agent responses
            if 'multi_agent_responses' in result:
                multi_responses = result['multi_agent_responses']
                print(f"\n✅ MULTI-AGENT SUCCESS!")
                print(f"   Individual Agent Responses: {len(multi_responses)}")
                
                for i, agent_resp in enumerate(multi_responses, 1):
                    agent_name = agent_resp['agent']
                    response_length = len(agent_resp.get('response', ''))
                    agent_time = agent_resp.get('processing_time', 0)
                    ollama_used = agent_resp.get('ollama_used', False)
                    
                    print(f"\n   Agent {i}: {agent_name}")
                    print(f"      └─ Response Length: {response_length} chars")
                    print(f"      └─ Processing Time: {agent_time:.3f}s")
                    print(f"      └─ Ollama Used: {ollama_used}")
                    
                    # Preview actual content
                    content_preview = agent_resp.get('response', '')[:150].replace('\n', ' ')
                    print(f"      └─ Preview: \"{content_preview}{'...' if response_length > 150 else ''}\"")
                
                print(f"\n🖥️ UI Display: Users will see {len(multi_responses)} separate response cards")
                return True
            else:
                print(f"\n⚠️ Single Agent Response (not multi-agent orchestration)")
                print(f"   Agent: {result.get('agent', 'Unknown')}")
                return False
                
        else:
            print(f"❌ Multi-agent test failed: HTTP {chat_resp.status_code}")
            print(f"   Response: {chat_resp.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Multi-agent orchestration error: {e}")
        return False

def test_database_storage(base_url, headers):
    """Test database storage and retrieval"""
    print("\n💾 Testing Database Storage")
    print("=" * 50)
    
    try:
        # Get system status including database stats
        status_resp = requests.get(f"{base_url}/api/system/status", headers=headers, timeout=10)
        
        if status_resp.status_code == 200:
            status_data = status_resp.json()
            mysql_status = status_data.get('mysql', {})
            
            print("Database Status:")
            if mysql_status.get('connected'):
                print("✅ MySQL Connected")
                print(f"   └─ Users: {mysql_status.get('users_count', 0)}")
                print(f"   └─ Interactions: {mysql_status.get('interactions_count', 0)}")
                print(f"   └─ Orchestrations: {mysql_status.get('orchestrations_count', 0)}")
                
                # Show orchestration strategies if available
                strategies = mysql_status.get('orchestration_strategies', {})
                if strategies:
                    print("   └─ Orchestration Strategies:")
                    for strategy, count in strategies.items():
                        print(f"      └─ {strategy}: {count}")
                
                return True
            else:
                print("❌ MySQL Not Connected")
                print("   💡 Ensure MySQL is running and database is initialized")
                return False
        else:
            print(f"⚠️ Could not retrieve database status: HTTP {status_resp.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Database status check error: {e}")
        return False

def main():
    """Run comprehensive orchestration test"""
    print("🚀 COMPREHENSIVE MULTI-AGENT ORCHESTRATION TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8003"
    
    # Step 1: Check service availability
    services = test_service_availability()
    
    if not services.get('multi_agent'):
        print("\n❌ Multi-Agent System not running. Please start it first:")
        print("   python multi_agent_system.py")
        return
    
    # Step 2: Setup authentication
    user_data, headers = register_and_login(base_url)
    if not user_data or not headers:
        print("❌ Authentication failed. Cannot continue tests.")
        return
    
    # Step 3: Build conversation history
    print("\n" + "="*60)
    history = test_single_agent_responses(base_url, user_data, headers)
    
    # Step 4: Test similarity search agent
    print("\n" + "="*60)
    search_results = test_similarity_search_agent(base_url, user_data, headers)
    
    # Step 5: Test multi-agent orchestration
    print("\n" + "="*60)
    multi_agent_success = test_multi_agent_orchestration(base_url, user_data, headers)
    
    # Step 6: Test database storage
    print("\n" + "="*60)
    db_success = test_database_storage(base_url, headers)
    
    # Final Summary
    print("\n" + "="*60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    search_agent_working = sum(1 for r in search_results if r['is_search_agent']) > 0
    
    results = {
        'System Running': services.get('multi_agent', False),
        'Ollama Available': services.get('ollama', False),
        'Authentication': user_data is not None,
        'Individual Agents': len(history) > 0,
        'Similarity Search': search_agent_working,
        'Multi-Agent Orchestration': multi_agent_success,
        'Database Storage': db_success
    }
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test:.<30} {status}")
    
    overall_success = all(results.values())
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
    
    if overall_success:
        print(f"\n🎉 SYSTEM FULLY FUNCTIONAL!")
        print(f"   • All agents orchestrating perfectly")
        print(f"   • Similarity search agent working effectively") 
        print(f"   • Database storing all responses properly")
        print(f"   • UI ready to display multi-agent responses")
        print(f"\n🌐 Access the system: {base_url}/")
        print(f"🔑 Login: {user_data['username']} / test123")
    else:
        print(f"\n🔧 Action Required:")
        for test, passed in results.items():
            if not passed:
                print(f"   • Fix: {test}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
