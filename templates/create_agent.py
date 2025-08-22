#!/usr/bin/env python3
"""
Agent Creation Helper Script
===========================
This script helps clients quickly create new agents using the template.
It prompts for necessary information and generates a working agent file.
"""

import os
import json
import shutil
from typing import Dict, List

def prompt_user(question: str, default: str = "") -> str:
    """Prompt user for input with optional default value"""
    if default:
        response = input(f"{question} [{default}]: ").strip()
        return response if response else default
    else:
        response = input(f"{question}: ").strip()
        while not response:
            response = input(f"Please provide {question.lower()}: ").strip()
        return response

def prompt_list(question: str, count: int, examples: List[str] = None) -> List[str]:
    """Prompt user for a list of items"""
    items = []
    print(f"\n{question} (need {count} items):")
    
    if examples:
        print(f"Examples: {', '.join(examples[:3])}")
    
    for i in range(count):
        while True:
            item = input(f"  {i+1}. ").strip()
            if item:
                items.append(item)
                break
            print("Please provide a value.")
    
    return items

def create_agent_from_template():
    """Interactive agent creation process"""
    print("🤖 Agent Creation Wizard")
    print("=" * 40)
    print("This wizard will help you create a custom agent for the multi-agent system.")
    print("Please provide the following information:\n")
    
    # Basic Information
    print("📋 Basic Information")
    print("-" * 20)
    
    agent_name = prompt_user("Agent class name (e.g., WeatherAnalyzer, RecipeRecommender)")
    # Ensure agent name ends with 'Agent'
    if not agent_name.endswith('Agent'):
        agent_name += 'Agent'
    
    domain_name = prompt_user("Domain name (e.g., Weather Analysis, Recipe Recommendations)")
    domain_description = prompt_user("What does your agent specialize in?")
    brief_description = prompt_user("Brief agent description")
    domain_area = prompt_user("Your expertise area (e.g., meteorology, culinary arts)")
    domain_key = prompt_user("Domain key for metadata (e.g., weather_analysis)", 
                            agent_name.lower().replace('agent', '_analysis'))
    
    # Capabilities
    print("\n🔧 Capabilities")
    print("-" * 15)
    capabilities = prompt_list(
        "Agent capabilities",
        5,
        ["weather_forecasting", "recipe_search", "market_analysis"]
    )
    
    # Keywords
    print("\n🎯 Keywords")
    print("-" * 12)
    keywords = prompt_list(
        "Keywords that trigger your agent",
        7,
        ["weather", "recipe", "stock", "temperature", "cooking", "investment"]
    )
    
    # Expertise Areas
    print("\n💡 Expertise Areas")
    print("-" * 18)
    expertise_areas = prompt_list(
        "Your agent's expertise areas",
        5,
        ["Weather pattern analysis", "Recipe recommendations", "Market analysis"]
    )
    
    # Confidence Terms
    print("\n🎯 Confidence Terms")
    print("-" * 19)
    high_confidence_terms = prompt_list(
        "High confidence terms (phrases that strongly indicate your domain)",
        3,
        ["weather forecast", "recipe recommendation", "stock analysis"]
    )
    
    medium_confidence_terms = prompt_list(
        "Medium confidence terms (general domain terms)",
        3,
        ["sunny", "ingredients", "market"]
    )
    
    activity_terms = prompt_list(
        "Activity-related terms (activities your domain relates to)",
        3,
        ["outdoor activities", "cooking dinner", "investment planning"]
    )
    
    # Categories and Focus Areas
    print("\n📊 Categories")
    print("-" * 13)
    categories = []
    for i in range(3):
        cat_name = prompt_user(f"Category {i+1} name (e.g., short_term_forecast)")
        categories.append(cat_name)
    
    focus_areas = []
    for i in range(3):
        focus_name = prompt_user(f"Focus area {i+1} name (e.g., forecast_accuracy)")
        focus_areas.append(focus_name)
    
    # Generate agent file
    print("\n🚀 Generating Agent...")
    print("-" * 22)
    
    # Read template
    template_path = os.path.join("templates", "sample_agent_template.py")
    if not os.path.exists(template_path):
        print("❌ Template file not found. Please ensure sample_agent_template.py exists.")
        return
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Replace placeholders
    replacements = {
        '[YOUR_AGENT_NAME]': agent_name.replace('Agent', ''),
        '[YOUR_DOMAIN_NAME]': domain_name,
        '[YOUR_DOMAIN_DESCRIPTION]': domain_description,
        '[BRIEF_DESCRIPTION_OF_YOUR_AGENT]': brief_description,
        '[YOUR_DOMAIN_AREA]': domain_area,
        '[YOUR_DOMAIN_KEY]': domain_key,
        
        # Capabilities
        '[CAPABILITY_1]': capabilities[0],
        '[CAPABILITY_2]': capabilities[1],
        '[CAPABILITY_3]': capabilities[2],
        '[CAPABILITY_4]': capabilities[3],
        '[CAPABILITY_5]': capabilities[4],
        
        # Keywords
        '[KEYWORD_1]': keywords[0],
        '[KEYWORD_2]': keywords[1],
        '[KEYWORD_3]': keywords[2],
        '[KEYWORD_4]': keywords[3],
        '[KEYWORD_5]': keywords[4],
        '[KEYWORD_6]': keywords[5],
        '[KEYWORD_7]': keywords[6],
        
        # Expertise areas
        '[EXPERTISE_AREA_1]': expertise_areas[0],
        '[EXPERTISE_AREA_2]': expertise_areas[1],
        '[EXPERTISE_AREA_3]': expertise_areas[2],
        '[EXPERTISE_AREA_4]': expertise_areas[3],
        '[EXPERTISE_AREA_5]': expertise_areas[4],
        
        # Confidence terms
        '[HIGH_CONFIDENCE_TERM_1]': high_confidence_terms[0],
        '[HIGH_CONFIDENCE_TERM_2]': high_confidence_terms[1],
        '[HIGH_CONFIDENCE_TERM_3]': high_confidence_terms[2],
        '[MEDIUM_CONFIDENCE_TERM_1]': medium_confidence_terms[0],
        '[MEDIUM_CONFIDENCE_TERM_2]': medium_confidence_terms[1],
        '[MEDIUM_CONFIDENCE_TERM_3]': medium_confidence_terms[2],
        '[ACTIVITY_TERM_1]': activity_terms[0],
        '[ACTIVITY_TERM_2]': activity_terms[1],
        '[ACTIVITY_TERM_3]': activity_terms[2],
        
        # Categories
        '[CATEGORY_1]': categories[0],
        '[CATEGORY_2]': categories[1],
        '[CATEGORY_3]': categories[2],
        '[FOCUS_AREA_1]': focus_areas[0],
        '[FOCUS_AREA_2]': focus_areas[1],
        '[FOCUS_AREA_3]': focus_areas[2],
        
        # Placeholder terms for categories
        '[CATEGORY_1_TERM_1]': f"{categories[0]}_term1",
        '[CATEGORY_1_TERM_2]': f"{categories[0]}_term2",
        '[CATEGORY_2_TERM_1]': f"{categories[1]}_term1",
        '[CATEGORY_2_TERM_2]': f"{categories[1]}_term2",
        '[CATEGORY_3_TERM_1]': f"{categories[2]}_term1",
        '[CATEGORY_3_TERM_2]': f"{categories[2]}_term2",
        '[FOCUS_1_TERM_1]': f"{focus_areas[0]}_term1",
        '[FOCUS_1_TERM_2]': f"{focus_areas[0]}_term2",
        '[FOCUS_2_TERM_1]': f"{focus_areas[1]}_term1",
        '[FOCUS_2_TERM_2]': f"{focus_areas[1]}_term2",
        '[FOCUS_3_TERM_1]': f"{focus_areas[2]}_term1",
        '[FOCUS_3_TERM_2]': f"{focus_areas[2]}_term2",
        
        # Custom method placeholders (leave for manual implementation)
        '[YOUR_CUSTOM_METHOD_1]': 'custom_method_1',
        '[YOUR_CUSTOM_METHOD_2]': 'custom_method_2',
        '[parameters]': 'parameters',
        '[return_type]': 'Any',
        
        # Recommendation placeholders (leave for manual implementation)
        '[RECOMMENDATION_1_FOR_CATEGORY_1]': f"Recommendation 1 for {categories[0]}",
        '[RECOMMENDATION_2_FOR_CATEGORY_1]': f"Recommendation 2 for {categories[0]}",
        '[RECOMMENDATION_1_FOR_CATEGORY_2]': f"Recommendation 1 for {categories[1]}",
        '[RECOMMENDATION_2_FOR_CATEGORY_2]': f"Recommendation 2 for {categories[1]}",
        '[RECOMMENDATION_1_FOR_CATEGORY_3]': f"Recommendation 1 for {categories[2]}",
        '[RECOMMENDATION_2_FOR_CATEGORY_3]': f"Recommendation 2 for {categories[2]}",
        '[GENERAL_RECOMMENDATION_1]': "General recommendation 1",
        '[GENERAL_RECOMMENDATION_2]': "General recommendation 2"
    }
    
    # Apply replacements
    agent_content = template_content
    for placeholder, replacement in replacements.items():
        agent_content = agent_content.replace(placeholder, replacement)
    
    # Write agent file
    agent_filename = f"{agent_name.lower()}.py"
    agent_path = os.path.join("agents", agent_filename)
    
    try:
        with open(agent_path, 'w') as f:
            f.write(agent_content)
        print(f"✅ Agent file created: {agent_path}")
    except Exception as e:
        print(f"❌ Error creating agent file: {e}")
        return
    
    # Generate configuration entry
    config_entry = {
        "id": agent_name,
        "name": f"{domain_name} Agent",
        "module": f"agents.{agent_name.lower()}",
        "description": brief_description,
        "capabilities": capabilities,
        "priority": 4  # Default priority for new agents
    }
    
    print("\n📝 Agent Configuration Entry:")
    print("-" * 30)
    print("Add this to your core/agents.json file:")
    print(json.dumps(config_entry, indent=2))
    
    # Generate test script
    test_script_content = f'''#!/usr/bin/env python3
"""
Test script for {agent_name}
Generated automatically by the agent creation wizard
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.{agent_name.lower()} import {agent_name}
from core.memory_manager import MemoryManager

def test_agent():
    """Test the {agent_name}"""
    print(f"Testing {agent_name}")
    print("=" * 40)
    
    # Initialize agent (memory manager optional for testing)
    agent = {agent_name}()
    
    # Test queries
    test_queries = [
        "{keywords[0]} {keywords[1]}",
        "What about {keywords[2]} and {keywords[3]}?",
        "Can you help with {domain_area.lower()}?"
    ]
    
    for query in test_queries:
        print(f"\\nTesting query: '{query}'")
        confidence = agent.can_handle(query)
        print(f"Confidence: {confidence:.2f}")
        
        if confidence > 0.3:
            # Mock state for testing
            state = {{
                "question": query,
                "user_id": 1,
                "session_id": "test_session"
            }}
            
            try:
                result = agent.process(state)
                response = result.get('answer', 'No response generated')
                print(f"Response length: {len(response)} characters")
                print(f"Response preview: {response[:100]}...")
            except Exception as e:
                print(f"Error processing: {e}")
        else:
            print("Confidence too low - agent would not handle this query")

if __name__ == "__main__":
    test_agent()
'''
    
    test_script_path = f"test_{agent_name.lower()}.py"
    try:
        with open(test_script_path, 'w') as f:
            f.write(test_script_content)
        print(f"✅ Test script created: {test_script_path}")
    except Exception as e:
        print(f"⚠️  Could not create test script: {e}")
    
    # Final instructions
    print("\n🎉 Agent Creation Complete!")
    print("=" * 30)
    print("Next steps:")
    print(f"1. Review and customize your agent file: {agent_path}")
    print("2. Implement the custom methods marked with 'custom_method_1' and 'custom_method_2'")
    print("3. Add the configuration entry to core/agents.json")
    print("4. Update edge connections in agents.json if needed")
    print(f"5. Test your agent: python {test_script_path}")
    print("6. Restart the FastAPI server to load the new agent")
    print("\n📖 See templates/AGENT_CREATION_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    create_agent_from_template()
