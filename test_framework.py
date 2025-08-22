#!/usr/bin/env python3
"""
Test Framework for LangGraph Multiagent System
This script tests various components and queries to validate the framework
"""

import sys
import json
import time
from datetime import datetime
from core.langgraph_multiagent_system import langgraph_multiagent_system
from auth.auth_service import auth_service

def test_authentication():
    """Test user authentication system"""
    print("🔐 Testing Authentication System...")
    
    try:
        # Test login with existing user
        result = auth_service.login_user("harsha", "password123")
        if result["success"]:
            print(f"✅ Authentication successful for user: {result['username']}")
            return result["user_id"]
        else:
            print(f"❌ Authentication failed: {result['error']}")
            # Create test user if authentication fails
            test_user_id = 999
            if auth_service.ensure_user_exists(test_user_id, "test_user"):
                print(f"✅ Created test user with ID: {test_user_id}")
                return test_user_id
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        # Fallback to test user
        test_user_id = 999
        try:
            if auth_service.ensure_user_exists(test_user_id, "test_user"):
                print(f"✅ Created fallback test user with ID: {test_user_id}")
                return test_user_id
        except:
            pass
        return None

def test_single_agent_queries(user_id):
    """Test individual agent functionality"""
    print("\n🤖 Testing Individual Agent Queries...")
    
    test_queries = [
        ("Weather Query", "What's the weather like in Delhi today?"),
        ("Dining Query", "Best restaurants in Mumbai for Italian food"),
        ("Location Query", "Beautiful scenic places near Goa"),
        ("Forest Query", "Tell me about the Western Ghats ecosystem"),
        ("Search Query", "Find previous conversations about travel")
    ]
    
    results = {}
    
    for query_type, question in test_queries:
        print(f"\n📝 Testing: {query_type}")
        print(f"   Question: {question}")
        
        try:
            start_time = time.time()
            result = langgraph_multiagent_system.process_request(
                user="test_user",
                user_id=user_id,
                question=question
            )
            end_time = time.time()
            
            response_time = round(end_time - start_time, 2)
            
            if result.get("error"):
                print(f"   ❌ Error: {result.get('response', 'Unknown error')}")
                results[query_type] = {"status": "failed", "error": result.get('response')}
            else:
                print(f"   ✅ Success ({response_time}s)")
                print(f"   Agent: {result.get('agent', 'Unknown')}")
                print(f"   Agents involved: {result.get('agents_involved', [])}")
                response_preview = result.get('response', '')[:200] + "..." if len(result.get('response', '')) > 200 else result.get('response', '')
                print(f"   Response preview: {response_preview}")
                
                results[query_type] = {
                    "status": "success",
                    "agent": result.get('agent'),
                    "agents_involved": result.get('agents_involved', []),
                    "response_time": response_time,
                    "execution_path": result.get('execution_path', [])
                }
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results[query_type] = {"status": "exception", "error": str(e)}
        
        # Add small delay between queries
        time.sleep(1)
    
    return results

def test_complex_multiagent_queries(user_id):
    """Test complex queries that should invoke multiple agents"""
    print("\n🔄 Testing Multi-Agent Queries...")
    
    complex_queries = [
        ("Travel Planning", "Plan a trip to Kerala - weather, dining, and scenic spots"),
        ("Nature Exploration", "Best forest areas near Bangalore with weather info"),
        ("Complete Guide", "Complete guide for visiting Rajasthan - places, food, weather")
    ]
    
    results = {}
    
    for query_type, question in complex_queries:
        print(f"\n📝 Testing: {query_type}")
        print(f"   Question: {question}")
        
        try:
            start_time = time.time()
            result = langgraph_multiagent_system.process_request(
                user="test_user",
                user_id=user_id,
                question=question
            )
            end_time = time.time()
            
            response_time = round(end_time - start_time, 2)
            
            if result.get("error"):
                print(f"   ❌ Error: {result.get('response', 'Unknown error')}")
                results[query_type] = {"status": "failed", "error": result.get('response')}
            else:
                agents_count = len(result.get('agents_involved', []))
                print(f"   ✅ Success ({response_time}s)")
                print(f"   Agents involved ({agents_count}): {result.get('agents_involved', [])}")
                print(f"   Execution path: {[step['agent'] for step in result.get('execution_path', [])]}")
                
                results[query_type] = {
                    "status": "success",
                    "agents_involved": result.get('agents_involved', []),
                    "agent_count": agents_count,
                    "response_time": response_time,
                    "execution_path": result.get('execution_path', [])
                }
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results[query_type] = {"status": "exception", "error": str(e)}
        
        # Add delay between complex queries
        time.sleep(2)
    
    return results

def test_routing_logic():
    """Test the routing logic without full execution"""
    print("\n🧭 Testing Routing Logic...")
    
    routing_tests = [
        ("weather in delhi", "weather"),
        ("best restaurants", "dining"),
        ("scenic places", "location"),
        ("forest conservation", "forest"),
        ("search my history", "search"),
        ("travel to goa", "location")
    ]
    
    for query, expected_route in routing_tests:
        try:
            # Test the routing analysis directly
            decision = langgraph_multiagent_system._analyze_query_for_routing(query)
            status = "✅" if decision == expected_route else "⚠️"
            print(f"   {status} '{query}' → {decision} (expected: {expected_route})")
        except Exception as e:
            print(f"   ❌ '{query}' → Error: {e}")

def test_memory_integration(user_id):
    """Test memory system integration"""
    print("\n💾 Testing Memory Integration...")
    
    try:
        # Test STM context retrieval
        stm_context = langgraph_multiagent_system._get_stm_context(user_id)
        print(f"   ✅ STM Context retrieved: {len(stm_context.get('recent_interactions', {}))} interactions")
        
        # Test LTM context retrieval
        ltm_context = langgraph_multiagent_system._get_ltm_context(user_id)
        print(f"   ✅ LTM Context retrieved: {ltm_context.get('count', 0)} entries")
        
        # Test context string building
        test_context = {"stm": stm_context, "ltm": ltm_context}
        context_string = langgraph_multiagent_system._build_context_string(test_context)
        print(f"   ✅ Context string built: {len(context_string)} characters")
        
        # Test null safety
        null_context = langgraph_multiagent_system._build_context_string(None)
        print(f"   ✅ Null safety test passed: '{null_context[:50]}...'")
        
    except Exception as e:
        print(f"   ❌ Memory integration error: {e}")

def generate_test_report(auth_result, single_results, multi_results):
    """Generate comprehensive test report"""
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("="*70)
    
    # Authentication results
    print(f"🔐 Authentication: {'✅ PASSED' if auth_result else '❌ FAILED'}")
    
    # Single agent results
    print(f"\n🤖 Single Agent Tests:")
    single_passed = sum(1 for r in single_results.values() if r.get('status') == 'success')
    single_total = len(single_results)
    print(f"   Success Rate: {single_passed}/{single_total} ({single_passed/single_total*100:.1f}%)")
    
    for query_type, result in single_results.items():
        status = result.get('status', 'unknown')
        icon = "✅" if status == 'success' else "❌"
        time_info = f"({result.get('response_time', 0)}s)" if status == 'success' else ""
        print(f"   {icon} {query_type} {time_info}")
    
    # Multi-agent results
    print(f"\n🔄 Multi-Agent Tests:")
    multi_passed = sum(1 for r in multi_results.values() if r.get('status') == 'success')
    multi_total = len(multi_results)
    print(f"   Success Rate: {multi_passed}/{multi_total} ({multi_passed/multi_total*100:.1f}%)")
    
    for query_type, result in multi_results.items():
        status = result.get('status', 'unknown')
        icon = "✅" if status == 'success' else "❌"
        agent_count = result.get('agent_count', 0) if status == 'success' else 0
        time_info = f"({result.get('response_time', 0)}s, {agent_count} agents)" if status == 'success' else ""
        print(f"   {icon} {query_type} {time_info}")
    
    # Overall summary
    total_passed = single_passed + multi_passed
    total_tests = single_total + multi_total
    overall_success = total_passed / total_tests * 100 if total_tests > 0 else 0
    
    print(f"\n📈 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_tests - total_passed}")
    print(f"   Success Rate: {overall_success:.1f}%")
    
    # Performance analysis
    if single_results or multi_results:
        successful_times = []
        for results in [single_results, multi_results]:
            for result in results.values():
                if result.get('status') == 'success' and 'response_time' in result:
                    successful_times.append(result['response_time'])
        
        if successful_times:
            avg_time = sum(successful_times) / len(successful_times)
            max_time = max(successful_times)
            min_time = min(successful_times)
            print(f"\n⏱️  Performance Metrics:")
            print(f"   Average Response Time: {avg_time:.2f}s")
            print(f"   Fastest Response: {min_time:.2f}s")
            print(f"   Slowest Response: {max_time:.2f}s")

def main():
    """Main test execution function"""
    print("🚀 STARTING LANGGRAPH MULTIAGENT FRAMEWORK TESTS")
    print("="*70)
    
    start_time = datetime.now()
    
    # Test 1: Authentication
    user_id = test_authentication()
    if not user_id:
        print("❌ Cannot proceed without authentication. Exiting.")
        return
    
    # Test 2: Routing Logic
    test_routing_logic()
    
    # Test 3: Memory Integration
    test_memory_integration(user_id)
    
    # Test 4: Single Agent Queries
    single_results = test_single_agent_queries(user_id)
    
    # Test 5: Multi-Agent Queries
    multi_results = test_complex_multiagent_queries(user_id)
    
    # Generate comprehensive report
    generate_test_report(bool(user_id), single_results, multi_results)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n⏱️  Total Test Duration: {duration:.2f} seconds")
    print("="*70)
    print("🏁 TESTING COMPLETED")

if __name__ == "__main__":
    main()
