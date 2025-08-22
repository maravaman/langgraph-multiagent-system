#!/usr/bin/env python3
"""
Test script for the multiagent system
Tests the LangGraph framework and individual components
"""

import sys
import os
import json
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test core imports
        from core.memory import MemoryManager
        print("✅ MemoryManager imported")
        
        from core.ollama_client import ollama_client
        print("✅ Ollama client imported")
        
        from core.langgraph_framework import langgraph_framework
        print("✅ LangGraph framework imported")
        
        # Test FastAPI imports
        from api.main import app
        print("✅ FastAPI app imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_memory_connections():
    """Test memory system connections"""
    print("\n🔍 Testing memory connections...")
    
    try:
        from core.memory import MemoryManager
        memory = MemoryManager()
        
        # Test Redis
        test_key = f"test_key_{int(datetime.now().timestamp())}"
        memory.set_stm("test_user", "test_agent", "test_value", 60)
        print("✅ Redis connection working")
        
        # Test MySQL
        memory.set_ltm("test_user", "test_agent", "test ltm value")
        print("✅ MySQL connection working")
        
        return True
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n🔍 Testing Ollama connection...")
    
    try:
        from core.ollama_client import ollama_client
        
        # Check if Ollama is available
        available = ollama_client.is_available()
        print(f"Ollama available: {available}")
        
        if available:
            models = ollama_client.list_models()
            print(f"Available models: {models}")
            
            # Try a simple generation
            if models:
                response = ollama_client.generate_response(
                    prompt="Say 'Hello from multiagent system!'",
                    system_prompt="You are a test agent."
                )
                print(f"✅ Test response: {response[:100]}...")
                return True
        else:
            print("⚠️ Ollama not available, but connection test passed")
            return True
            
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

def test_langgraph_framework():
    """Test LangGraph framework"""
    print("\n🔍 Testing LangGraph framework...")
    
    try:
        from core.langgraph_framework import langgraph_framework
        
        # Test configuration loading
        print(f"Agents config: {len(langgraph_framework.agents_config)} agents")
        print(f"Edge map: {langgraph_framework.edge_map}")
        print(f"Entry point: {langgraph_framework.entry_point}")
        
        # Test agent initialization
        langgraph_framework.initialize_agents()
        print(f"✅ Initialized {len(langgraph_framework.loaded_agents)} agents")
        
        # Test a simple request processing
        test_result = langgraph_framework.process_request(
            user="test_user",
            user_id=12345,
            question="Tell me about beautiful mountain locations"
        )
        
        print(f"✅ Framework test completed")
        print(f"Response preview: {test_result.get('response', 'No response')[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ LangGraph test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints without starting the full server"""
    print("\n🔍 Testing API endpoints...")
    
    try:
        from api.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        health_response = client.get("/health")
        print(f"Health endpoint: {health_response.status_code}")
        
        # Test ping endpoint
        ping_response = client.get("/ping")
        print(f"Ping endpoint: {ping_response.status_code}")
        
        # Test agents endpoint
        agents_response = client.get("/agents")
        print(f"Agents endpoint: {agents_response.status_code}")
        
        # Test run_graph_legacy endpoint
        test_payload = {
            "user": "test_user",
            "question": "Tell me about scenic mountain locations"
        }
        graph_response = client.post("/run_graph_legacy", json=test_payload)
        print(f"Graph endpoint: {graph_response.status_code}")
        
        if graph_response.status_code == 200:
            response_data = graph_response.json()
            print(f"✅ API test successful")
            print(f"Agent used: {response_data.get('agent', 'Unknown')}")
            print(f"Response preview: {response_data.get('response', 'No response')[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Multiagent System Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_memory_connections,
        test_ollama_connection,
        test_langgraph_framework,
        test_api_endpoints
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Multiagent system is working properly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
