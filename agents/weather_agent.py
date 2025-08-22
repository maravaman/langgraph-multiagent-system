"""
Weather Agent
Specialized agent for weather information, forecasts, and climate analysis
Part of the LangGraph Multiagent System
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
from core.base_agent import BaseAgent, GraphState

logger = logging.getLogger(__name__)

class WeatherAgent(BaseAgent):
    """Agent specialized in weather information and climate analysis"""
    
    def __init__(self, memory_manager=None, name: str = "WeatherAgent"):
        super().__init__(memory_manager, name)
        self._description = "Weather information, forecasts, and climate analysis specialist"
        self._capabilities = [
            "weather_forecast",
            "climate_analysis", 
            "meteorology",
            "weather_planning",
            "seasonal_patterns",
            "weather_alerts",
            "outdoor_activity_weather",
            "travel_weather_advice"
        ]
    
    @property
    def keywords(self) -> List[str]:
        """Keywords that trigger this agent"""
        return [
            "weather", "temperature", "rain", "sun", "climate", "forecast", 
            "humidity", "wind", "storm", "snow", "hot", "cold", "sunny",
            "cloudy", "precipitation", "barometric", "pressure", "degrees"
        ]
    
    @property
    def system_prompt(self) -> str:
        """System prompt for weather agent"""
        return """You are WeatherAgent, a specialized weather and climate analysis assistant. 

Your capabilities include:
- Weather forecasts and current conditions
- Climate analysis and seasonal patterns  
- Weather-related planning advice
- Impact assessments for outdoor activities
- Travel weather recommendations
- Severe weather alerts and safety advice
- Meteorological explanations
- Weather data interpretation

Provide practical, actionable weather information that helps users make informed decisions.
Be specific with temperature ranges, precipitation chances, and timing when possible.
Consider the impact of weather on user activities and provide relevant recommendations."""

    def process(self, state: GraphState) -> GraphState:
        """Process weather-related queries"""
        if not self.validate_state(state):
            return self.handle_error(state, ValueError("Invalid state received"))
        
        query = state.get("question", "")
        user_id = state.get("user_id", 0)
        
        try:
            self.log_processing(query, user_id)
            
            # Extract location context if available
            location_context = self._extract_location_context(state)
            
            # Analyze weather query type
            weather_type = self._analyze_weather_query(query)
            
            # Generate weather response
            weather_response = self._generate_weather_response(query, location_context, weather_type)
            
            # Store the weather interaction
            self.store_interaction(
                user_id=user_id,
                query=query,
                response=weather_response,
                interaction_type="weather_analysis",
                metadata={
                    "weather_type": weather_type,
                    "location_context": location_context,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return self.format_state_response(
                state=state,
                response=weather_response,
                additional_data={
                    "weather_data": {
                        "analysis_type": weather_type,
                        "location_context": location_context,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def can_handle(self, query: str) -> float:
        """Determine if this agent can handle the weather query"""
        base_confidence = super().can_handle(query)
        
        query_lower = query.lower()
        
        # High confidence weather terms
        high_confidence_terms = [
            "weather forecast", "what's the weather", "temperature today", 
            "will it rain", "is it sunny", "weather condition"
        ]
        if any(term in query_lower for term in high_confidence_terms):
            base_confidence = min(base_confidence + 0.6, 1.0)
        
        # Weather activity terms
        activity_terms = [
            "outdoor activity", "hiking weather", "beach weather", 
            "travel weather", "weather for"
        ]
        if any(term in query_lower for term in activity_terms):
            base_confidence = min(base_confidence + 0.4, 1.0)
        
        # Specific weather phenomena
        phenomena_terms = [
            "storm", "hurricane", "snow", "blizzard", "heat wave", 
            "cold front", "precipitation"
        ]
        if any(term in query_lower for term in phenomena_terms):
            base_confidence = min(base_confidence + 0.3, 1.0)
        
        return base_confidence
    
    def _extract_location_context(self, state: GraphState) -> str:
        """Extract location information from state or query"""
        location_data = state.get("location_data", {})
        if location_data:
            return location_data.get("location", "")
        
        # Try to extract from query
        query = state.get("question", "").lower()
        
        # Simple location extraction (can be enhanced with NLP)
        location_keywords = ["in ", "at ", "for ", "around ", "near "]
        for keyword in location_keywords:
            if keyword in query:
                parts = query.split(keyword)
                if len(parts) > 1:
                    potential_location = parts[1].split()[0:3]  # Take next few words
                    return " ".join(potential_location)
        
        return "general area"
    
    def _analyze_weather_query(self, query: str) -> str:
        """Analyze the type of weather query"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["forecast", "tomorrow", "next week", "future"]):
            return "forecast"
        elif any(term in query_lower for term in ["current", "now", "today", "right now"]):
            return "current_conditions"
        elif any(term in query_lower for term in ["climate", "seasonal", "average", "typical"]):
            return "climate_analysis"
        elif any(term in query_lower for term in ["activity", "outdoor", "travel", "plan"]):
            return "activity_planning"
        elif any(term in query_lower for term in ["alert", "warning", "severe", "storm"]):
            return "weather_alerts"
        else:
            return "general_weather"
    
    def _generate_weather_response(self, query: str, location_context: str, weather_type: str) -> str:
        """Generate comprehensive weather response"""
        try:
            # Use the LLM to generate weather response
            from core.ollama_client import ollama_client
            
            # Create enhanced prompt with context
            enhanced_query = f"{query}"
            if location_context and location_context != "general area":
                enhanced_query += f" (Location context: {location_context})"
            
            context_prompt = f"""Weather Query Type: {weather_type}
Location: {location_context}
Query: {enhanced_query}

Please provide a comprehensive weather analysis including:
1. Current conditions or forecast as appropriate
2. Temperature information
3. Precipitation chances if relevant
4. Wind conditions
5. Any weather advisories or recommendations
6. Impact on activities if mentioned

Be specific, practical, and helpful."""

            response = ollama_client.generate_response(
                prompt=context_prompt,
                system_prompt=self.system_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate weather response: {e}")
            return f"I apologize, but I'm having trouble accessing current weather information. Please try again or check a reliable weather service for {location_context}."
    
    def get_weather_for_location(self, location: str, query_type: str = "current") -> Dict[str, Any]:
        """Get weather information for a specific location"""
        try:
            weather_query = f"What is the {query_type} weather for {location}?"
            
            response = self._generate_weather_response(weather_query, location, query_type)
            
            return {
                "location": location,
                "query_type": query_type,
                "weather_info": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get weather for {location}: {e}")
            return {
                "location": location,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_activity_weather_advice(self, activity: str, location: str = "general area") -> str:
        """Get weather advice for specific activities"""
        try:
            query = f"What's the weather advice for {activity} in {location}?"
            return self._generate_weather_response(query, location, "activity_planning")
            
        except Exception as e:
            logger.error(f"Failed to get activity weather advice: {e}")
            return f"Unable to provide weather advice for {activity} at this time. Please check current weather conditions."
