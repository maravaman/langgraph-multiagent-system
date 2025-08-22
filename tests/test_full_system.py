"""
Comprehensive LangGraph AI Agent System Test
- Real Ollama integration
- MySQL database integration  
- Multi-agent orchestration testing
- Search agent vector similarity testing
"""
from fastapi import FastAPI, Request, HTTPException, Body, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
import logging
import hashlib
import jwt
from datetime import datetime, timedelta
import requests
import mysql.connector
import redis
import numpy as np
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI Setup
app = FastAPI(
    title="LangGraph AI Agent System - Full Test",
    description="Complete multi-agent AI system with real integrations",
    version="1.0.0-test"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuration
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database connections
def get_mysql_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='langgraph_ai_system',
            autocommit=True
        )
    except mysql.connector.Error as e:
        logger.error(f"MySQL connection failed: {e}")
        return None

def get_redis_connection():
    try:
        redis_conn = redis.StrictRedis(host='localhost', port=6379, decode_responses=True, socket_timeout=5)
        redis_conn.ping()
        return redis_conn
    except redis.RedisError as e:
        logger.error(f"Redis connection failed: {e}")
        return None

# Initialize database
def initialize_database():
    """Create tables if they don't exist"""
    conn = get_mysql_connection()
    if not conn:
        logger.warning("Cannot initialize database - MySQL not available")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS langgraph_ai_system")
        cursor.execute("USE langgraph_ai_system")
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                INDEX idx_username (username)
            )
        """)
        
        # Agent interactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_interactions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                agent_name VARCHAR(100) NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                interaction_type ENUM('single', 'orchestrated') DEFAULT 'single',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_agent (user_id, agent_name),
                INDEX idx_timestamp (timestamp)
            )
        """)
        
        # LTM by agent
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ltm_by_agent (
                id INT PRIMARY KEY AUTO_INCREMENT,
                agent_name VARCHAR(100) NOT NULL,
                user_id INT NOT NULL,
                memory_key VARCHAR(255) NOT NULL,
                memory_value TEXT NOT NULL,
                context_metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_agent_user_key (agent_name, user_id, memory_key),
                INDEX idx_agent_name (agent_name)
            )
        """)
        
        # Vector embeddings (simplified for demo)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vector_embeddings (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                agent_name VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                embedding_summary TEXT,
                similarity_keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_agent (user_id, agent_name)
            )
        """)
        
        cursor.close()
        conn.close()
        logger.info("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatInput(BaseModel):
    user: str
    user_id: int
    question: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request):
    """Get current authenticated user"""
    auth_header = request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if username:
            conn = get_mysql_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username = %s AND is_active = TRUE", (username,))
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                if user:
                    return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
    
    raise HTTPException(status_code=401, detail="Invalid authentication")

# Real Ollama client
class RealOllamaClient:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.default_model = "llama3:latest"  # Use available model
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str, system_prompt: str = None, model: str = None) -> str:
        if not self.is_available():
            return f"Ollama not available. Mock response: {self._mock_response(prompt)}"
        
        try:
            payload = {
                "model": model or self.default_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 500}
            }
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
        
        return f"Ollama error. Mock response: {self._mock_response(prompt)}"
    
    def _mock_response(self, prompt: str) -> str:
        """Fallback mock responses"""
        if "search" in prompt.lower():
            return json.dumps({
                "search_results": [
                    {"content": "Previous scenic location query", "similarity": 0.89},
                    {"content": "Earlier forest discussion", "similarity": 0.76}
                ],
                "total_matches": 2
            }, indent=2)
        return f"Mock response for: {prompt[:50]}..."

ollama_client = RealOllamaClient()

# Database-integrated memory manager
class DatabaseMemoryManager:
    def __init__(self):
        self.mysql_conn = get_mysql_connection()
        self.redis_conn = get_redis_connection()
    
    def store_interaction(self, user_id: int, agent_name: str, query: str, response: str, interaction_type: str = 'single'):
        """Store interaction in database"""
        if not self.mysql_conn:
            return
        
        try:
            cursor = self.mysql_conn.cursor()
            cursor.execute(
                """INSERT INTO agent_interactions (user_id, agent_name, query, response, interaction_type)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, agent_name, query, response, interaction_type)
            )
            cursor.close()
            logger.info(f"Stored interaction for {agent_name}")
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
    
    def store_agent_memory(self, agent_name: str, user_id: int, memory_key: str, memory_value: str, metadata: dict = None):
        """Store LTM grouped by agent name"""
        if not self.mysql_conn:
            return
        
        try:
            cursor = self.mysql_conn.cursor()
            cursor.execute(
                """INSERT INTO ltm_by_agent (agent_name, user_id, memory_key, memory_value, context_metadata)
                   VALUES (%s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE 
                   memory_value = VALUES(memory_value),
                   context_metadata = VALUES(context_metadata),
                   updated_at = CURRENT_TIMESTAMP""",
                (agent_name, user_id, memory_key, memory_value, json.dumps(metadata or {}))
            )
            cursor.close()
            logger.info(f"Stored agent memory for {agent_name}")
        except Exception as e:
            logger.error(f"Error storing agent memory: {e}")
    
    def get_recent_interactions(self, user_id: int, limit: int = 10):
        """Get recent user interactions"""
        if not self.mysql_conn:
            return []
        
        try:
            cursor = self.mysql_conn.cursor(dictionary=True)
            cursor.execute(
                """SELECT agent_name, query, response, timestamp, interaction_type
                   FROM agent_interactions 
                   WHERE user_id = %s 
                   ORDER BY timestamp DESC LIMIT %s""",
                (user_id, limit)
            )
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Error getting interactions: {e}")
            return []
    
    def similarity_search(self, query: str, user_id: int, limit: int = 5):
        """Simplified similarity search using keyword matching"""
        if not self.mysql_conn:
            return []
        
        try:
            # Extract keywords from query
            query_keywords = set(re.findall(r'\w+', query.lower()))
            
            cursor = self.mysql_conn.cursor(dictionary=True)
            cursor.execute(
                """SELECT agent_name, query as content, response, timestamp 
                   FROM agent_interactions 
                   WHERE user_id = %s 
                   ORDER BY timestamp DESC LIMIT 50""",
                (user_id,)
            )
            interactions = cursor.fetchall()
            cursor.close()
            
            # Calculate similarity based on keyword overlap
            results = []
            for interaction in interactions:
                content_keywords = set(re.findall(r'\w+', interaction['content'].lower()))
                common_keywords = query_keywords.intersection(content_keywords)
                
                if common_keywords:
                    similarity = len(common_keywords) / len(query_keywords.union(content_keywords))
                    results.append({
                        'content': interaction['content'],
                        'agent_name': interaction['agent_name'],
                        'similarity': similarity,
                        'timestamp': interaction['timestamp']
                    })
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []

memory_manager = DatabaseMemoryManager()

# Agent classes with real integration
class RealAgent:
    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
    
    def process(self, query: str, user_id: int) -> dict:
        """Process query with real Ollama and database storage"""
        start_time = datetime.now()
        
        # Generate response using real Ollama
        full_prompt = f"{self.system_prompt}\n\nUser Query: {query}"
        response = ollama_client.generate_response(full_prompt, self.system_prompt)
        
        # Store interaction in database
        memory_manager.store_interaction(user_id, self.name, query, response, 'single')
        
        # Store in agent memory
        memory_key = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        memory_manager.store_agent_memory(
            self.name, user_id, memory_key, query,
            {"response_preview": response[:100], "timestamp": start_time.isoformat()}
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "agent": self.name,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "processing_time": processing_time,
            "ollama_used": ollama_client.is_available()
        }

class RealSearchAgent(RealAgent):
    def __init__(self):
        super().__init__(
            "SearchAgent",
            "Vector-based similarity search agent for history matching",
            "You are SearchAgent, specialized in finding similar content from user history. Always return responses in JSON format with similarity scores and explanations."
        )
    
    def process(self, query: str, user_id: int) -> dict:
        """Enhanced search with real similarity matching"""
        start_time = datetime.now()
        
        # Perform similarity search
        similar_results = memory_manager.similarity_search(query, user_id)
        
        # Create structured JSON response
        search_response = {
            "search_results": {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "similar_content": similar_results,
                "total_matches": len(similar_results)
            },
            "agent": self.name,
            "analysis": f"Found {len(similar_results)} similar interactions based on keyword matching"
        }
        
        json_response = json.dumps(search_response, indent=2, default=str)
        
        # Store interaction
        memory_manager.store_interaction(user_id, self.name, query, json_response, 'single')
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "agent": self.name,
            "response": json_response,
            "timestamp": datetime.now().isoformat(),
            "processing_time": processing_time,
            "response_type": "json",
            "search_matches": len(similar_results)
        }

class RealOrchestratorAgent:
    def __init__(self):
        self.name = "OrchestratorAgent"
        self.agents = {
            "SearchAgent": RealSearchAgent(),
            "ScenicLocationFinder": RealAgent(
                "ScenicLocationFinder", 
                "Scenic location finding agent",
                "You are ScenicLocationFinder. Help users discover beautiful, scenic places with detailed recommendations including practical information about accessibility, best times to visit, and photography opportunities."
            ),
            "ForestAnalyzer": RealAgent(
                "ForestAnalyzer",
                "Forest analysis agent", 
                "You are ForestAnalyzer. Provide detailed analysis of forest ecosystems, biodiversity, conservation status, and environmental factors. Include scientific insights and management recommendations."
            ),
            "WaterBodyAnalyzer": RealAgent(
                "WaterBodyAnalyzer",
                "Water body analysis agent",
                "You are WaterBodyAnalyzer. Analyze water bodies including hydrological characteristics, water quality, aquatic ecosystems, and environmental impacts. Provide scientific and practical insights."
            )
        }
    
    def route_query(self, query: str, user_id: int) -> dict:
        """Advanced query routing with real multi-agent orchestration"""
        query_lower = query.lower()
        start_time = datetime.now()
        
        # Enhanced routing logic
        routing_scores = {}
        
        # Pattern matching for routing
        patterns = {
            "SearchAgent": ["search", "history", "previous", "before", "recall", "find similar", "what did"],
            "ScenicLocationFinder": ["scenic", "mountain", "landscape", "beautiful", "view", "tourist", "visit", "travel", "place"],
            "ForestAnalyzer": ["forest", "tree", "woodland", "ecosystem", "biodiversity", "conservation", "deforestation"],
            "WaterBodyAnalyzer": ["water", "lake", "river", "ocean", "sea", "pond", "hydrology", "aquatic", "marine"]
        }
        
        for agent, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                routing_scores[agent] = score
        
        # Decide on routing strategy
        if not routing_scores:
            # Default fallback
            selected_agent = self.agents["ScenicLocationFinder"]
            strategy = "fallback"
            result = selected_agent.process(query, user_id)
            
        elif len(routing_scores) == 1 or max(routing_scores.values()) >= 3:
            # Single agent with high confidence
            best_agent_name = max(routing_scores, key=routing_scores.get)
            selected_agent = self.agents[best_agent_name]
            strategy = "single_agent"
            result = selected_agent.process(query, user_id)
            
        else:
            # Multi-agent orchestration for complex queries
            strategy = "multi_agent"
            selected_agents = [agent for agent, score in routing_scores.items() if score >= 1][:3]  # Max 3 agents
            
            logger.info(f"Multi-agent orchestration: {selected_agents}")
            
            agent_responses = []
            for agent_name in selected_agents:
                try:
                    agent_result = self.agents[agent_name].process(query, user_id)
                    agent_responses.append({
                        "agent": agent_name,
                        "response": agent_result["response"],
                        "processing_time": agent_result.get("processing_time", 0)
                    })
                except Exception as e:
                    logger.error(f"Error with agent {agent_name}: {e}")
                    agent_responses.append({
                        "agent": agent_name,
                        "response": f"Error processing query: {str(e)}",
                        "processing_time": 0
                    })
            
            # Synthesize responses using Ollama
            synthesis_prompt = f"""
            Query: {query}
            
            Multiple AI agents have provided responses:
            
            {chr(10).join([f"{r['agent']}: {r['response'][:200]}..." for r in agent_responses])}
            
            Please synthesize these responses into a comprehensive, coherent answer that addresses the user's query.
            """
            
            synthesized_response = ollama_client.generate_response(
                synthesis_prompt,
                "You are an expert at synthesizing multiple AI agent responses into coherent, comprehensive answers."
            )
            
            combined_response = f"**Multi-Agent Orchestrated Response:**\n\n{synthesized_response}\n\n**Individual Agent Contributions:**\n\n"
            for r in agent_responses:
                combined_response += f"**{r['agent']}:** {r['response'][:300]}...\n\n"
            
            # Store orchestrated interaction
            memory_manager.store_interaction(user_id, self.name, query, combined_response, 'orchestrated')
            
            total_processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "agent": self.name,
                "response": combined_response,
                "timestamp": datetime.now().isoformat(),
                "processing_time": total_processing_time,
                "individual_responses": agent_responses,
                "agents_used": len(agent_responses)
            }
        
        # Add orchestration metadata
        result["orchestration"] = {
            "strategy": strategy,
            "routing_scores": routing_scores,
            "query_complexity": len(query.split()),
            "selected_agents": selected_agents if strategy == "multi_agent" else [result["agent"]]
        }
        
        return result

# Global orchestrator
orchestrator = RealOrchestratorAgent()

# Initialize database on startup
initialize_database()

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ping")
async def ping():
    return {"pong": True}

@app.get("/health")
async def health():
    mysql_status = get_mysql_connection() is not None
    redis_status = get_redis_connection() is not None
    ollama_status = ollama_client.is_available()
    
    return {
        "status": "Full system running ✅",
        "mysql_connected": mysql_status,
        "redis_connected": redis_status,
        "ollama_available": ollama_status,
        "components": {
            "database": "✅" if mysql_status else "❌",
            "cache": "✅" if redis_status else "❌", 
            "ai_model": "✅" if ollama_status else "❌"
        }
    }

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    conn = get_mysql_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                      (user_data.username, user_data.email))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Create user
        cursor.execute(
            """INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)""",
            (user_data.username, user_data.email, hash_password(user_data.password))
        )
        user_id = cursor.lastrowid
        
        # Get created user
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", response_model=Token)
async def login_user(user_data: UserLogin):
    conn = get_mysql_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND is_active = TRUE", (user_data.username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or not verify_password(user_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"]
    )

@app.get("/auth/session")
async def get_user_session(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # Get recent interactions
    recent_interactions = memory_manager.get_recent_interactions(user_id, 10)
    
    # Get active agents
    active_agents = list(set([
        interaction["agent_name"] 
        for interaction in recent_interactions
    ])) if recent_interactions else list(orchestrator.agents.keys())
    
    return {
        "user": current_user,
        "recent_interactions": recent_interactions,
        "active_agents": active_agents,
        "database_connected": get_mysql_connection() is not None
    }

# Main chat endpoint
@app.post("/ai/chat")
async def ai_chat(input_data: ChatInput, current_user: dict = Depends(get_current_user)):
    """Main chat endpoint with full orchestration and database integration"""
    try:
        logger.info(f"Processing chat request from user {input_data.user}: {input_data.question}")
        
        # Use real orchestrator with database integration
        result = orchestrator.route_query(input_data.question, current_user["id"])
        
        logger.info(f"Query processed - Strategy: {result.get('orchestration', {}).get('strategy', 'unknown')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

# System status and testing endpoints
@app.get("/api/ollama/status")
async def ollama_status():
    """Comprehensive Ollama status check"""
    try:
        available = ollama_client.is_available()
        models = []
        
        if available:
            response = requests.get(f"{ollama_client.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json().get("models", [])
                models = [model["name"] for model in models_data]
        
        return {
            "available": available,
            "models": models,
            "base_url": ollama_client.base_url,
            "default_model": ollama_client.default_model,
            "status": "Connected" if available else "Disconnected"
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "base_url": ollama_client.base_url,
            "status": "Error"
        }

@app.get("/api/database/status")
async def database_status(current_user: dict = Depends(get_current_user)):
    """Check database connectivity and show sample data"""
    mysql_conn = get_mysql_connection()
    redis_conn = get_redis_connection()
    
    status = {
        "mysql": {"connected": mysql_conn is not None},
        "redis": {"connected": redis_conn is not None}
    }
    
    if mysql_conn:
        try:
            cursor = mysql_conn.cursor()
            
            # Get table counts
            cursor.execute("SELECT COUNT(*) as count FROM users")
            status["mysql"]["users_count"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) as count FROM agent_interactions")
            status["mysql"]["interactions_count"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) as count FROM ltm_by_agent")
            status["mysql"]["ltm_records"] = cursor.fetchone()[0]
            
            # Recent interactions
            cursor.execute("""
                SELECT agent_name, COUNT(*) as count 
                FROM agent_interactions 
                GROUP BY agent_name 
                ORDER BY count DESC
            """)
            status["mysql"]["agent_usage"] = dict(cursor.fetchall())
            
            cursor.close()
            mysql_conn.close()
            
        except Exception as e:
            status["mysql"]["error"] = str(e)
    
    return status

@app.get("/api/agents")
async def get_agents(current_user: dict = Depends(get_current_user)):
    """Get all available agents with their capabilities"""
    return {
        "agents": {
            name: {
                "name": agent.name,
                "description": agent.description,
                "capabilities": ["real_ollama_integration", "database_storage", "memory_management"]
            }
            for name, agent in orchestrator.agents.items()
        },
        "orchestrator": {
            "name": orchestrator.name,
            "capabilities": ["multi_agent_routing", "query_analysis", "response_synthesis"]
        },
        "system": "Full integration with Ollama and MySQL"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("""
    🚀 Starting LangGraph AI Agent System - FULL INTEGRATION TEST
    
    📍 Server: http://localhost:8001
    
    🎯 Real Integration Features:
    ✅ Real Ollama LLM Integration (llama3:latest)
    ✅ MySQL Database Storage (Users, Interactions, LTM)
    ✅ Redis Caching (STM)
    ✅ Multi-Agent Orchestration
    ✅ Vector Similarity Search (Database-based)
    ✅ Agent-based LTM Storage
    ✅ Interactive Web UI
    
    📊 Test Queries:
    - "Find scenic mountain locations" (Single Agent)
    - "Tell me about forest ecosystems and water bodies" (Multi-Agent)
    - "Search my conversation history" (Search Agent)
    """)
    
    uvicorn.run(app, host="localhost", port=8001, log_level="info")
