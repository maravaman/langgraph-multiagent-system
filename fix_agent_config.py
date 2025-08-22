#!/usr/bin/env python3
"""
Simple Database Agent Configuration Fix
"""

import mysql.connector
import json
from config import config

def fix_agent_config():
    """Fix agent configuration in database"""
    print("🔧 Fixing Agent Configurations")
    print("=" * 40)
    
    try:
        # Connect to database
        conn = mysql.connector.connect(**config.get_mysql_connection_params())
        cursor = conn.cursor()
        
        print(f"✅ Connected to database: {config.MYSQL_DATABASE}")
        cursor.execute(f"USE {config.MYSQL_DATABASE}")
        
        # Clear old configurations
        print("\n1. Clearing legacy agent configurations...")
        legacy_agents = ['ScenicLocationFinder', 'WaterBodyAnalyzer', 'ForestAnalyzer']
        for agent in legacy_agents:
            cursor.execute("DELETE FROM agent_configurations WHERE agent_name = %s", (agent,))
            print(f"   🗑️ Removed: {agent}")
        
        placeholders = ','.join(['%s'] * len(legacy_agents))
        cursor.execute(f"DELETE FROM graph_edges WHERE source_agent IN ({placeholders}) OR target_agent IN ({placeholders})", 
                      legacy_agents + legacy_agents)
        print("   🗑️ Removed legacy edges")
        
        # Add current agents
        print("\n2. Adding current agent configurations...")
        current_agents = [
            ('ScenicLocationFinderAgent', 'core.agents.scenic_location_finder_agent', 
             'Specialized agent for finding beautiful scenic locations'),
            ('ForestAnalyzerAgent', 'core.agents.forest_analyzer_agent',
             'Specializes in forest ecology, conservation, and biodiversity'),
            ('SearchAgent', 'core.agents.search_agent',
             'Performs similarity search in user history and memory'),
            ('TemplateAgent', 'core.agents.template_agent',
             'Template agent for general queries and fallback responses')
        ]
        
        for agent_name, module_path, description in current_agents:
            cursor.execute("""
                INSERT IGNORE INTO agent_configurations 
                (agent_name, module_path, description, is_active) 
                VALUES (%s, %s, %s, TRUE)
            """, (agent_name, module_path, description))
            print(f"   ✅ Added: {agent_name}")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Agent configuration fixes completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_agent_config()
