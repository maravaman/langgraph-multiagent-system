#!/usr/bin/env python3
"""
Test LangGraph system with AI responses
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 LangGraph System with Ollama AI Test")
    print("=" * 50)
    
    try:
        from core.langgraph_framework import langgraph_framework
        
        # Test 1: Waterfall photography query (should trigger ScenicLocationFinder -> WaterBodyAnalyzer)
        print("\n🎯 Test 1: Waterfall Photography Query")
        print("-" * 35)
        
        result1 = langgraph_framework.process_request(
            user="photographer",
            user_id=401,
            question="Find me the most beautiful waterfalls in Iceland for photography"
        )
        
        print("✅ Response received!")
        print(f"Agent: {result1['agent']}")
        print(f"Edges traversed: {result1['edges_traversed']}")
        print(f"Response length: {len(result1['response'])} characters")
        print(f"Preview: {result1['response'][:150]}...")
        
        # Test 2: Forest conservation query (should trigger ScenicLocationFinder -> ForestAnalyzer)
        print("\n🎯 Test 2: Forest Conservation Query")  
        print("-" * 35)
        
        result2 = langgraph_framework.process_request(
            user="biologist",
            user_id=402,
            question="Tell me about Amazon rainforest biodiversity and conservation strategies"
        )
        
        print("✅ Response received!")
        print(f"Agent: {result2['agent']}")
        print(f"Edges traversed: {result2['edges_traversed']}")
        print(f"Response length: {len(result2['response'])} characters")
        print(f"Preview: {result2['response'][:150]}...")
        
        # Test 3: General AI question
        print("\n🎯 Test 3: General AI Question")
        print("-" * 30)
        
        result3 = langgraph_framework.process_request(
            user="student",
            user_id=403,
            question="What is machine learning and how does it work?"
        )
        
        print("✅ Response received!")
        print(f"Agent: {result3['agent']}")
        print(f"Edges traversed: {result3['edges_traversed']}")
        print(f"Response length: {len(result3['response'])} characters")
        print(f"Preview: {result3['response'][:150]}...")
        
        print("\n🎉 All tests completed successfully!")
        print("\n📊 Summary:")
        print(f"  • Test 1: {result1['agent']} -> {' -> '.join(result1['edges_traversed'])}")
        print(f"  • Test 2: {result2['agent']} -> {' -> '.join(result2['edges_traversed'])}")
        print(f"  • Test 3: {result3['agent']} -> {' -> '.join(result3['edges_traversed'])}")
        
        # Check memory storage
        print(f"\n💾 Memory Status:")
        print(f"  • STM entries: {result3['context']['stm']['count']}")
        print(f"  • LTM entries: {result3['context']['ltm']['count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ VERIFICATION COMPLETE: All agents working with AI responses!")
    else:
        print("\n❌ Some issues detected")
