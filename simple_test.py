#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.langgraph_multiagent_system import langgraph_multiagent_system

print("Testing LangGraph Multiagent System...")

# Test weather query
try:
    result = langgraph_multiagent_system.process_request(
        user="TestUser",
        user_id=1001, 
        question="What is the weather like today?"
    )
    
    print(f"✅ Agent: {result.get('agent')}")
    print(f"✅ Agents Involved: {result.get('agents_involved')}")
    print(f"✅ Response Preview: {result.get('response', 'No response')[:200]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("Test completed!")
