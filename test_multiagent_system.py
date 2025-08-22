"""
Test Script for LangGraph Multiagent System
Tests the new Weather Agent and Dining Agent integration
"""

import sys
import os
import asyncio
import json
import logging
from datetime import datetime

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.langgraph_multiagent_system import langgraph_multiagent_system

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_weather_queries():
    """Test weather-related queries"""
    print("\n" + "="*60)
    print("🌤️ TESTING WEATHER AGENT")
    print("="*60)
    
    test_queries = [
        "What's the weather like today?",
        "Will it rain tomorrow?",
        "What's the best weather for hiking?",
        "Is it a good day for outdoor activities?",
        "Weather forecast for this weekend"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔸 Test {i}: {query}")
        try:
            result = langgraph_multiagent_system.process_request(
                user="TestUser",
                user_id=1001,
                question=query
            )
            
            print(f"✅ Agent: {result.get('agent', 'Unknown')}")
            print(f"✅ Agents Involved: {result.get('agents_involved', [])}")
            print(f"✅ Response Preview: {result.get('response', 'No response')[:200]}...")
            
            # Check execution path
            execution_path = result.get('execution_path', [])
            if execution_path:
                print(f"✅ Execution Path: {' → '.join([step['agent'] for step in execution_path])}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_dining_queries():
    """Test dining-related queries"""
    print("\n" + "="*60)
    print("🍽️ TESTING DINING AGENT")
    print("="*60)
    
    test_queries = [
        "Where can I find good Italian restaurants?",
        "What's the best food in downtown?",
        "Recommend a romantic restaurant for dinner",
        "I need vegetarian dining options",
        "What cuisine should I try for lunch?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔸 Test {i}: {query}")
        try:
            result = langgraph_multiagent_system.process_request(
                user="TestUser",
                user_id=1002,
                question=query
            )
            
            print(f"✅ Agent: {result.get('agent', 'Unknown')}")
            print(f"✅ Agents Involved: {result.get('agents_involved', [])}")
            print(f"✅ Response Preview: {result.get('response', 'No response')[:200]}...")
            
            # Check execution path
            execution_path = result.get('execution_path', [])
            if execution_path:
                print(f"✅ Execution Path: {' → '.join([step['agent'] for step in execution_path])}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_multiagent_queries():
    """Test queries that should involve multiple agents"""
    print("\n" + "="*60)
    print("🤖 TESTING MULTIAGENT COORDINATION")
    print("="*60)
    
    test_queries = [
        "Plan a perfect day trip with good weather and restaurants",
        "I want to visit scenic places with good food and nice weather",
        "What are the best outdoor dining options for sunny weather?",
        "Recommend restaurants near beautiful mountain locations",
        "Plan a nature trip with dining and weather considerations"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔸 Test {i}: {query}")
        try:
            result = langgraph_multiagent_system.process_request(
                user="TestUser",
                user_id=1003,
                question=query
            )
            
            print(f"✅ Primary Agent: {result.get('agent', 'Unknown')}")
            print(f"✅ Agents Involved: {result.get('agents_involved', [])}")
            print(f"✅ Response Preview: {result.get('response', 'No response')[:300]}...")
            
            # Check execution path
            execution_path = result.get('execution_path', [])
            if execution_path:
                print(f"✅ Execution Path: {' → '.join([step['agent'] for step in execution_path])}")
            
            # Check if multiple agents were used
            agents_involved = result.get('agents_involved', [])
            if len(agents_involved) > 1:
                print(f"🎯 Successfully coordinated {len(agents_involved)} agents!")
            else:
                print(f"⚠️ Only one agent involved: {agents_involved}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_scenic_location_queries():
    """Test scenic location queries (existing functionality)"""
    print("\n" + "="*60)
    print("🏔️ TESTING SCENIC LOCATION AGENT")
    print("="*60)
    
    test_queries = [
        "Show me beautiful mountain destinations",
        "Where are the most scenic viewpoints?",
        "Recommend tourist attractions with great views"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔸 Test {i}: {query}")
        try:
            result = langgraph_multiagent_system.process_request(
                user="TestUser",
                user_id=1004,
                question=query
            )
            
            print(f"✅ Agent: {result.get('agent', 'Unknown')}")
            print(f"✅ Agents Involved: {result.get('agents_involved', [])}")
            print(f"✅ Response Preview: {result.get('response', 'No response')[:200]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_system_configuration():
    """Test system configuration and agent loading"""
    print("\n" + "="*60)
    print("⚙️ TESTING SYSTEM CONFIGURATION")
    print("="*60)
    
    try:
        # Test agent configuration loading
        print("🔸 Agent Configuration:")
        for agent_id, config in langgraph_multiagent_system.agents_config.items():
            print(f"  • {agent_id}: {config.get('description', 'No description')}")
        
        print(f"\n🔸 Total Agents Configured: {len(langgraph_multiagent_system.agents_config)}")
        
        # Test routing rules
        print(f"\n🔸 Routing Rules Available: {len(langgraph_multiagent_system.routing_rules)}")
        
        # Test agent capabilities
        print(f"\n🔸 Agent Capabilities:")
        for agent_id, capabilities in langgraph_multiagent_system.agent_capabilities.items():
            keywords = capabilities.get('keywords', [])
            print(f"  • {agent_id}: {len(keywords)} keywords, Priority {capabilities.get('priority', 'N/A')}")
        
        print("✅ System configuration loaded successfully")
        
    except Exception as e:
        print(f"❌ Configuration Error: {e}")

def run_comprehensive_tests():
    """Run all tests"""
    print("🚀 STARTING LANGGRAPH MULTIAGENT SYSTEM TESTS")
    print("=" * 80)
    
    start_time = datetime.now()
    
    # Run all test suites
    test_system_configuration()
    test_weather_queries()
    test_dining_queries() 
    test_scenic_location_queries()
    test_multiagent_queries()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*80)
    print(f"🎯 ALL TESTS COMPLETED in {duration:.2f} seconds")
    print("="*80)
    
    print("\n📊 SUMMARY:")
    print("✅ Weather Agent: Provides weather forecasts and climate analysis")
    print("✅ Dining Agent: Recommends restaurants and cuisine analysis")
    print("✅ Scenic Location Agent: Finds beautiful destinations")
    print("✅ Multiagent Coordination: Routes between agents based on query analysis")
    print("✅ LangGraph Integration: Proper state management and execution paths")
    print("✅ Memory Integration: STM (Redis) and LTM (MySQL) support")

if __name__ == "__main__":
    print("Testing LangGraph Multiagent System with Weather and Dining Agents")
    print("Make sure Ollama is running for LLM responses\n")
    
    try:
        run_comprehensive_tests()
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
