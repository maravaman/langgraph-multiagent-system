#!/usr/bin/env python3
"""
Direct test of LangGraph framework without server
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_framework_directly():
    """Test the LangGraph framework directly"""
    try:
        print("🧪 Testing LangGraph Framework directly...")
        
        # Import and test the framework
        from core.langgraph_framework import langgraph_framework
        
        print("✅ LangGraph framework imported successfully")
        
        # Test the framework with a sample request
        result = langgraph_framework.process_request(
            user="test_user",
            user_id=1,
            question="What is artificial intelligence?"
        )
        
        print("✅ Framework processing completed")
        print(f"📋 Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Framework test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_manager():
    """Test Memory Manager separately"""
    try:
        print("\n🧪 Testing Memory Manager...")
        
        from core.memory import MemoryManager
        memory_manager = MemoryManager()
        
        print("✅ Memory Manager imported successfully")
        
        # Test STM
        memory_manager.set_stm("test_user", "test_agent", "test_value", 3600)
        stm_value = memory_manager.get_stm("test_user", "test_agent")
        print(f"✅ STM test: {stm_value}")
        
        # Test LTM
        memory_manager.set_ltm("test_user", "test_agent", "test_ltm_value")
        ltm_values = memory_manager.get_ltm_by_agent("test_user", "test_agent")
        print(f"✅ LTM test: {ltm_values}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agents_config():
    """Test agents.json configuration"""
    try:
        print("\n🧪 Testing agents.json configuration...")
        
        import json
        config_path = os.path.join(os.path.dirname(__file__), "core", "agents.json")
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("✅ agents.json loaded successfully")
            agents = config.get('agents', [])
            if isinstance(agents, list):
                agent_names = [agent.get('id', 'Unknown') for agent in agents]
            else:
                agent_names = list(agents.keys()) if agents else []
            print(f"📋 Agents: {agent_names}")
            print(f"📋 Entry point: {config.get('entry_point', 'Not set')}")
            return True
        else:
            print(f"❌ agents.json not found at {config_path}")
            return False
            
    except Exception as e:
        print(f"❌ agents.json test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Direct LangGraph Framework Testing")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Memory Manager
    if test_memory_manager():
        tests_passed += 1
    
    # Test 2: Agents Config
    if test_agents_config():
        tests_passed += 1
    
    # Test 3: Framework
    if test_framework_directly():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All direct framework tests passed!")
    else:
        print("❌ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main()
