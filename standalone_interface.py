#!/usr/bin/env python3
"""
Standalone Agent Interface
Direct interface to the agent system without requiring a web server
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main interface function"""
    
    print("🤖 LangGraph AI Agent System - Standalone Interface")
    print("=" * 60)
    print("Welcome! You can ask questions about:")
    print("  • Scenic locations and travel destinations")
    print("  • Water bodies, lakes, rivers, and aquatic ecosystems")
    print("  • Forests, ecology, and conservation")
    print("  • Search your conversation history")
    print("  • General AI and technology questions")
    print()
    print("The system automatically routes to the best specialized agent!")
    print("=" * 60)
    print()
    
    try:
        # Import the orchestrator
        from core.orchestrator import run_direct_orchestrator
        
        # Test the agent registry
        from core.agent_registry import AgentRegistry
        from core.memory import MemoryManager
        
        print("🔄 Initializing agent system...")
        
        # Initialize memory and registry
        memory = MemoryManager()
        registry = AgentRegistry(memory_manager=memory)
        
        # Show available agents
        agents = registry.get_agent_names()
        print(f"✅ Loaded {len(agents)} agents: {', '.join(agents)}")
        print()
        
        # Main interaction loop
        user_id = int(datetime.now().timestamp())
        print("💬 Start chatting! (Type 'quit' to exit)")
        print("-" * 40)
        
        while True:
            try:
                # Get user input
                question = input("\n🔮 You: ").strip()
                
                if not question:
                    continue
                    
                if question.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye!")
                    break
                
                # Process the question
                print("\n🤔 Processing...")
                
                result = run_direct_orchestrator(
                    user="standalone_user",
                    user_id=user_id,
                    question=question
                )
                
                # Display the result
                agent_name = result.get("agent", "Unknown")
                response = result.get("response", "No response generated")
                
                print(f"\n🤖 {agent_name}: {response}")
                
                # Show orchestration info if available
                orchestration = result.get("orchestration", {})
                if orchestration:
                    strategy = orchestration.get("strategy", "unknown")
                    print(f"\n📊 Strategy: {strategy}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error processing your question: {e}")
                print("Please try again or rephrase your question.")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are installed and the system is properly configured.")
    except Exception as e:
        print(f"❌ System error: {e}")
        print("The agent system failed to initialize. Please check the configuration.")

if __name__ == "__main__":
    main()
