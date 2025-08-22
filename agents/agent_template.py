"""
Agent Template - Ready to Use
============================
Copy this file and customize it to create your own agent.

STEPS TO CREATE YOUR AGENT:
1. Copy this file: cp agents/agent_template.py agents/your_agent_name.py
2. Replace all UPPERCASE placeholders with your values
3. Add your domain-specific logic in the custom methods
4. Add your agent to core/agents.json
5. Restart the server

EXAMPLE DOMAINS: Weather, Recipe, Stock, Music, Health, Education, etc.
"""

from typing import Dict, Any, List
import logging
from core.base_agent import BaseAgent, GraphState

logger = logging.getLogger(__name__)


class YOUR_AGENT_NAMEAgent(BaseAgent):
    """
    Replace YOUR_AGENT_NAME with your agent name (e.g., WeatherAnalyzer, RecipeRecommender)
    
    This agent specializes in YOUR_DOMAIN_HERE
    """
    
    def __init__(self, memory_manager=None, name: str = "YOUR_AGENT_NAME"):
        super().__init__(memory_manager, name)
        
        # Brief description of what your agent does
        self._description = "YOUR_AGENT_DESCRIPTION_HERE"
        
        # Define 5 capabilities that your agent provides
        self._capabilities = [
            "YOUR_CAPABILITY_1",     # e.g., "weather_forecasting"
            "YOUR_CAPABILITY_2",     # e.g., "recipe_search" 
            "YOUR_CAPABILITY_3",     # e.g., "market_analysis"
            "YOUR_CAPABILITY_4",     # e.g., "recommendation_engine"
            "YOUR_CAPABILITY_5"      # e.g., "data_analysis"
        ]
    
    @property
    def keywords(self) -> List[str]:
        """
        Keywords that trigger this agent - users will search with these terms
        Add 7+ words related to your domain
        """
        return [
            "YOUR_KEYWORD_1",        # e.g., "weather"
            "YOUR_KEYWORD_2",        # e.g., "temperature"
            "YOUR_KEYWORD_3",        # e.g., "recipe"
            "YOUR_KEYWORD_4",        # e.g., "cooking"
            "YOUR_KEYWORD_5",        # e.g., "stock"
            "YOUR_KEYWORD_6",        # e.g., "investment"
            "YOUR_KEYWORD_7"         # e.g., "music"
        ]
    
    @property
    def system_prompt(self) -> str:
        """
        This defines your agent's personality and expertise for the AI model
        """
        return """You are YOUR_AGENT_NAME, an expert in YOUR_DOMAIN_AREA.

Your expertise includes:
- YOUR_EXPERTISE_1 (e.g., Weather forecasting and analysis)
- YOUR_EXPERTISE_2 (e.g., Recipe recommendations)
- YOUR_EXPERTISE_3 (e.g., Market trend analysis)
- YOUR_EXPERTISE_4 (e.g., Music discovery and curation)
- YOUR_EXPERTISE_5 (e.g., Health and wellness advice)

Provide accurate, helpful information about YOUR_DOMAIN_AREA.
Always be practical and give actionable advice.
Adapt your language to the user's knowledge level."""

    def get_capabilities(self) -> List[str]:
        """Return the list of capabilities this agent provides"""
        return self._capabilities
    
    def process(self, state: GraphState) -> GraphState:
        """
        Main method that processes user queries
        This is where your agent's logic goes
        """
        if not self.validate_state(state):
            return self.handle_error(state, ValueError("Invalid state received"))
        
        query = state.get("question", "")
        user_id = state.get("user_id", 0)
        
        try:
            # Log that we're processing this query
            self.log_processing(query, user_id)
            
            # Search for similar past queries from this user
            search_results = self.search_similar_content(query, user_id, limit=3)
            
            # Get user's recent history for context
            historical_context = self.get_historical_context(user_id, days=7)
            
            # Build context for the AI model
            context_parts = []
            
            # Add previous similar searches
            if search_results.get("similar_content"):
                context_parts.append(f"Previous {self.name.lower()} searches:")
                for item in search_results["similar_content"][:2]:
                    if isinstance(item, dict) and "content" in item:
                        context_parts.append(f"- {item['content'][:100]}...")
            
            # Add recent user history  
            if historical_context:
                context_parts.append(f"Recent {self.name.lower()} history:")
                for item in historical_context[-2:]:
                    if isinstance(item, dict) and "value" in item:
                        context_parts.append(f"- {item['value'][:100]}...")
            
            # Detect what category this query falls into
            category = self._detect_category(query)
            if category != "general":
                context_parts.append(f"Query category: {category}")
            
            # Detect the focus of this query
            focus = self._detect_focus(query)
            if focus != "general":
                context_parts.append(f"Focus area: {focus}")
            
            # Combine all context
            context = "\n".join(context_parts) if context_parts else ""
            
            # Generate response using AI model
            response = self.generate_response_with_context(
                query=query,
                context=context,
                temperature=0.7  # Adjust for creativity vs accuracy
            )
            
            # Store this interaction for future reference
            self.store_interaction(
                user_id=user_id,
                query=query,
                response=response,
                interaction_type=f"{self.name.lower()}_query",
                metadata={
                    "category": category,
                    "focus": focus,
                    "had_context": bool(context_parts)
                }
            )
            
            # Store vector embedding for similarity search
            self.store_vector_embedding(
                user_id=user_id,
                content=f"{self.name} Query: {query}\nResponse: {response}",
                metadata={
                    "agent": self.name,
                    "domain": "YOUR_DOMAIN_KEY",  # e.g., "weather", "recipes", "stocks"
                    "category": category,
                    "focus": focus
                }
            )
            
            # Return formatted response
            return self.format_state_response(
                state=state,
                response=response,
                additional_data={
                    "orchestration": {
                        "agent": self.name,
                        "category": category,
                        "focus": focus,
                        "context_used": bool(context_parts)
                    }
                }
            )
            
        except Exception as e:
            # Handle any errors gracefully
            return self.handle_error(state, e)
    
    def can_handle(self, query: str) -> float:
        """
        Determine how confident this agent is about handling the query
        Returns score from 0.0 (can't handle) to 1.0 (perfect match)
        """
        # Start with basic confidence from parent class
        confidence = super().can_handle(query)
        query_lower = query.lower()
        
        # High confidence terms - strong indicators of your domain
        high_confidence_terms = [
            "YOUR_HIGH_CONFIDENCE_TERM_1",    # e.g., "weather forecast"
            "YOUR_HIGH_CONFIDENCE_TERM_2",    # e.g., "recipe ingredients"  
            "YOUR_HIGH_CONFIDENCE_TERM_3"     # e.g., "stock analysis"
        ]
        if any(term in query_lower for term in high_confidence_terms):
            confidence = min(confidence + 0.4, 1.0)
        
        # Medium confidence terms - related to your domain
        medium_confidence_terms = [
            "YOUR_MEDIUM_TERM_1",    # e.g., "sunny"
            "YOUR_MEDIUM_TERM_2",    # e.g., "cooking"
            "YOUR_MEDIUM_TERM_3"     # e.g., "market"
        ]
        if any(term in query_lower for term in medium_confidence_terms):
            confidence = min(confidence + 0.3, 1.0)
        
        # Activity-related terms - things people do with your domain
        activity_terms = [
            "YOUR_ACTIVITY_TERM_1",    # e.g., "outdoor planning"
            "YOUR_ACTIVITY_TERM_2",    # e.g., "meal planning"
            "YOUR_ACTIVITY_TERM_3"     # e.g., "investment planning"
        ]
        if any(term in query_lower for term in activity_terms):
            confidence = min(confidence + 0.2, 1.0)
        
        return confidence
    
    def _detect_category(self, query: str) -> str:
        """
        Detect what category this query belongs to within your domain
        """
        query_lower = query.lower()
        
        # Define 3 main categories for your domain
        if any(term in query_lower for term in ["CATEGORY_1_TERM_1", "CATEGORY_1_TERM_2"]):
            return "YOUR_CATEGORY_1"  # e.g., "short_term" for weather
        elif any(term in query_lower for term in ["CATEGORY_2_TERM_1", "CATEGORY_2_TERM_2"]):
            return "YOUR_CATEGORY_2"  # e.g., "long_term" for weather
        elif any(term in query_lower for term in ["CATEGORY_3_TERM_1", "CATEGORY_3_TERM_2"]):
            return "YOUR_CATEGORY_3"  # e.g., "emergency" for weather
        else:
            return "general"
    
    def _detect_focus(self, query: str) -> str:
        """
        Detect the focus area of this query
        """
        query_lower = query.lower()
        
        # Define focus areas for your domain
        if any(term in query_lower for term in ["FOCUS_1_TERM_1", "FOCUS_1_TERM_2"]):
            return "YOUR_FOCUS_AREA_1"  # e.g., "planning"
        elif any(term in query_lower for term in ["FOCUS_2_TERM_1", "FOCUS_2_TERM_2"]):
            return "YOUR_FOCUS_AREA_2"  # e.g., "analysis"
        elif any(term in query_lower for term in ["FOCUS_3_TERM_1", "FOCUS_3_TERM_2"]):
            return "YOUR_FOCUS_AREA_3"  # e.g., "recommendations"
        else:
            return "general"
    
    # ADD YOUR CUSTOM METHODS HERE
    def your_custom_method_1(self, parameter1, parameter2):
        """
        Add your domain-specific logic here
        
        Example for weather agent:
        def get_weather_forecast(self, location: str, days: int):
            # Call weather API
            # Process data
            # Return forecast
        """
        # Your implementation here
        pass
    
    def your_custom_method_2(self, parameter1):
        """
        Another custom method for your domain
        
        Example for recipe agent:
        def search_recipes_by_ingredients(self, ingredients: List[str]):
            # Search recipe database
            # Filter by ingredients
            # Return matching recipes
        """
        # Your implementation here
        pass
    
    def get_domain_recommendations(self, category: str) -> List[str]:
        """
        Generate recommendations specific to your domain
        """
        recommendations = []
        
        if category == "YOUR_CATEGORY_1":
            recommendations = [
                "YOUR_RECOMMENDATION_1_FOR_CATEGORY_1",
                "YOUR_RECOMMENDATION_2_FOR_CATEGORY_1"
            ]
        elif category == "YOUR_CATEGORY_2":
            recommendations = [
                "YOUR_RECOMMENDATION_1_FOR_CATEGORY_2", 
                "YOUR_RECOMMENDATION_2_FOR_CATEGORY_2"
            ]
        elif category == "YOUR_CATEGORY_3":
            recommendations = [
                "YOUR_RECOMMENDATION_1_FOR_CATEGORY_3",
                "YOUR_RECOMMENDATION_2_FOR_CATEGORY_3"
            ]
        else:
            recommendations = [
                "YOUR_GENERAL_RECOMMENDATION_1",
                "YOUR_GENERAL_RECOMMENDATION_2"
            ]
        
        return recommendations


# CONFIGURATION TEMPLATE FOR AGENTS.JSON
# Copy this and add to your core/agents.json file:
"""
{
  "id": "YOUR_AGENT_NAMEAgent",
  "name": "YOUR_AGENT_NAME Agent",
  "module": "agents.YOUR_FILE_NAME",
  "description": "YOUR_AGENT_DESCRIPTION_HERE",
  "capabilities": ["YOUR_CAPABILITY_1", "YOUR_CAPABILITY_2", "YOUR_CAPABILITY_3"],
  "priority": 4
}
"""

# EDGE CONNECTIONS TEMPLATE
# Add these connections to the "edges" section in agents.json:
"""
"YOUR_AGENT_NAMEAgent": ["SearchAgent"],
"ScenicLocationFinderAgent": ["YOUR_AGENT_NAMEAgent", "ForestAnalyzerAgent", "SearchAgent"]
"""
