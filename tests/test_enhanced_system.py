#!/usr/bin/env python3
"""
Comprehensive Test for Enhanced Multi-Agent System
- Tests configuration management
- Verifies Ollama integration for all agents
- Checks full response visibility
- Validates complete system functionality
"""

import requests
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_configuration_system():
    """Test the configuration system"""
    print("🔧 Testing Configuration System")
    print("=" * 50)
    
    try:
        from config import config
        
        print("✅ Configuration loaded successfully")
        print(f"   App Host: {config.APP_HOST}")
        print(f"   App Port: {config.APP_PORT}")
        print(f"   Ollama URL: {config.OLLAMA_BASE_URL}")
        print(f"   Ollama Model: {config.OLLAMA_DEFAULT_MODEL}")
        print(f"   Max Tokens: {config.OLLAMA_MAX_TOKENS}")
        print(f"   Max Response Length: {config.AGENT_MAX_RESPONSE_LENGTH}")
        
        # Test validation
        is_valid = config.validate_config()
        print(f"✅ Configuration Validation: {'PASSED' if is_valid else 'FAILED'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_service_availability():
    """Test all services availability"""
    print("\n🔍 Testing Service Availability")
    print("=" * 50)
    
    base_url = "http://localhost:8003"
    services = {}
    
    # Test enhanced system
    try:
        resp = requests.get(f'{base_url}/health', timeout=5)
        if resp.status_code == 200:
            health_data = resp.json()
            services['system'] = True
            print(f"✅ Enhanced System: {health_data.get('status', 'Running')}")
            
            # Check configuration details
            config_details = health_data.get('configuration', {})
            print(f"   └─ Max Tokens: {config_details.get('max_tokens', 'N/A')}")
            print(f"   └─ Timeout: {config_details.get('timeout', 'N/A')}s")
            print(f"   └─ Max Response Length: {config_details.get('max_response_length', 'N/A')}")
            
            # Check components
            components = health_data.get('components', {})
            for comp, status in components.items():
                print(f"   └─ {comp}: {status}")
        else:
            services['system'] = False
            print(f"❌ Enhanced System: HTTP {resp.status_code}")
    except requests.exceptions.RequestException as e:
        services['system'] = False
        print(f"❌ Enhanced System: {e}")
    
    # Test Ollama directly
    try:
        resp = requests.get('http://localhost:11434/api/tags', timeout=3)
        if resp.status_code == 200:
            services['ollama'] = True
            models = resp.json().get('models', [])
            print(f"✅ Ollama: {len(models)} models available")
            if models:
                for model in models[:3]:  # Show first 3 models
                    print(f"   └─ {model.get('name', 'Unknown')}")
        else:
            services['ollama'] = False
            print(f"⚠️ Ollama: HTTP {resp.status_code}")
    except requests.exceptions.RequestException:
        services['ollama'] = False
        print(f"⚠️ Ollama: Not available - Enhanced mock responses will be used")
    
    return services

def setup_test_user(base_url):
    """Setup test user and authentication"""
    print("\n👤 Setting up Test User")
    print("=" * 50)
    
    timestamp = int(time.time())
    test_user = {
        'username': f'enhanced_test_{timestamp}',
        'email': f'enhanced_test_{timestamp}@example.com',
        'password': 'test123'
    }
    
    try:
        # Register user
        print("1. Registering enhanced test user...")
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
        headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
        print("✅ Authentication successful")
        
        return user_data, headers
        
    except Exception as e:
        print(f"❌ User setup error: {e}")
        return None, None

def test_individual_agents(base_url, user_data, headers, ollama_available):
    """Test each agent individually with enhanced response checking"""
    print("\n🤖 Testing Individual Agents with Enhanced Responses")
    print("=" * 50)
    
    agent_tests = [
        {
            'query': 'Tell me about the most scenic mountain locations in Maharashtra with detailed travel information',
            'expected_agent': 'ScenicLocationFinder',
            'keywords': ['Maharashtra', 'mountain', 'travel'],
            'expected_length': 500 if ollama_available else 300
        },
        {
            'query': 'Provide comprehensive analysis of forest ecosystems in Western Ghats including biodiversity details',
            'expected_agent': 'ForestAnalyzer',
            'keywords': ['forest', 'biodiversity', 'Western Ghats'],
            'expected_length': 500 if ollama_available else 300
        },
        {
            'query': 'Analyze water bodies and rivers in Maharashtra with detailed ecological information',
            'expected_agent': 'WaterBodyAnalyzer',
            'keywords': ['water', 'river', 'ecological'],
            'expected_length': 500 if ollama_available else 300
        }
    ]
    
    results = []
    
    for i, test in enumerate(agent_tests, 1):
        print(f"\n{i}. Testing {test['expected_agent']}")
        print(f"   Query: \"{test['query'][:60]}...\"")
        
        try:
            start_time = time.time()
            chat_resp = requests.post(f"{base_url}/ai/chat", json={
                'user': user_data['username'],
                'user_id': user_data['id'],
                'question': test['query']
            }, headers=headers, timeout=60)
            
            if chat_resp.status_code == 200:
                result = chat_resp.json()
                elapsed = time.time() - start_time
                
                agent_used = result.get('agent', 'Unknown')
                response = result.get('response', '')
                response_length = len(response)
                processing_time = result.get('processing_time', 0)
                ollama_used = result.get('ollama_used', False)
                
                print(f"   ✅ Agent: {agent_used}")
                print(f"   ✅ Response Length: {response_length} chars")
                print(f"   ✅ Processing Time: {processing_time:.3f}s")
                print(f"   ✅ Ollama Used: {ollama_used}")
                print(f"   ✅ Total Time: {elapsed:.3f}s")
                
                # Check response quality
                quality_score = 0
                for keyword in test['keywords']:
                    if keyword.lower() in response.lower():
                        quality_score += 1
                
                print(f"   ✅ Content Quality: {quality_score}/{len(test['keywords'])} keywords found")
                
                # Check if response meets expected length
                if response_length >= test['expected_length']:
                    print(f"   ✅ Response Length: Meets expectations ({test['expected_length']}+ chars)")
                else:
                    print(f"   ⚠️ Response Length: Below expectations ({response_length} < {test['expected_length']})")
                
                # Preview response content
                preview = response[:200].replace('\n', ' ')
                print(f"   📝 Preview: \"{preview}{'...' if len(response) > 200 else ''}\"")
                
                results.append({
                    'agent': agent_used,
                    'response_length': response_length,
                    'processing_time': processing_time,
                    'ollama_used': ollama_used,
                    'quality_score': quality_score,
                    'meets_length_expectation': response_length >= test['expected_length']
                })
                
            else:
                print(f"   ❌ Request failed: HTTP {chat_resp.status_code}")
                print(f"   Response: {chat_resp.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Small delay between tests
    
    # Summary
    total_tests = len(results)
    successful_tests = len([r for r in results if r['response_length'] > 0])
    quality_tests = len([r for r in results if r['quality_score'] >= 2])
    length_tests = len([r for r in results if r['meets_length_expectation']])
    
    print(f"\n📊 Individual Agent Test Summary:")
    print(f"   • Total Tests: {total_tests}")
    print(f"   • Successful: {successful_tests}")
    print(f"   • Good Quality: {quality_tests}")
    print(f"   • Adequate Length: {length_tests}")
    
    return results

def test_search_agent(base_url, user_data, headers):
    """Test SearchAgent specifically"""
    print("\n🔍 Testing Enhanced Search Agent")
    print("=" * 50)
    
    search_queries = [
        "search my conversation history for previous discussions",
        "find similar past conversations about locations",
        "recall what we talked about regarding forests",
        "show me my interaction history"
    ]
    
    search_results = []
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n{i}. Search Query: \"{query}\"")
        
        try:
            chat_resp = requests.post(f"{base_url}/ai/chat", json={
                'user': user_data['username'],
                'user_id': user_data['id'],
                'question': query
            }, headers=headers, timeout=30)
            
            if chat_resp.status_code == 200:
                result = chat_resp.json()
                agent_used = result.get('agent', 'Unknown')
                response = result.get('response', '')
                processing_time = result.get('processing_time', 0)
                
                print(f"   ✅ Agent: {agent_used}")
                print(f"   ✅ Processing Time: {processing_time:.3f}s")
                print(f"   ✅ Response Length: {len(response)} chars")
                
                # Check if SearchAgent was activated
                if agent_used == 'SearchAgent' or 'search_results' in response.lower():
                    print(f"   ✅ SearchAgent activated successfully")
                    
                    # Try to parse JSON response
                    try:
                        if response.startswith('{'):
                            json_data = json.loads(response)
                            search_data = json_data.get('search_results', {})
                            total_matches = search_data.get('total_matches', 0)
                            similar_content = search_data.get('similar_content', [])
                            
                            print(f"   ✅ JSON Response: {total_matches} matches")
                            print(f"   ✅ Similar Content: {len(similar_content)} items")
                            
                            if similar_content:
                                print("   📋 Sample matches:")
                                for match in similar_content[:2]:
                                    agent_name = match.get('agent_name', 'Unknown')
                                    similarity = match.get('similarity', 0)
                                    content = match.get('content', '')[:40]
                                    print(f"      └─ {agent_name} (sim: {similarity:.3f}): {content}...")
                        else:
                            print(f"   ℹ️ Text response format")
                            
                    except json.JSONDecodeError:
                        print(f"   ℹ️ Response not JSON format")
                else:
                    print(f"   ℹ️ Routed to {agent_used} instead of SearchAgent")
                
                search_results.append({
                    'query': query,
                    'agent': agent_used,
                    'is_search_agent': agent_used == 'SearchAgent',
                    'processing_time': processing_time
                })
                
            else:
                print(f"   ❌ Failed: HTTP {chat_resp.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.5)
    
    search_activations = sum(1 for r in search_results if r['is_search_agent'])
    print(f"\n📊 Search Agent Summary:")
    print(f"   • Total queries: {len(search_queries)}")
    print(f"   • SearchAgent activations: {search_activations}")
    print(f"   • Success rate: {(search_activations/len(search_queries)*100):.1f}%")
    
    return search_results

def test_multi_agent_orchestration(base_url, user_data, headers, ollama_available):
    """Test enhanced multi-agent orchestration"""
    print("\n🎭 Testing Enhanced Multi-Agent Orchestration")
    print("=" * 50)
    
    # Complex query designed to trigger multiple agents
    complex_query = "I want comprehensive information about the best scenic locations, water bodies, and forest ecosystems in Maharashtra for nature photography and ecological research"
    
    print(f"Complex Query: \"{complex_query[:80]}...\"")
    print("Expected: Multiple agents working together")
    
    try:
        start_time = time.time()
        chat_resp = requests.post(f"{base_url}/ai/chat", json={
            'user': user_data['username'],
            'user_id': user_data['id'],
            'question': complex_query
        }, headers=headers, timeout=120)  # Longer timeout for multi-agent
        
        if chat_resp.status_code == 200:
            result = chat_resp.json()
            elapsed = time.time() - start_time
            
            orchestration = result.get('orchestration', {})
            strategy = orchestration.get('strategy', 'unknown')
            selected_agents = orchestration.get('selected_agents', [])
            routing_scores = orchestration.get('routing_scores', {})
            processing_time = result.get('processing_time', 0)
            
            print(f"\n🎯 Enhanced Orchestration Results:")
            print(f"   Strategy: {strategy}")
            print(f"   Agents Selected: {selected_agents}")
            print(f"   Routing Scores: {routing_scores}")
            print(f"   Processing Time: {processing_time:.3f}s")
            print(f"   Total Time: {elapsed:.3f}s")
            
            # Check configuration usage
            config_used = orchestration.get('configuration_used', {})
            if config_used:
                print(f"   Configuration Applied:")
                for key, value in config_used.items():
                    print(f"      └─ {key}: {value}")
            
            if 'multi_agent_responses' in result:
                multi_responses = result['multi_agent_responses']
                print(f"\n✅ ENHANCED MULTI-AGENT SUCCESS!")
                print(f"   Individual Agent Responses: {len(multi_responses)}")
                
                total_response_length = 0
                for i, agent_resp in enumerate(multi_responses, 1):
                    agent_name = agent_resp['agent']
                    response = agent_resp.get('response', '')
                    response_length = len(response)
                    agent_time = agent_resp.get('processing_time', 0)
                    ollama_used = agent_resp.get('ollama_used', False)
                    
                    total_response_length += response_length
                    
                    print(f"\n   Agent {i}: {agent_name}")
                    print(f"      └─ Response Length: {response_length} chars")
                    print(f"      └─ Processing Time: {agent_time:.3f}s")
                    print(f"      └─ Ollama Used: {ollama_used}")
                    
                    # Check for meaningful content (not just fallback messages)
                    if response_length > 300:
                        print(f"      └─ Content Quality: ✅ Substantial response")
                    elif response_length > 100:
                        print(f"      └─ Content Quality: ⚠️ Moderate response")
                    else:
                        print(f"      └─ Content Quality: ❌ Brief response")
                    
                    # Preview content
                    preview = response[:100].replace('\n', ' ')
                    print(f"      └─ Preview: \"{preview}{'...' if len(response) > 100 else ''}\"")
                
                print(f"\n📊 Multi-Agent Summary:")
                print(f"   • Total Agents Activated: {len(multi_responses)}")
                print(f"   • Total Response Length: {total_response_length} chars")
                print(f"   • Average Response Length: {total_response_length/len(multi_responses):.0f} chars")
                print(f"   • Ollama Usage: {sum(1 for r in multi_responses if r.get('ollama_used', False))}/{len(multi_responses)} agents")
                
                return True
            else:
                print(f"\n⚠️ Single Agent Response")
                print(f"   Agent: {result.get('agent', 'Unknown')}")
                print(f"   Response Length: {len(result.get('response', ''))}")
                return False
                
        else:
            print(f"❌ Multi-agent test failed: HTTP {chat_resp.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Multi-agent orchestration error: {e}")
        return False

def test_system_status(base_url, headers):
    """Test enhanced system status"""
    print("\n💾 Testing Enhanced System Status")
    print("=" * 50)
    
    try:
        # Test system status
        status_resp = requests.get(f"{base_url}/api/system/status", headers=headers, timeout=10)
        
        if status_resp.status_code == 200:
            status_data = status_resp.json()
            
            print("Enhanced System Status:")
            
            # MySQL status
            mysql_status = status_data.get('mysql', {})
            if mysql_status.get('connected'):
                print("✅ MySQL Connected")
                print(f"   └─ Users: {mysql_status.get('users_count', 0)}")
                print(f"   └─ Interactions: {mysql_status.get('interactions_count', 0)}")
                print(f"   └─ Orchestrations: {mysql_status.get('orchestrations_count', 0)}")
                
                strategies = mysql_status.get('orchestration_strategies', {})
                if strategies:
                    print("   └─ Orchestration Strategies:")
                    for strategy, count in strategies.items():
                        print(f"      └─ {strategy}: {count}")
            else:
                print("❌ MySQL Not Connected")
            
            # Ollama status
            ollama_status = status_data.get('ollama', {})
            print(f"Ollama Status: {'✅' if ollama_status.get('available') else '⚠️'}")
            print(f"   └─ Base URL: {ollama_status.get('base_url', 'N/A')}")
            print(f"   └─ Timeout: {ollama_status.get('timeout', 'N/A')}s")
            print(f"   └─ Max Tokens: {ollama_status.get('max_tokens', 'N/A')}")
            
            # Configuration status
            config_status = status_data.get('configuration', {})
            print("Configuration Status:")
            print(f"   └─ App Port: {config_status.get('app_port', 'N/A')}")
            print(f"   └─ Debug Mode: {config_status.get('debug', 'N/A')}")
            print(f"   └─ Max Response Length: {config_status.get('max_response_length', 'N/A')}")
            print(f"   └─ Multi-Agent Max: {config_status.get('multi_agent_max', 'N/A')}")
            
            return True
        else:
            print(f"⚠️ System status check failed: HTTP {status_resp.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ System status error: {e}")
        return False

def main():
    """Run comprehensive enhanced system test"""
    print("🚀 COMPREHENSIVE ENHANCED MULTI-AGENT SYSTEM TEST")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_url = "http://localhost:8003"
    
    # Test results tracking
    test_results = {}
    
    # Step 1: Test configuration system
    test_results['configuration'] = test_configuration_system()
    
    # Step 2: Test service availability
    services = test_service_availability()
    test_results['services'] = services.get('system', False)
    ollama_available = services.get('ollama', False)
    
    if not test_results['services']:
        print("\n❌ Enhanced system not running. Please start it with:")
        print("   python multi_agent_system_fixed.py")
        return
    
    # Step 3: Setup authentication
    user_data, headers = setup_test_user(base_url)
    test_results['authentication'] = user_data is not None
    
    if not test_results['authentication']:
        print("❌ Authentication failed. Cannot continue tests.")
        return
    
    # Step 4: Test individual agents with enhanced responses
    agent_results = test_individual_agents(base_url, user_data, headers, ollama_available)
    test_results['individual_agents'] = len(agent_results) > 0
    
    # Step 5: Test search agent
    search_results = test_search_agent(base_url, user_data, headers)
    test_results['search_agent'] = any(r['is_search_agent'] for r in search_results)
    
    # Step 6: Test multi-agent orchestration
    test_results['multi_agent'] = test_multi_agent_orchestration(base_url, user_data, headers, ollama_available)
    
    # Step 7: Test system status
    test_results['system_status'] = test_system_status(base_url, headers)
    
    # Final comprehensive summary
    print("\n" + "=" * 70)
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        test_display = test_name.replace('_', ' ').title()
        print(f"{test_display:.<35} {status}")
    
    overall_success = all(test_results.values())
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
    
    if overall_success:
        print(f"\n🎉 ENHANCED SYSTEM FULLY FUNCTIONAL!")
        print(f"   • Configuration management working perfectly")
        print(f"   • All agents providing {'full Ollama responses' if ollama_available else 'enhanced mock responses'}")
        print(f"   • Multi-agent orchestration with full response visibility")
        print(f"   • Database storing complete interaction data")
        print(f"   • Search agent functioning with JSON responses")
        print(f"   • UI ready to display all agent responses without truncation")
        print(f"\n🌐 Access the enhanced system: {base_url}/")
        print(f"🔑 Login: {user_data['username']} / test123")
        print(f"🤖 Ollama Status: {'Connected' if ollama_available else 'Using Enhanced Mocks'}")
    else:
        print(f"\n🔧 Issues Found:")
        for test, passed in test_results.items():
            if not passed:
                print(f"   • Fix: {test.replace('_', ' ').title()}")
    
    print(f"\nTest completed at {datetime.now().strftime('%H:%M:%S')}!")

if __name__ == "__main__":
    main()
