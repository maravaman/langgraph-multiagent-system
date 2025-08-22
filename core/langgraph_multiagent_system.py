"""
LangGraph Multiagent System
Advanced multiagent architecture with conditional routing, state management, and agent communication
Includes Weather Agent and Dining Agent for comprehensive functionality
"""

import json
import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated, Literal
from datetime import datetime
from pathlib import Path
import operator

from langgraph.graph import StateGraph, END
from core.memory import MemoryManager
from core.ollama_client import ollama_client, prompt_manager

logger = logging.getLogger(__name__)

# Enhanced GraphState for multiagent communication
class MultiAgentState(TypedDict, total=False):
    """Enhanced state for multiagent LangGraph system"""
    user: str
    user_id: int
    question: str
    
    # Agent routing and communication
    current_agent: str
    next_agent: Optional[str]
    agent_chain: List[str]
    routing_decision: str
    
    # Responses and data
    response: str
    agent_responses: Dict[str, str]
    final_response: str
    
    # Context and memory
    context: Dict[str, Any]
    memory: Dict[str, Any]
    shared_data: Dict[str, Any]
    
    # Execution tracking
    edges_traversed: List[str]
    execution_path: List[Dict[str, Any]]
    timestamp: str
    
    # Agent-specific data
    weather_data: Optional[Dict[str, Any]]
    dining_data: Optional[Dict[str, Any]]
    location_data: Optional[Dict[str, Any]]
    forest_data: Optional[Dict[str, Any]]
    search_results: Optional[Dict[str, Any]]

class LangGraphMultiAgentSystem:
    """
    Advanced LangGraph Multiagent System
    Features:
    - Conditional agent routing based on query analysis
    - State management between agents
    - Memory integration (Redis STM + MySQL LTM)
    - Agent communication and data sharing
    - Dynamic execution paths
    """
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.agents_config = {}
        self.routing_rules = {}
        self.agent_capabilities = {}
        self.graph = None
        
        # Load configuration and initialize system
        self.load_agent_configuration()
        self.setup_routing_rules()
        
    def load_agent_configuration(self):
        """Load and expand agent configuration with Weather and Dining agents"""
        base_config = {
            "entry_point": "RouterAgent",
            "version": "2.0.0",
            "description": "LangGraph Multiagent System with Weather and Dining Agents",
            "agents": [
                {
                    "id": "RouterAgent",
                    "name": "Query Router Agent",
                    "description": "Routes queries to appropriate specialized agents",
                    "capabilities": ["query_analysis", "routing", "orchestration"],
                    "keywords": ["route", "analyze", "direct"],
                    "priority": 1
                },
                {
                    "id": "WeatherAgent",
                    "name": "Weather Analysis Agent", 
                    "description": "Provides weather information, forecasts, and climate analysis",
                    "capabilities": ["weather_forecast", "climate_analysis", "meteorology", "weather_planning"],
                    "keywords": ["weather", "temperature", "rain", "sun", "climate", "forecast", "humidity", "wind", "storm", "snow"],
                    "priority": 2
                },
                {
                    "id": "DiningAgent",
                    "name": "Dining and Restaurant Agent",
                    "description": "Recommends restaurants, cuisines, and dining experiences",
                    "capabilities": ["restaurant_recommendations", "cuisine_analysis", "dining_planning", "food_culture"],
                    "keywords": ["restaurant", "food", "cuisine", "dining", "eat", "meal", "chef", "menu", "cooking", "recipe"],
                    "priority": 2
                },
                {
                    "id": "ScenicLocationFinderAgent",
                    "name": "Scenic Location Finder Agent",
                    "description": "Specialized agent for finding beautiful scenic locations",
                    "capabilities": ["location_search", "tourism_advice", "geographical_analysis", "photography_spots"],
                    "keywords": ["scenic", "beautiful", "location", "tourist", "destination", "view", "landscape", "mountain"],
                    "priority": 2
                },
                {
                    "id": "ForestAnalyzerAgent",
                    "name": "Forest Ecosystem Analyzer Agent", 
                    "description": "Specializes in forest ecology and conservation",
                    "capabilities": ["forest_ecology", "biodiversity", "conservation", "wildlife_analysis"],
                    "keywords": ["forest", "tree", "wildlife", "ecosystem", "conservation", "nature", "biodiversity"],
                    "priority": 3
                },
                {
                    "id": "SearchAgent",
                    "name": "Memory Search Agent",
                    "description": "Performs similarity search in user history",
                    "capabilities": ["memory_search", "similarity_matching", "history_analysis", "pattern_recognition"],
                    "keywords": ["search", "history", "remember", "previous", "similar", "past", "recall"],
                    "priority": 4
                }
            ]
        }
        
        self.agents_config = {agent['id']: agent for agent in base_config['agents']}
        self.entry_point = base_config['entry_point']
        
        # Build agent capabilities map
        for agent_id, config in self.agents_config.items():
            self.agent_capabilities[agent_id] = {
                'capabilities': config.get('capabilities', []),
                'keywords': config.get('keywords', []),
                'description': config.get('description', ''),
                'priority': config.get('priority', 5)
            }
        
        logger.info(f"✅ Loaded {len(self.agents_config)} agents including Weather and Dining agents")
        
    def setup_routing_rules(self):
        """Setup intelligent routing rules for agent communication"""
        self.routing_rules = {
            "RouterAgent": {
                "weather_query": ["WeatherAgent"],
                "dining_query": ["DiningAgent"], 
                "location_query": ["ScenicLocationFinderAgent"],
                "forest_query": ["ForestAnalyzerAgent"],
                "search_query": ["SearchAgent"],
                "complex_travel": ["WeatherAgent", "DiningAgent", "ScenicLocationFinderAgent"],
                "nature_exploration": ["ForestAnalyzerAgent", "WeatherAgent", "ScenicLocationFinderAgent"],
                "default": ["ScenicLocationFinderAgent"]
            },
            "WeatherAgent": {
                "needs_location": ["ScenicLocationFinderAgent"],
                "needs_dining": ["DiningAgent"],
                "end": []
            },
            "DiningAgent": {
                "needs_weather": ["WeatherAgent"],
                "needs_location": ["ScenicLocationFinderAgent"], 
                "end": []
            },
            "ScenicLocationFinderAgent": {
                "needs_weather": ["WeatherAgent"],
                "needs_dining": ["DiningAgent"],
                "needs_forest_info": ["ForestAnalyzerAgent"],
                "end": []
            },
            "ForestAnalyzerAgent": {
                "needs_location": ["ScenicLocationFinderAgent"],
                "needs_weather": ["WeatherAgent"],
                "end": []
            },
            "SearchAgent": {
                "end": []
            }
        }
        
    def build_langgraph(self) -> StateGraph:
        """Build the complete LangGraph with all agent nodes and conditional edges"""
        builder = StateGraph(MultiAgentState)
        
        # Add all agent nodes
        builder.add_node("RouterAgent", self._router_agent_node)
        builder.add_node("WeatherAgent", self._weather_agent_node)
        builder.add_node("DiningAgent", self._dining_agent_node)
        builder.add_node("ScenicLocationFinderAgent", self._scenic_agent_node)
        builder.add_node("ForestAnalyzerAgent", self._forest_agent_node)
        builder.add_node("SearchAgent", self._search_agent_node)
        builder.add_node("ResponseSynthesizer", self._response_synthesizer_node)
        
        # Set entry point
        builder.set_entry_point("RouterAgent")
        
        # Add conditional edges from RouterAgent
        builder.add_conditional_edges(
            "RouterAgent",
            self._route_from_router,
            {
                "weather": "WeatherAgent",
                "dining": "DiningAgent",
                "location": "ScenicLocationFinderAgent", 
                "forest": "ForestAnalyzerAgent",
                "search": "SearchAgent",
                "synthesize": "ResponseSynthesizer"
            }
        )
        
        # Add conditional edges from each agent
        for agent_id in ["WeatherAgent", "DiningAgent", "ScenicLocationFinderAgent", "ForestAnalyzerAgent", "SearchAgent"]:
            builder.add_conditional_edges(
                agent_id,
                self._route_to_next_agent,
                {
                    "weather": "WeatherAgent",
                    "dining": "DiningAgent", 
                    "location": "ScenicLocationFinderAgent",
                    "forest": "ForestAnalyzerAgent",
                    "search": "SearchAgent",
                    "synthesize": "ResponseSynthesizer",
                    "end": END
                }
            )
        
        # ResponseSynthesizer always ends
        builder.add_edge("ResponseSynthesizer", END)
        
        return builder.compile()
    
    def _router_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Router agent analyzes query and determines execution path"""
        question = state.get("question", "")
        
        # Analyze query to determine routing
        routing_decision = self._analyze_query_for_routing(question)
        
        # Update state
        updated_state = state.copy()
        updated_state["current_agent"] = "RouterAgent"
        updated_state["routing_decision"] = routing_decision
        updated_state["agent_chain"] = [routing_decision] if routing_decision != "synthesize" else []
        updated_state["edges_traversed"] = state.get("edges_traversed", []) + ["RouterAgent"]
        
        # Add execution path entry
        execution_path = state.get("execution_path", [])
        execution_path.append({
            "agent": "RouterAgent",
            "action": f"Routed query to {routing_decision}",
            "timestamp": datetime.now().isoformat()
        })
        updated_state["execution_path"] = execution_path
        
        logger.info(f"Router decided: {routing_decision} for query: {question[:50]}...")
        return updated_state
    
    def _weather_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Weather agent provides weather information and forecasts"""
        try:
            question = state.get("question", "")
            user_id = state.get("user_id", 0)
            
            if not question:
                logger.warning("Empty question in weather agent")
                question = "General weather inquiry"
            
            # Build context for weather analysis with null safety
            context = self._build_context_string(state.get("context", {}))
            location_data = state.get("location_data", {})
            
            # Enhance question with location context if available
            enhanced_question = question
            if location_data and isinstance(location_data, dict):
                location = location_data.get('location', 'unknown')
                enhanced_question = f"{question} (considering location: {location})"
            
            # Generate weather response with comprehensive error handling
            response = None
            try:
                prompt_data = prompt_manager.get_prompt("WeatherAgent", enhanced_question, context)
                if not prompt_data or not isinstance(prompt_data, dict):
                    logger.warning("Invalid prompt data from prompt manager")
                    raise Exception("Invalid prompt data")
                
                if "prompt" not in prompt_data or "system" not in prompt_data:
                    logger.warning("Missing prompt or system key in prompt data")
                    raise Exception("Incomplete prompt data")
                    
                response = ollama_client.generate_response(
                    prompt=prompt_data["prompt"],
                    system_prompt=prompt_data["system"]
                )
            except Exception as prompt_error:
                logger.error(f"Weather agent prompt generation error: {prompt_error}")
                # Fallback to direct response with safe system prompt
                try:
                    response = ollama_client.generate_response(
                        prompt=f"Weather Query: {enhanced_question}\n\nContext: {context}\n\nPlease provide weather information.",
                        system_prompt=self._get_weather_system_prompt()
                    )
                except Exception as fallback_error:
                    logger.error(f"Weather agent fallback failed: {fallback_error}")
                    response = f"Weather information is currently unavailable due to technical issues. Query was: {enhanced_question}"
            
            # Ensure response is valid
            if not response or not isinstance(response, str):
                response = f"Weather agent processed query: {enhanced_question}, but no response was generated."
            
            # Store weather data for other agents
            weather_data = {
                "forecast": response,
                "location": location_data.get("location", "") if isinstance(location_data, dict) else "",
                "analysis_time": datetime.now().isoformat()
            }
            
            # Update state
            updated_state = state.copy()
            updated_state["current_agent"] = "WeatherAgent"
            updated_state["weather_data"] = weather_data
            
            # Update agent responses
            agent_responses = state.get("agent_responses", {})
            agent_responses["WeatherAgent"] = response
            updated_state["agent_responses"] = agent_responses
            
            # Update execution path
            execution_path = state.get("execution_path", [])
            execution_path.append({
                "agent": "WeatherAgent", 
                "action": "Provided weather analysis",
                "timestamp": datetime.now().isoformat()
            })
            updated_state["execution_path"] = execution_path
            
            # Store in memory
            self._store_agent_interaction(user_id, "WeatherAgent", question, response)
            
            logger.info("Weather agent completed analysis")
            return updated_state
            
        except Exception as e:
            logger.error(f"Weather agent error: {e}")
            updated_state = state.copy()
            updated_state["current_agent"] = "WeatherAgent"
            updated_state["agent_responses"] = state.get("agent_responses", {})
            updated_state["agent_responses"]["WeatherAgent"] = f"Weather information currently unavailable: {str(e)}"
            return updated_state
    
    def _dining_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Dining agent provides restaurant and cuisine recommendations"""
        try:
            question = state.get("question", "")
            user_id = state.get("user_id", 0)
            
            if not question:
                logger.warning("Empty question in dining agent")
                question = "General dining inquiry"
            
            # Build context for dining recommendations with null safety
            context = self._build_context_string(state.get("context", {}))
            location_data = state.get("location_data", {})
            weather_data = state.get("weather_data", {})
            
            # Enhance question with available context
            enhanced_question = question
            context_parts = []
            
            if location_data and isinstance(location_data, dict):
                location = location_data.get('location', 'unknown')
                context_parts.append(f"Location: {location}")
            if weather_data and isinstance(weather_data, dict):
                forecast = weather_data.get('forecast', 'unknown')
                if forecast and len(str(forecast)) > 100:
                    forecast = str(forecast)[:100] + "..."
                context_parts.append(f"Weather: {forecast}")
                
            if context_parts:
                enhanced_question = f"{question} (Context: {'; '.join(context_parts)})"
            
            # Generate dining response with comprehensive error handling
            response = None
            try:
                prompt_data = prompt_manager.get_prompt("DiningAgent", enhanced_question, context)
                if not prompt_data or not isinstance(prompt_data, dict):
                    logger.warning("Invalid prompt data from prompt manager")
                    raise Exception("Invalid prompt data")
                
                if "prompt" not in prompt_data or "system" not in prompt_data:
                    logger.warning("Missing prompt or system key in prompt data")
                    raise Exception("Incomplete prompt data")
                    
                response = ollama_client.generate_response(
                    prompt=prompt_data["prompt"],
                    system_prompt=prompt_data["system"]
                )
            except Exception as prompt_error:
                logger.error(f"Dining agent prompt generation error: {prompt_error}")
                # Fallback to direct response with safe system prompt
                try:
                    response = ollama_client.generate_response(
                        prompt=f"Dining Query: {enhanced_question}\n\nContext: {context}\n\nPlease provide dining recommendations.",
                        system_prompt=self._get_dining_system_prompt()
                    )
                except Exception as fallback_error:
                    logger.error(f"Dining agent fallback failed: {fallback_error}")
                    response = f"Dining recommendations are currently unavailable due to technical issues. Query was: {enhanced_question}"
            
            # Ensure response is valid
            if not response or not isinstance(response, str):
                response = f"Dining agent processed query: {enhanced_question}, but no response was generated."
            
            # Store dining data for other agents
            dining_data = {
                "recommendations": response,
                "location": location_data.get("location", ""),
                "weather_considered": bool(weather_data),
                "analysis_time": datetime.now().isoformat()
            }
            
            # Update state
            updated_state = state.copy()
            updated_state["current_agent"] = "DiningAgent"
            updated_state["dining_data"] = dining_data
            
            # Update agent responses
            agent_responses = state.get("agent_responses", {})
            agent_responses["DiningAgent"] = response
            updated_state["agent_responses"] = agent_responses
            
            # Update execution path
            execution_path = state.get("execution_path", [])
            execution_path.append({
                "agent": "DiningAgent",
                "action": "Provided dining recommendations", 
                "timestamp": datetime.now().isoformat()
            })
            updated_state["execution_path"] = execution_path
            
            # Store in memory
            self._store_agent_interaction(user_id, "DiningAgent", question, response)
            
            logger.info("Dining agent completed recommendations")
            return updated_state
            
        except Exception as e:
            logger.error(f"Dining agent error: {e}")
            updated_state = state.copy()
            updated_state["current_agent"] = "DiningAgent"
            updated_state["agent_responses"] = state.get("agent_responses", {})
            updated_state["agent_responses"]["DiningAgent"] = f"Dining recommendations currently unavailable: {str(e)}"
            return updated_state
    
    def _scenic_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Scenic location finder agent with enhanced context awareness"""
        try:
            question = state.get("question", "")
            user_id = state.get("user_id", 0)
            
            if not question:
                logger.warning("Empty question in scenic location agent")
                question = "General location inquiry"
            
            # Build context with null safety
            context = self._build_context_string(state.get("context", {}))
            weather_data = state.get("weather_data", {})
            dining_data = state.get("dining_data", {})
            
            # Enhance question with weather and dining context
            enhanced_question = question
            context_parts = []
            
            if weather_data and isinstance(weather_data, dict):
                forecast = weather_data.get('forecast', 'unknown')
                if forecast and len(str(forecast)) > 100:
                    forecast = str(forecast)[:100] + "..."
                context_parts.append(f"Weather: {forecast}")
            if dining_data and isinstance(dining_data, dict):
                recommendations = dining_data.get('recommendations', 'unknown')
                if recommendations and len(str(recommendations)) > 100:
                    recommendations = str(recommendations)[:100] + "..."
                context_parts.append(f"Dining: {recommendations}")
                
            if context_parts:
                enhanced_question = f"{question} (Context: {'; '.join(context_parts)})"
            
            # Generate scenic location response with comprehensive error handling
            response = None
            try:
                prompt_data = prompt_manager.get_prompt("ScenicLocationFinder", enhanced_question, context)
                if not prompt_data or not isinstance(prompt_data, dict):
                    logger.warning("Invalid prompt data from prompt manager")
                    raise Exception("Invalid prompt data")
                
                if "prompt" not in prompt_data or "system" not in prompt_data:
                    logger.warning("Missing prompt or system key in prompt data")
                    raise Exception("Incomplete prompt data")
                    
                response = ollama_client.generate_response(
                    prompt=prompt_data["prompt"],
                    system_prompt=prompt_data["system"]
                )
            except Exception as prompt_error:
                logger.error(f"Scenic agent prompt generation error: {prompt_error}")
                # Fallback to direct response with safe system prompt
                try:
                    response = ollama_client.generate_response(
                        prompt=f"Location Query: {enhanced_question}\n\nContext: {context}\n\nPlease provide scenic location recommendations.",
                        system_prompt=self._get_scenic_system_prompt()
                    )
                except Exception as fallback_error:
                    logger.error(f"Scenic agent fallback failed: {fallback_error}")
                    response = f"Scenic location recommendations are currently unavailable due to technical issues. Query was: {enhanced_question}"
            
            # Ensure response is valid
            if not response or not isinstance(response, str):
                response = f"Scenic location agent processed query: {enhanced_question}, but no response was generated."
            
            # Store location data for other agents
            location_result_data = {
                "recommendations": response,
                "weather_integrated": bool(weather_data),
                "dining_integrated": bool(dining_data),
                "analysis_time": datetime.now().isoformat()
            }
            
            # Update state
            updated_state = state.copy()
            updated_state["current_agent"] = "ScenicLocationFinderAgent"
            updated_state["location_data"] = location_result_data
            
            # Update agent responses
            agent_responses = state.get("agent_responses", {})
            agent_responses["ScenicLocationFinderAgent"] = response
            updated_state["agent_responses"] = agent_responses
            
            # Update execution path
            execution_path = state.get("execution_path", [])
            execution_path.append({
                "agent": "ScenicLocationFinderAgent",
                "action": "Provided location recommendations",
                "timestamp": datetime.now().isoformat()
            })
            updated_state["execution_path"] = execution_path
            
            # Store in memory
            self._store_agent_interaction(user_id, "ScenicLocationFinderAgent", question, response)
            
            logger.info("Scenic location agent completed analysis")
            return updated_state
            
        except Exception as e:
            logger.error(f"Scenic location agent error: {e}")
            updated_state = state.copy()
            updated_state["current_agent"] = "ScenicLocationFinderAgent" 
            updated_state["agent_responses"] = state.get("agent_responses", {})
            updated_state["agent_responses"]["ScenicLocationFinderAgent"] = f"Location recommendations currently unavailable: {str(e)}"
            return updated_state
    
    def _forest_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Forest analyzer agent with enhanced context"""
        try:
            question = state.get("question", "")
            user_id = state.get("user_id", 0)
            
            if not question:
                logger.warning("Empty question in forest agent")
                question = "General forest inquiry"
            
            # Build context with null safety
            context = self._build_context_string(state.get("context", {}))
            location_data = state.get("location_data", {})
            weather_data = state.get("weather_data", {})
            
            # Enhance with available context
            enhanced_question = question
            context_parts = []
            
            if location_data and isinstance(location_data, dict):
                recommendations = location_data.get('recommendations', 'unknown')
                if recommendations and len(str(recommendations)) > 100:
                    recommendations = str(recommendations)[:100] + "..."
                context_parts.append(f"Location: {recommendations}")
            if weather_data and isinstance(weather_data, dict):
                forecast = weather_data.get('forecast', 'unknown')
                if forecast and len(str(forecast)) > 100:
                    forecast = str(forecast)[:100] + "..."
                context_parts.append(f"Weather: {forecast}")
                
            if context_parts:
                enhanced_question = f"{question} (Context: {'; '.join(context_parts)})"
            
            # Generate forest analysis response with comprehensive error handling
            response = None
            try:
                prompt_data = prompt_manager.get_prompt("ForestAnalyzer", enhanced_question, context)
                if not prompt_data or not isinstance(prompt_data, dict):
                    logger.warning("Invalid prompt data from prompt manager")
                    raise Exception("Invalid prompt data")
                
                if "prompt" not in prompt_data or "system" not in prompt_data:
                    logger.warning("Missing prompt or system key in prompt data")
                    raise Exception("Incomplete prompt data")
                    
                response = ollama_client.generate_response(
                    prompt=prompt_data["prompt"],
                    system_prompt=prompt_data["system"]
                )
            except Exception as prompt_error:
                logger.error(f"Forest agent prompt generation error: {prompt_error}")
                # Fallback to direct response with safe system prompt
                try:
                    response = ollama_client.generate_response(
                        prompt=f"Forest Query: {enhanced_question}\n\nContext: {context}\n\nPlease provide forest ecosystem analysis.",
                        system_prompt=self._get_forest_system_prompt()
                    )
                except Exception as fallback_error:
                    logger.error(f"Forest agent fallback failed: {fallback_error}")
                    response = f"Forest analysis is currently unavailable due to technical issues. Query was: {enhanced_question}"
            
            # Ensure response is valid
            if not response or not isinstance(response, str):
                response = f"Forest agent processed query: {enhanced_question}, but no response was generated."
            
            # Store forest data
            forest_data = {
                "analysis": response,
                "location_considered": bool(location_data),
                "weather_considered": bool(weather_data),
                "analysis_time": datetime.now().isoformat()
            }
            
            # Update state
            updated_state = state.copy()
            updated_state["current_agent"] = "ForestAnalyzerAgent"
            updated_state["forest_data"] = forest_data
            
            # Update agent responses
            agent_responses = state.get("agent_responses", {})
            agent_responses["ForestAnalyzerAgent"] = response
            updated_state["agent_responses"] = agent_responses
            
            # Update execution path
            execution_path = state.get("execution_path", [])
            execution_path.append({
                "agent": "ForestAnalyzerAgent",
                "action": "Provided forest ecosystem analysis",
                "timestamp": datetime.now().isoformat()
            })
            updated_state["execution_path"] = execution_path
            
            # Store in memory
            self._store_agent_interaction(user_id, "ForestAnalyzerAgent", question, response)
            
            logger.info("Forest analyzer agent completed analysis")
            return updated_state
            
        except Exception as e:
            logger.error(f"Forest analyzer agent error: {e}")
            updated_state = state.copy()
            updated_state["current_agent"] = "ForestAnalyzerAgent"
            updated_state["agent_responses"] = state.get("agent_responses", {})
            updated_state["agent_responses"]["ForestAnalyzerAgent"] = f"Forest analysis currently unavailable: {str(e)}"
            return updated_state
    
    def _search_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Search agent for memory and history analysis"""
        try:
            question = state.get("question", "")
            user_id = state.get("user_id", 0)
            
            if not question:
                logger.warning("Empty question in search agent")
                question = "General search inquiry"
            
            # Perform memory search with error handling
            try:
                search_results = self._perform_memory_search(question, user_id)
            except Exception as search_error:
                logger.error(f"Memory search failed: {search_error}")
                search_results = {"query": question, "matches": [], "total_found": 0, "error": str(search_error)}
            
            # Build context with null safety
            context = self._build_context_string(state.get("context", {}))
            
            # Generate search response with comprehensive error handling
            response = None
            try:
                search_context = f"{context}\n\nSearch Results: {search_results}"
                prompt_data = prompt_manager.get_prompt("SearchAgent", question, search_context)
                if not prompt_data or not isinstance(prompt_data, dict):
                    logger.warning("Invalid prompt data from prompt manager")
                    raise Exception("Invalid prompt data")
                
                if "prompt" not in prompt_data or "system" not in prompt_data:
                    logger.warning("Missing prompt or system key in prompt data")
                    raise Exception("Incomplete prompt data")
                    
                response = ollama_client.generate_response(
                    prompt=prompt_data["prompt"],
                    system_prompt=prompt_data["system"]
                )
            except Exception as prompt_error:
                logger.error(f"Search agent prompt generation error: {prompt_error}")
                # Fallback to direct response with safe system prompt
                try:
                    search_context = f"{context}\n\nSearch Results: {search_results}"
                    response = ollama_client.generate_response(
                        prompt=f"Search Query: {question}\n\nContext: {search_context}\n\nPlease analyze the search results.",
                        system_prompt=self._get_search_system_prompt()
                    )
                except Exception as fallback_error:
                    logger.error(f"Search agent fallback failed: {fallback_error}")
                    response = f"Search analysis is currently unavailable due to technical issues. Query was: {question}"
            
            # Ensure response is valid
            if not response or not isinstance(response, str):
                response = f"Search agent processed query: {question}, but no response was generated."
            
            # Update state
            updated_state = state.copy()
            updated_state["current_agent"] = "SearchAgent"
            updated_state["search_results"] = search_results
            
            # Update agent responses
            agent_responses = state.get("agent_responses", {})
            agent_responses["SearchAgent"] = response
            updated_state["agent_responses"] = agent_responses
            
            # Update execution path
            execution_path = state.get("execution_path", [])
            execution_path.append({
                "agent": "SearchAgent",
                "action": "Performed memory search and analysis",
                "timestamp": datetime.now().isoformat()
            })
            updated_state["execution_path"] = execution_path
            
            # Store in memory
            self._store_agent_interaction(user_id, "SearchAgent", question, response)
            
            logger.info("Search agent completed analysis")
            return updated_state
            
        except Exception as e:
            logger.error(f"Search agent error: {e}")
            updated_state = state.copy()
            updated_state["current_agent"] = "SearchAgent"
            updated_state["agent_responses"] = state.get("agent_responses", {})
            updated_state["agent_responses"]["SearchAgent"] = f"Search analysis currently unavailable: {str(e)}"
            return updated_state
    
    def _response_synthesizer_node(self, state: MultiAgentState) -> MultiAgentState:
        """Synthesize responses from multiple agents into coherent final response"""
        agent_responses = state.get("agent_responses", {})
        
        if not agent_responses:
            updated_state = state.copy()
            updated_state["final_response"] = "No agent responses to synthesize."
            updated_state["response"] = "No agent responses to synthesize."
            return updated_state
        
        # Create comprehensive response
        response_parts = []
        response_parts.append("🤖 **Multiagent Analysis Results**\n")
        
        # Add each agent's contribution
        agent_order = ["WeatherAgent", "DiningAgent", "ScenicLocationFinderAgent", "ForestAnalyzerAgent", "SearchAgent"]
        
        for agent_id in agent_order:
            if agent_id in agent_responses:
                response = agent_responses[agent_id].strip()
                if response:
                    agent_name = agent_id.replace("Agent", "").replace("Finder", "")
                    response_parts.append(f"**{agent_name} Analysis:**")
                    response_parts.append(response)
                    response_parts.append("")  # Add spacing
        
        # Add execution summary
        execution_path = state.get("execution_path", [])
        if execution_path:
            response_parts.append("**Execution Path:**")
            for step in execution_path:
                response_parts.append(f"• {step['agent']}: {step['action']}")
        
        final_response = "\n".join(response_parts)
        
        # Update state
        updated_state = state.copy()
        updated_state["current_agent"] = "ResponseSynthesizer"
        updated_state["final_response"] = final_response
        updated_state["response"] = final_response
        
        # Update execution path
        execution_path = state.get("execution_path", [])
        execution_path.append({
            "agent": "ResponseSynthesizer",
            "action": f"Synthesized {len(agent_responses)} agent responses",
            "timestamp": datetime.now().isoformat()
        })
        updated_state["execution_path"] = execution_path
        
        logger.info(f"Response synthesizer combined {len(agent_responses)} agent responses")
        return updated_state
    
    def _analyze_query_for_routing(self, question: str) -> str:
        """Analyze query and determine initial routing decision"""
        question_lower = question.lower()
        
        # Weather-related queries
        weather_keywords = ["weather", "temperature", "rain", "sun", "climate", "forecast", "humidity", "wind", "storm", "snow"]
        if any(keyword in question_lower for keyword in weather_keywords):
            return "weather"
        
        # Dining-related queries  
        dining_keywords = ["restaurant", "food", "cuisine", "dining", "eat", "meal", "chef", "menu", "cooking", "recipe"]
        if any(keyword in question_lower for keyword in dining_keywords):
            return "dining"
        
        # Location-related queries
        location_keywords = ["scenic", "beautiful", "location", "tourist", "destination", "view", "landscape", "mountain"]
        if any(keyword in question_lower for keyword in location_keywords):
            return "location"
        
        # Forest-related queries
        forest_keywords = ["forest", "tree", "wildlife", "ecosystem", "conservation", "nature", "biodiversity"]
        if any(keyword in question_lower for keyword in forest_keywords):
            return "forest"
        
        # Search-related queries
        search_keywords = ["search", "history", "remember", "previous", "similar", "past", "recall"]
        if any(keyword in question_lower for keyword in search_keywords):
            return "search"
        
        # Complex travel queries that need multiple agents
        travel_keywords = ["travel", "trip", "vacation", "visit", "plan"]
        if any(keyword in question_lower for keyword in travel_keywords):
            return "location"  # Start with location, will route to others as needed
        
        # Default to synthesize if no specific routing
        return "location"
    
    def _route_from_router(self, state: MultiAgentState) -> str:
        """Route from RouterAgent to appropriate agent"""
        routing_decision = state.get("routing_decision", "location")
        return routing_decision
    
    def _route_to_next_agent(self, state: MultiAgentState) -> str:
        """Determine next agent or end execution"""
        current_agent = state.get("current_agent", "")
        question = state.get("question", "").lower()
        agent_responses = state.get("agent_responses", {})
        
        # Check if we need additional agents based on current response and query
        if current_agent == "WeatherAgent":
            # After weather, check if we need location or dining info
            if any(word in question for word in ["restaurant", "food", "dining", "eat"]):
                if "DiningAgent" not in agent_responses:
                    return "dining"
            if any(word in question for word in ["location", "place", "where", "scenic"]):
                if "ScenicLocationFinderAgent" not in agent_responses:
                    return "location"
        
        elif current_agent == "DiningAgent":
            # After dining, check if we need weather or location
            if any(word in question for word in ["weather", "climate", "temperature"]):
                if "WeatherAgent" not in agent_responses:
                    return "weather"
            if any(word in question for word in ["location", "place", "where", "scenic"]):
                if "ScenicLocationFinderAgent" not in agent_responses:
                    return "location"
        
        elif current_agent == "ScenicLocationFinderAgent":
            # After location, check if we need weather or dining
            if any(word in question for word in ["weather", "climate", "temperature"]):
                if "WeatherAgent" not in agent_responses:
                    return "weather" 
            if any(word in question for word in ["restaurant", "food", "dining"]):
                if "DiningAgent" not in agent_responses:
                    return "dining"
            if any(word in question for word in ["forest", "tree", "wildlife"]):
                if "ForestAnalyzerAgent" not in agent_responses:
                    return "forest"
        
        elif current_agent == "ForestAnalyzerAgent":
            # After forest analysis, check if we need location or weather
            if any(word in question for word in ["location", "where", "scenic"]):
                if "ScenicLocationFinderAgent" not in agent_responses:
                    return "location"
            if any(word in question for word in ["weather", "climate"]):
                if "WeatherAgent" not in agent_responses:
                    return "weather"
        
        # If we have multiple agent responses, synthesize them
        if len(agent_responses) > 1:
            return "synthesize"
        
        # If only one agent has responded and no additional routing needed, synthesize
        if len(agent_responses) >= 1:
            return "synthesize"
        
        # Default end
        return "end"
    
    def _build_context_string(self, context: Dict[str, Any]) -> str:
        """Build context string from memory and shared data with null safety"""
        try:
            # Handle None or invalid context
            if context is None or not isinstance(context, dict):
                return "No previous context available."
            
            context_parts = []
            
            # Add STM context with null safety
            stm_data = context.get("stm", {})
            if isinstance(stm_data, dict) and stm_data.get("recent_interactions"):
                recent_interactions = stm_data["recent_interactions"]
                if isinstance(recent_interactions, dict):
                    context_parts.append("Recent interactions:")
                    for agent_id, interaction in recent_interactions.items():
                        if agent_id and interaction:
                            context_parts.append(f"- {agent_id}: {interaction}")
            
            # Add LTM context with null safety
            ltm_data = context.get("ltm", {})
            if isinstance(ltm_data, dict) and ltm_data.get("recent_history"):
                recent_history = ltm_data["recent_history"]
                if isinstance(recent_history, list):
                    context_parts.append("\nRelevant history:")
                    for entry in recent_history[:3]:
                        if isinstance(entry, dict) and "value" in entry and entry["value"]:
                            context_parts.append(f"- {entry['value']}")
            
            return "\n".join(context_parts) if context_parts else "No previous context available."
            
        except Exception as e:
            logger.warning(f"Error building context string: {e}")
            return "No previous context available."
    
    def _perform_memory_search(self, query: str, user_id: int) -> Dict[str, Any]:
        """Perform memory search for SearchAgent"""
        try:
            # Get recent STM and LTM data
            stm_data = self.memory_manager.get_all_stm_for_user(str(user_id))
            ltm_data = self.memory_manager.get_recent_ltm(str(user_id), days=30)
            
            # Simple text matching
            query_lower = query.lower()
            matching_items = []
            
            # Search STM
            for agent_id, content in stm_data.items():
                if query_lower in str(content).lower():
                    matching_items.append({
                        "source": "stm",
                        "agent": agent_id,
                        "content": content,
                        "relevance": str(content).lower().count(query_lower)
                    })
            
            # Search LTM
            for entry in ltm_data:
                if isinstance(entry, dict) and "value" in entry:
                    content = entry["value"]
                    if query_lower in content.lower():
                        matching_items.append({
                            "source": "ltm",
                            "content": content,
                            "relevance": content.lower().count(query_lower),
                            "timestamp": entry.get("timestamp")
                        })
            
            # Sort by relevance
            matching_items.sort(key=lambda x: x.get("relevance", 0), reverse=True)
            
            return {
                "query": query,
                "matches": matching_items[:10],  # Top 10 matches
                "total_found": len(matching_items)
            }
            
        except Exception as e:
            logger.error(f"Memory search error: {e}")
            return {"query": query, "matches": [], "total_found": 0, "error": str(e)}
    
    def _store_agent_interaction(self, user_id: int, agent_id: str, question: str, response: str):
        """Store agent interaction in memory"""
        try:
            # Store in STM (temporary)
            self.memory_manager.set_stm(
                user_id=str(user_id),
                agent_id=agent_id,
                value=f"Q: {question}\nA: {response}",
                expiry=3600  # 1 hour
            )
            
            # Store in LTM (permanent)
            self.memory_manager.set_ltm(
                user_id=str(user_id),
                agent_id=agent_id,
                value=f"Query: {question}\nResponse: {response}"
            )
            
        except Exception as e:
            logger.error(f"Failed to store agent interaction: {e}")
    
    # System prompts for each agent
    def _get_weather_system_prompt(self) -> str:
        return """You are WeatherAgent, a specialized weather analysis assistant. Provide accurate, helpful weather information including:
        - Current conditions and forecasts
        - Climate analysis and seasonal patterns
        - Weather-related planning advice
        - Impact on outdoor activities
        Be practical and actionable in your responses."""
    
    def _get_dining_system_prompt(self) -> str:
        return """You are DiningAgent, a culinary and restaurant specialist. Provide excellent dining recommendations including:
        - Restaurant suggestions and cuisine types
        - Local food culture and specialties
        - Dining experiences and ambiance
        - Food and weather/location considerations
        Be descriptive and helpful for dining decisions."""
    
    def _get_scenic_system_prompt(self) -> str:
        return """You are ScenicLocationFinderAgent, specialized in beautiful destinations. Provide detailed location recommendations including:
        - Scenic spots and viewpoints
        - Photography opportunities
        - Access information and travel tips
        - Integration with weather and dining options
        Be inspiring and practical in your suggestions."""
    
    def _get_forest_system_prompt(self) -> str:
        return """You are ForestAnalyzerAgent, focused on forest ecosystems. Provide comprehensive forest analysis including:
        - Ecosystem characteristics and biodiversity
        - Conservation status and environmental factors
        - Wildlife and flora information
        - Integration with location and weather data
        Be scientific yet accessible in your explanations."""
    
    def _get_search_system_prompt(self) -> str:
        return """You are SearchAgent, specialized in memory and history analysis. Provide insightful search results including:
        - Pattern recognition in user history
        - Relevant past interactions and context
        - Similarity analysis and connections
        - Historical insights for current queries
        Be analytical and helpful in connecting past and present."""
    
    def process_request(self, user: str, user_id: int, question: str) -> Dict[str, Any]:
        """Main processing function for the multiagent system"""
        try:
            # Build graph if not built
            if not self.graph:
                self.graph = self.build_langgraph()
            
            # Get memory context
            stm_context = self._get_stm_context(user_id)
            ltm_context = self._get_ltm_context(user_id)
            
            # Initialize state
            initial_state = MultiAgentState(
                user=user,
                user_id=user_id,
                question=question,
                current_agent="",
                next_agent=None,
                agent_chain=[],
                routing_decision="",
                response="",
                agent_responses={},
                final_response="",
                context={
                    "stm": stm_context,
                    "ltm": ltm_context
                },
                memory={
                    "interactions": [],
                    "agent_data": {}
                },
                shared_data={},
                edges_traversed=[],
                execution_path=[],
                timestamp=datetime.now().isoformat(),
                weather_data=None,
                dining_data=None,
                location_data=None,
                forest_data=None,
                search_results=None
            )
            
            # Execute the graph
            final_state = self.graph.invoke(initial_state)
            
            # Return comprehensive response
            return {
                "user": final_state.get("user"),
                "user_id": final_state.get("user_id"),
                "question": final_state.get("question"),
                "agent": final_state.get("current_agent"),
                "response": final_state.get("final_response", final_state.get("response", "")),
                "agent_responses": final_state.get("agent_responses", {}),
                "execution_path": final_state.get("execution_path", []),
                "edges_traversed": final_state.get("edges_traversed", []),
                "context": final_state.get("context", {}),
                "timestamp": final_state.get("timestamp"),
                "system_version": "2.0.0-multiagent",
                "agents_involved": list(final_state.get("agent_responses", {}).keys())
            }
            
        except Exception as e:
            logger.error(f"Multiagent system execution failed: {e}")
            return {
                "user": user,
                "user_id": user_id,
                "question": question,
                "agent": "ErrorHandler",
                "response": f"Multiagent system error: {str(e)}",
                "error": True,
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_stm_context(self, user_id: int) -> Dict[str, Any]:
        """Get short-term memory context"""
        try:
            stm_data = self.memory_manager.get_all_stm_for_user(str(user_id))
            return {
                "recent_interactions": stm_data,
                "count": len(stm_data)
            }
        except Exception as e:
            logger.warning(f"Could not fetch STM context: {e}")
            return {}
    
    def _get_ltm_context(self, user_id: int) -> Dict[str, Any]:
        """Get long-term memory context"""
        try:
            ltm_data = self.memory_manager.get_recent_ltm(str(user_id), days=7)
            return {
                "recent_history": ltm_data[:10],
                "count": len(ltm_data)
            }
        except Exception as e:
            logger.warning(f"Could not fetch LTM context: {e}")
            return {}

# Global multiagent system instance
langgraph_multiagent_system = LangGraphMultiAgentSystem()
