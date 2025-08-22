"""
Dining Agent
Specialized agent for restaurant recommendations, cuisine analysis, and dining experiences
Part of the LangGraph Multiagent System
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
from core.base_agent import BaseAgent, GraphState

logger = logging.getLogger(__name__)

class DiningAgent(BaseAgent):
    """Agent specialized in dining, restaurants, and culinary experiences"""
    
    def __init__(self, memory_manager=None, name: str = "DiningAgent"):
        super().__init__(memory_manager, name)
        self._description = "Restaurant recommendations, cuisine analysis, and dining experience specialist"
        self._capabilities = [
            "restaurant_recommendations",
            "cuisine_analysis",
            "dining_planning",
            "food_culture",
            "menu_analysis",
            "dining_experiences",
            "local_specialties",
            "dietary_recommendations",
            "chef_recommendations",
            "wine_pairing",
            "food_events"
        ]
    
    @property
    def keywords(self) -> List[str]:
        """Keywords that trigger this agent"""
        return [
            "restaurant", "food", "cuisine", "dining", "eat", "meal", "chef", 
            "menu", "cooking", "recipe", "taste", "flavor", "dish", "kitchen",
            "cafe", "bistro", "eatery", "dine", "lunch", "dinner", "breakfast",
            "culinary", "gastronomy", "delicious", "tasty"
        ]
    
    @property
    def system_prompt(self) -> str:
        """System prompt for dining agent"""
        return """You are DiningAgent, a culinary and restaurant specialist with expertise in dining experiences worldwide.

Your capabilities include:
- Restaurant recommendations and reviews
- Cuisine analysis and cultural context
- Menu suggestions and dish recommendations
- Local food specialties and hidden gems
- Dietary accommodations and alternatives
- Dining etiquette and cultural customs
- Food and wine pairings
- Culinary events and food festivals
- Chef recommendations and signature dishes
- Seasonal menu insights

Provide detailed, enticing dining recommendations that consider:
- Location and accessibility
- Price range and value
- Ambiance and dining experience
- Quality and authenticity
- Dietary restrictions and preferences
- Weather considerations for outdoor dining
- Local cultural context

Be descriptive and help users discover amazing dining experiences."""

    def process(self, state: GraphState) -> GraphState:
        """Process dining-related queries"""
        if not self.validate_state(state):
            return self.handle_error(state, ValueError("Invalid state received"))
        
        query = state.get("question", "")
        user_id = state.get("user_id", 0)
        
        try:
            self.log_processing(query, user_id)
            
            # Extract context from other agents
            context_data = self._extract_multi_agent_context(state)
            
            # Analyze dining query type
            dining_type = self._analyze_dining_query(query)
            
            # Generate dining response with context
            dining_response = self._generate_dining_response(query, context_data, dining_type)
            
            # Store the dining interaction
            self.store_interaction(
                user_id=user_id,
                query=query,
                response=dining_response,
                interaction_type="dining_analysis",
                metadata={
                    "dining_type": dining_type,
                    "context_data": context_data,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return self.format_state_response(
                state=state,
                response=dining_response,
                additional_data={
                    "dining_data": {
                        "analysis_type": dining_type,
                        "context_integrated": bool(context_data),
                        "location_considered": context_data.get("location", "") != "",
                        "weather_considered": context_data.get("weather", "") != "",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def can_handle(self, query: str) -> float:
        """Determine if this agent can handle the dining query"""
        base_confidence = super().can_handle(query)
        
        query_lower = query.lower()
        
        # High confidence dining terms
        high_confidence_terms = [
            "restaurant recommendation", "where to eat", "best food", 
            "dining options", "good restaurant", "food recommendation"
        ]
        if any(term in query_lower for term in high_confidence_terms):
            base_confidence = min(base_confidence + 0.6, 1.0)
        
        # Cuisine-specific terms
        cuisine_terms = [
            "italian food", "chinese restaurant", "indian cuisine", "mexican food",
            "french restaurant", "japanese dining", "local cuisine", "street food"
        ]
        if any(term in query_lower for term in cuisine_terms):
            base_confidence = min(base_confidence + 0.5, 1.0)
        
        # Dining experience terms
        experience_terms = [
            "fine dining", "casual dining", "romantic dinner", "family restaurant",
            "business lunch", "quick bite", "food truck", "cafe"
        ]
        if any(term in query_lower for term in experience_terms):
            base_confidence = min(base_confidence + 0.4, 1.0)
        
        return base_confidence
    
    def _extract_multi_agent_context(self, state: GraphState) -> Dict[str, str]:
        """Extract context from other agents in the system"""
        context_data = {}
        
        # Extract location context
        location_data = state.get("location_data", {})
        if location_data:
            context_data["location"] = location_data.get("recommendations", "")[:200]
        
        # Extract weather context
        weather_data = state.get("weather_data", {})
        if weather_data:
            context_data["weather"] = weather_data.get("forecast", "")[:200]
        
        # Extract forest/nature context
        forest_data = state.get("forest_data", {})
        if forest_data:
            context_data["nature"] = forest_data.get("analysis", "")[:200]
        
        # Extract from query for location hints
        query = state.get("question", "").lower()
        location_hints = self._extract_location_hints(query)
        if location_hints:
            context_data["location_hints"] = location_hints
        
        return context_data
    
    def _extract_location_hints(self, query: str) -> str:
        """Extract location hints from query"""
        location_keywords = ["in ", "at ", "near ", "around ", "downtown ", "city center "]
        for keyword in location_keywords:
            if keyword in query:
                parts = query.split(keyword)
                if len(parts) > 1:
                    potential_location = parts[1].split()[0:3]
                    return " ".join(potential_location)
        return ""
    
    def _analyze_dining_query(self, query: str) -> str:
        """Analyze the type of dining query"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["recommend", "suggestion", "where to eat"]):
            return "restaurant_recommendation"
        elif any(term in query_lower for term in ["cuisine", "food type", "cooking style"]):
            return "cuisine_analysis"
        elif any(term in query_lower for term in ["menu", "dish", "order", "specialty"]):
            return "menu_analysis"
        elif any(term in query_lower for term in ["fine dining", "romantic", "special occasion"]):
            return "fine_dining"
        elif any(term in query_lower for term in ["quick", "fast", "casual", "grab"]):
            return "casual_dining"
        elif any(term in query_lower for term in ["local", "authentic", "traditional"]):
            return "local_specialties"
        elif any(term in query_lower for term in ["vegetarian", "vegan", "gluten", "dietary"]):
            return "dietary_accommodation"
        else:
            return "general_dining"
    
    def _generate_dining_response(self, query: str, context_data: Dict[str, str], dining_type: str) -> str:
        """Generate comprehensive dining response with context"""
        try:
            from core.ollama_client import ollama_client
            
            # Build context-enhanced prompt
            enhanced_query = f"{query}"
            context_additions = []
            
            if context_data.get("location"):
                context_additions.append(f"Location context: {context_data['location'][:100]}...")
            if context_data.get("weather"):
                context_additions.append(f"Weather context: {context_data['weather'][:100]}...")
            if context_data.get("location_hints"):
                context_additions.append(f"Location: {context_data['location_hints']}")
            
            if context_additions:
                enhanced_query += f"\n\nAdditional context: {'; '.join(context_additions)}"
            
            dining_prompt = f"""Dining Query Type: {dining_type}
Query: {enhanced_query}

Please provide comprehensive dining recommendations including:

1. **Restaurant Suggestions**: Specific restaurant names or types
2. **Cuisine Analysis**: Style, flavors, and cultural context
3. **Location Considerations**: Accessibility and area recommendations  
4. **Ambiance & Experience**: Dining atmosphere and setting
5. **Menu Highlights**: Signature dishes or must-try items
6. **Price Range**: Budget considerations and value
7. **Special Considerations**: 
   - Weather impact (if outdoor dining mentioned)
   - Dietary accommodations (if mentioned)
   - Time of day appropriateness
8. **Local Insights**: Hidden gems or local favorites

Be specific, enticing, and practical in your recommendations."""

            response = ollama_client.generate_response(
                prompt=dining_prompt,
                system_prompt=self.system_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate dining response: {e}")
            return f"I apologize, but I'm having trouble providing dining recommendations at the moment. Please try again or consult local dining guides for the best restaurant options."
    
    def get_restaurant_recommendations(self, location: str, cuisine_type: str = "", budget: str = "") -> Dict[str, Any]:
        """Get specific restaurant recommendations"""
        try:
            query_parts = ["restaurant recommendations"]
            if location:
                query_parts.append(f"in {location}")
            if cuisine_type:
                query_parts.append(f"for {cuisine_type} cuisine")
            if budget:
                query_parts.append(f"with {budget} budget")
            
            query = " ".join(query_parts)
            context_data = {"location_hints": location}
            
            response = self._generate_dining_response(query, context_data, "restaurant_recommendation")
            
            return {
                "location": location,
                "cuisine_type": cuisine_type,
                "budget": budget,
                "recommendations": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get restaurant recommendations: {e}")
            return {
                "location": location,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_cuisine_analysis(self, cuisine_type: str, location: str = "") -> str:
        """Get detailed cuisine analysis"""
        try:
            query = f"Tell me about {cuisine_type} cuisine"
            if location:
                query += f" in {location}"
            
            context_data = {"location_hints": location} if location else {}
            return self._generate_dining_response(query, context_data, "cuisine_analysis")
            
        except Exception as e:
            logger.error(f"Failed to analyze cuisine {cuisine_type}: {e}")
            return f"Unable to provide cuisine analysis for {cuisine_type} at this time."
    
    def get_dietary_recommendations(self, dietary_restriction: str, location: str = "") -> str:
        """Get recommendations for specific dietary needs"""
        try:
            query = f"Restaurant recommendations for {dietary_restriction} diet"
            if location:
                query += f" in {location}"
            
            context_data = {"location_hints": location} if location else {}
            return self._generate_dining_response(query, context_data, "dietary_accommodation")
            
        except Exception as e:
            logger.error(f"Failed to get dietary recommendations: {e}")
            return f"Unable to provide {dietary_restriction} dining recommendations at this time."
    
    def get_weather_appropriate_dining(self, weather_condition: str, location: str = "") -> str:
        """Get dining recommendations based on weather"""
        try:
            query = f"Dining recommendations for {weather_condition} weather"
            if location:
                query += f" in {location}"
            
            context_data = {
                "weather": f"Weather condition: {weather_condition}",
                "location_hints": location
            }
            
            return self._generate_dining_response(query, context_data, "restaurant_recommendation")
            
        except Exception as e:
            logger.error(f"Failed to get weather-appropriate dining recommendations: {e}")
            return f"Unable to provide weather-appropriate dining suggestions for {weather_condition} conditions."
