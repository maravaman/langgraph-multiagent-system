#!/usr/bin/env python3
"""
Database Schema Fix - Add missing embedding column and resolve schema issues
"""

import mysql.connector
import json
from config import config

def fix_database_schema():
    """Fix database schema issues including missing embedding column"""
    print("🔧 Fixing Database Schema Issues")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = mysql.connector.connect(**config.get_mysql_connection_params())
        cursor = conn.cursor()
        
        print(f"✅ Connected to database: {config.MYSQL_DATABASE}")
        
        # Use the database
        cursor.execute(f"USE {config.MYSQL_DATABASE}")
        
        # 1. Check if vector_embeddings table exists and has embedding column
        print("\n1. 📊 Checking vector_embeddings table...")
        try:
            cursor.execute("DESCRIBE vector_embeddings")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            
            print(f"   Current columns: {column_names}")
            
            if 'embedding' not in column_names:
                print("   ⚠️ Missing 'embedding' column - adding it...")
                cursor.execute("""
                    ALTER TABLE vector_embeddings 
                    ADD COLUMN embedding JSON NOT NULL AFTER content
                """)
                print("   ✅ Added 'embedding' column")
            else:
                print("   ✅ 'embedding' column exists")
                
        except mysql.connector.Error as e:
            if "doesn't exist" in str(e):
                print("   ⚠️ vector_embeddings table doesn't exist - creating it...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `vector_embeddings` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `user_id` INT NOT NULL,
                        `agent_name` VARCHAR(100) NOT NULL,
                        `content` TEXT NOT NULL,
                        `embedding` JSON NOT NULL,
                        `metadata` JSON,
                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_user_agent (user_id, agent_name),
                        INDEX idx_created_at (created_at)
                    )
                """)
                print("   ✅ Created vector_embeddings table with embedding column")
            else:
                print(f"   ❌ Error checking vector_embeddings table: {e}")
        
        # 2. Ensure agent_interactions table has proper structure
        print("\n2. 📊 Checking agent_interactions table...")
        try:
            cursor.execute("DESCRIBE agent_interactions")
            columns = cursor.fetchall()
            
            response_column = None
            for col in columns:
                if col[0] == 'response':
                    response_column = col[1]
                    break
            
            if response_column and 'longtext' not in response_column.lower():
                print(f"   ⚠️ Response column is {response_column} - upgrading to LONGTEXT...")
                cursor.execute("""
                    ALTER TABLE agent_interactions 
                    MODIFY COLUMN response LONGTEXT NOT NULL
                """)
                print("   ✅ Upgraded response column to LONGTEXT")
            else:
                print("   ✅ Response column is already LONGTEXT")
                
        except mysql.connector.Error as e:
            print(f"   ❌ Error checking agent_interactions: {e}")
        
        # 3. Create multi_agent_orchestration table if missing
        print("\n3. 📊 Checking multi_agent_orchestration table...")
        try:
            cursor.execute("DESCRIBE multi_agent_orchestration")
            print("   ✅ multi_agent_orchestration table exists")
        except mysql.connector.Error as e:
            if "doesn't exist" in str(e):
                print("   ⚠️ multi_agent_orchestration table missing - creating it...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `multi_agent_orchestration` (
                        `id` INT PRIMARY KEY AUTO_INCREMENT,
                        `user_id` INT NOT NULL,
                        `original_query` TEXT NOT NULL,
                        `orchestration_strategy` ENUM('single_agent', 'multi_agent', 'fallback') NOT NULL,
                        `selected_agents` JSON NOT NULL,
                        `agent_responses` LONGTEXT NOT NULL,
                        `final_response` LONGTEXT NOT NULL,
                        `processing_time_ms` INT DEFAULT 0,
                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_user_id (user_id),
                        INDEX idx_strategy (orchestration_strategy),
                        INDEX idx_created_at (created_at)
                    )
                """)
                print("   ✅ Created multi_agent_orchestration table")
            else:
                print(f"   ❌ Error checking multi_agent_orchestration: {e}")
        
        # 4. Update database schema configuration entries
        print("\n4. 🔄 Updating agent configurations in database...")
        try:
            # Remove old legacy agent configurations
            legacy_agents = ['ScenicLocationFinder', 'WaterBodyAnalyzer', 'ForestAnalyzer']
            for agent in legacy_agents:
                cursor.execute("DELETE FROM agent_configurations WHERE agent_name = %s", (agent,))
                print(f"   🗑️ Removed legacy agent: {agent}")
            
            # Add/update current agent configurations
            current_agents = [
                {
                    'agent_name': 'ScenicLocationFinderAgent',
                    'module_path': 'core.agents.scenic_location_finder_agent',
                    'description': 'Specialized agent for finding beautiful scenic locations and tourist destinations',
                    'capabilities': ['location_search', 'tourism_advice', 'geographical_analysis']
                },
                {
                    'agent_name': 'ForestAnalyzerAgent',
                    'module_path': 'core.agents.forest_analyzer_agent',
                    'description': 'Specializes in forest ecology, conservation, and biodiversity analysis',
                    'capabilities': ['forest_ecology', 'biodiversity', 'conservation']
                },
                {
                    'agent_name': 'SearchAgent',
                    'module_path': 'core.agents.search_agent',
                    'description': 'Performs similarity search in user history and memory',
                    'capabilities': ['memory_search', 'similarity_matching', 'history_analysis']
                },
                {
                    'agent_name': 'TemplateAgent',
                    'module_path': 'core.agents.template_agent',
                    'description': 'Template agent for general queries and fallback responses',
                    'capabilities': ['general_query', 'fallback_response', 'template_processing']
                }
            ]
            
            for agent in current_agents:
                cursor.execute("""
                    INSERT INTO agent_configurations 
                    (agent_name, module_path, description, capabilities, is_active) 
                    VALUES (%s, %s, %s, %s, TRUE)
                    ON DUPLICATE KEY UPDATE
                    module_path = VALUES(module_path),
                    description = VALUES(description),
                    capabilities = VALUES(capabilities),
                    is_active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                """, (
                    agent['agent_name'],
                    agent['module_path'],
                    agent['description'],
                    json.dumps(agent['capabilities'])
                ))
                print(f"   ✅ Updated agent configuration: {agent['agent_name']}")
            
        except mysql.connector.Error as e:
            print(f"   ⚠️ Error updating agent configurations: {e}")
            # This is not critical, so we continue
        
        # 5. Clean up old graph edges for legacy agents
        print("\n5. 🔄 Cleaning up graph edges...")
        try:
            # Remove edges referencing legacy agents
            cursor.execute("""
                DELETE FROM graph_edges 
                WHERE source_agent IN ('ScenicLocationFinder', 'WaterBodyAnalyzer', 'ForestAnalyzer')
                OR target_agent IN ('ScenicLocationFinder', 'WaterBodyAnalyzer', 'ForestAnalyzer')
            """)
            print("   🗑️ Cleaned up legacy agent edges")
            
            # Add new edges for current agents
            new_edges = [
                ('ScenicLocationFinderAgent', 'ForestAnalyzerAgent', 'forest_related_query', 1),
                ('ScenicLocationFinderAgent', 'SearchAgent', 'search_required', 1),
                ('ForestAnalyzerAgent', 'SearchAgent', 'search_required', 1),
                ('TemplateAgent', 'SearchAgent', 'search_required', 1),
            ]
            
            for source, target, condition, weight in new_edges:
                cursor.execute("""
                    INSERT INTO graph_edges (source_agent, target_agent, condition, weight, is_active)
                    VALUES (%s, %s, %s, %s, TRUE)
                    ON DUPLICATE KEY UPDATE
                    condition = VALUES(condition),
                    weight = VALUES(weight),
                    is_active = TRUE
                """, (source, target, condition, weight))
            
            print("   ✅ Added new agent edges")
            
        except mysql.connector.Error as e:
            print(f"   ⚠️ Error updating graph edges: {e}")
        
        # Commit all changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Database schema fixes completed successfully!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_schema_fixes():
    """Verify that the schema fixes were successful"""
    print(f"\n🔍 Verifying Schema Fixes")
    print("=" * 30)
    
    try:
        conn = mysql.connector.connect(**config.get_mysql_connection_params())
        cursor = conn.cursor()
        
        cursor.execute(f"USE {config.MYSQL_DATABASE}")
        
        # Check vector_embeddings table
        print("1. Checking vector_embeddings table...")
        cursor.execute("SHOW COLUMNS FROM vector_embeddings LIKE 'embedding'")
        result = cursor.fetchone()
        if result:
            print(f"   ✅ Embedding column exists: {result[1]}")
        else:
            print("   ❌ Embedding column missing")
        
        # Check agent_configurations
        print("\n2. Checking agent configurations...")
        cursor.execute("SELECT agent_name, is_active FROM agent_configurations WHERE is_active = TRUE")
        results = cursor.fetchall()
        print(f"   ✅ Active agents in database: {len(results)}")
        for agent_name, is_active in results:
            print(f"      - {agent_name}: {'Active' if is_active else 'Inactive'}")
        
        # Check graph edges
        print("\n3. Checking graph edges...")
        cursor.execute("SELECT source_agent, target_agent FROM graph_edges WHERE is_active = TRUE")
        results = cursor.fetchall()
        print(f"   ✅ Active edges in database: {len(results)}")
        for source, target in results:
            print(f"      - {source} -> {target}")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Schema verification completed!")
        
    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    try:
        print(f"📋 Database Configuration:")
        print(f"   Host: {config.MYSQL_HOST}")
        print(f"   Database: {config.MYSQL_DATABASE}")
        print()
        
        if fix_database_schema():
            verify_schema_fixes()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the config.py file exists and database is accessible")
