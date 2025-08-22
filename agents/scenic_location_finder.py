"""
Scenic Location Finder Agent
Specializes in providing recommendations for scenic locations with practical information,
cultural insights, and photography tips.
"""

from typing import Dict, Any, List
import logging
from core.base_agent import BaseAgent, GraphState

logger = logging.getLogger(__name__)


class ScenicLocationFinderAgent(BaseAgent):
    """Agent specialized in finding and recommending scenic locations"""
    
    def __init__(self, memory_manager=None, name: str = "ScenicLocationFinder"):
        super().__init__(memory_manager, name)
        self._description = "Scenic location finding agent for beautiful places with detailed recommendations"
        self._capabilities = [
            "scenic_location_recommendations",
            "travel_planning",
            "photography_tips",
            "cultural_insights",
            "practical_travel_information"
        ]
    
    @property
    def keywords(self) -> List[str]:
        """Keywords that trigger this agent"""
        return [
            "scenic", "mountain", "landscape", "beautiful", "view", 
            "tourist", "visit", "travel", "place", "location", 
            "destination", "photography", "sight", "attraction"
        ]
    
    @property
    def system_prompt(self) -> str:
        """System prompt for this agent"""
        return """You are ScenicLocationFinder, an expert travel and scenic location advisor. 
        Provide detailed recommendations for scenic locations with:
        - Practical travel information (how to get there, best times to visit)
        - Cultural insights and local significance
        - Photography tips and best viewpoints
        - Nearby amenities and accommodation options
        - Safety considerations and preparation tips
        
        Always be enthusiastic about beautiful places while providing accurate, helpful information."""
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self._capabilities
    
    def process(self, state: GraphState) -> GraphState:
        """Process scenic location queries"""
        if not self.validate_state(state):
            return self.handle_error(state, ValueError("Invalid state received"))
        
        query = state.get("question", "")
        user_id = state.get("user_id", 0)
        
        try:
            self.log_processing(query, user_id)
            
            # Search for similar past queries
            search_results = self.search_similar_content(query, user_id, limit=3)
            
            # Get recent context
            recent_context = self.get_recent_interactions(user_id, hours=2)
            
            # Build context from search results and recent interactions
            context_parts = []
            if search_results.get("similar_content"):
                context_parts.append("Previous similar queries:")
                for item in search_results["similar_content"][:2]:
                    if isinstance(item, dict) and "content" in item:
                        context_parts.append(f"- {item['content'][:100]}...")
            
            if recent_context:
                context_parts.append("Recent conversation context:")
                for item in recent_context[-2:]:
                    if isinstance(item, str):
                        context_parts.append(f"- {item[:100]}...")
            
            context = "\n".join(context_parts) if context_parts else ""
            
            # Generate response using LLM
            response = self.generate_response_with_context(
                query=query,
                context=context,
                temperature=0.7
            )
            
            # Store the interaction
            self.store_interaction(
                user_id=user_id,
                query=query,
                response=response,
                interaction_type="scenic_location_query"
            )
            
            # Store vector embedding for future searches
            self.store_vector_embedding(
                user_id=user_id,
                content=f"Query: {query}\nResponse: {response}",
                metadata={"agent": self.name, "query_type": "scenic_location"}
            )
            
            return self.format_state_response(
                state=state,
                response=response,
                additional_data={
                    "orchestration": {
                        "strategy": "scenic_location_specialized",
                        "selected_agents": [self.name],
                        "context_used": bool(context_parts)
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def can_handle(self, query: str) -> float:
        """
        Determine if this agent can handle the query
        Enhanced logic for scenic location detection
        """
        base_confidence = super().can_handle(query)
        
        # Additional confidence boosters
        query_lower = query.lower()
        
        # High-confidence terms
        high_confidence_terms = ["scenic", "beautiful place", "tourist destination", "landscape"]
        if any(term in query_lower for term in high_confidence_terms):
            base_confidence = min(base_confidence + 0.3, 1.0)
        
        # Location-related terms
        location_terms = ["where to visit", "places to see", "destination", "travel to"]
        if any(term in query_lower for term in location_terms):
            base_confidence = min(base_confidence + 0.2, 1.0)
        
        # Photography-related terms
        photo_terms = ["photography", "photo spot", "instagram", "picture"]
        if any(term in query_lower for term in photo_terms):
            base_confidence = min(base_confidence + 0.1, 1.0)
        
        return base_confidence
    
    def get_specialized_recommendations(self, location_type: str, region: str = "") -> Dict[str, Any]:
        """
        Get specialized recommendations for specific location types
        
        Args:
            location_type: Type of location (mountain, beach, forest, etc.)
            region: Geographic region
            
        Returns:
            Dictionary with specialized recommendations
        """
        # This could be enhanced to query external APIs or databases
        recommendations = {
            "location_type": location_type,
            "region": region,
            "recommendations": [],
            "tips": []
        }
        
        if location_type.lower() == "mountain":
            recommendations["tips"] = [
                "Visit during golden hour for best photography",
                "Check weather conditions before hiking",
                "Bring layers for temperature changes",
                "Consider altitude effects"
            ]
        elif location_type.lower() == "beach":
            recommendations["tips"] = [
                "Visit during sunrise or sunset for best photos",
                "Check tide schedules",
                "Bring sun protection",
                "Research local marine life"
            ]
        
        return recommendations
