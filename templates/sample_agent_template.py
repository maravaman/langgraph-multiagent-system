"""
Sample Agent Template
====================
This template provides a complete example for creating custom agents in the multi-agent system.
Copy this file and modify it according to your specific domain requirements.

Domain: [YOUR_DOMAIN_NAME] (e.g., "Weather Analysis", "Recipe Recommendations", "Stock Analysis")
Description: [BRIEF_DESCRIPTION_OF_WHAT_YOUR_AGENT_DOES]
"""

from typing import Dict, Any, List
import logging
from core.base_agent import BaseAgent, GraphState

logger = logging.getLogger(__name__)


class [YOUR_AGENT_NAME]Agent(BaseAgent):
    """
    Agent specialized in [YOUR_DOMAIN_DESCRIPTION]
    
    Replace [YOUR_AGENT_NAME] with your actual agent name (e.g., WeatherAnalyzer, RecipeRecommender)
    Replace [YOUR_DOMAIN_DESCRIPTION] with your domain description
    """
    
    def __init__(self, memory_manager=None, name: str = "[YOUR_AGENT_NAME]"):
        super().__init__(memory_manager, name)
        self._description = "[BRIEF_DESCRIPTION_OF_YOUR_AGENT]"
        
        # Define your agent's capabilities - these are used for agent selection
        self._capabilities = [
            "[CAPABILITY_1]",      # e.g., "weather_forecasting"
            "[CAPABILITY_2]",      # e.g., "climate_analysis"  
            "[CAPABILITY_3]",      # e.g., "weather_alerts"
            "[CAPABILITY_4]",      # e.g., "seasonal_patterns"
            "[CAPABILITY_5]"       # e.g., "location_weather"
        ]
    
    @property
    def keywords(self) -> List[str]:
        """
        Keywords that trigger this agent - used for democratic agent selection
        Add keywords related to your domain that users might use in queries
        """
        return [
            "[KEYWORD_1]",         # e.g., "weather"
            "[KEYWORD_2]",         # e.g., "temperature"
            "[KEYWORD_3]",         # e.g., "forecast"
            "[KEYWORD_4]",         # e.g., "rain"
            "[KEYWORD_5]",         # e.g., "climate"
            "[KEYWORD_6]",         # e.g., "storm"
            "[KEYWORD_7]"          # e.g., "sunny"
        ]
    
    @property
    def system_prompt(self) -> str:
        """
        System prompt that defines your agent's personality and expertise
        This is sent to the LLM to guide response generation
        """
        return """You are [YOUR_AGENT_NAME], an expert in [YOUR_DOMAIN_AREA].
        
        Your expertise includes:
        - [EXPERTISE_AREA_1] (e.g., Weather pattern analysis and forecasting)
        - [EXPERTISE_AREA_2] (e.g., Climate data interpretation)
        - [EXPERTISE_AREA_3] (e.g., Seasonal trend analysis)
        - [EXPERTISE_AREA_4] (e.g., Location-specific weather insights)
        - [EXPERTISE_AREA_5] (e.g., Weather impact on activities and planning)
        
        Provide accurate, helpful, and actionable information about [YOUR_DOMAIN].
        Always consider the user's context and provide relevant recommendations.
        Be informative yet accessible to different knowledge levels."""
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self._capabilities
    
    def process(self, state: GraphState) -> GraphState:
        """
        Main processing method - this is where your agent logic goes
        
        Args:
            state: Current graph state containing user query and context
            
        Returns:
            Updated graph state with agent's response
        """
        if not self.validate_state(state):
            return self.handle_error(state, ValueError("Invalid state received"))
        
        query = state.get("question", "")
        user_id = state.get("user_id", 0)
        
        try:
            self.log_processing(query, user_id)
            
            # Search for similar content in user's history
            search_results = self.search_similar_content(query, user_id, limit=3)
            
            # Get historical context from user's recent activity
            historical_context = self.get_historical_context(user_id, days=7)
            
            # Build context for your domain-specific analysis
            context_parts = []
            
            # Add similar content context
            if search_results.get("similar_content"):
                context_parts.append(f"Previous {self.name.lower()} research:")
                for item in search_results["similar_content"][:2]:
                    if isinstance(item, dict) and "content" in item:
                        context_parts.append(f"- {item['content'][:150]}...")
            
            # Add historical context
            if historical_context:
                context_parts.append(f"Your recent {self.name.lower()} history:")
                for item in historical_context[-2:]:
                    if isinstance(item, dict) and "value" in item:
                        context_parts.append(f"- {item['value'][:150]}...")
            
            # Add domain-specific detection and context
            domain_category = self._detect_domain_category(query)
            if domain_category != "general":
                context_parts.append(f"Detected category: {domain_category}")
            
            # Add domain-specific analysis
            analysis_focus = self._detect_analysis_focus(query)
            if analysis_focus != "general_inquiry":
                context_parts.append(f"Analysis focus: {analysis_focus}")
            
            context = "\n".join(context_parts) if context_parts else ""
            
            # Generate response using your agent's context
            response = self.generate_response_with_context(
                query=query,
                context=context,
                temperature=0.7  # Adjust temperature based on your domain needs
            )
            
            # Store interaction with domain-specific metadata
            self.store_interaction(
                user_id=user_id,
                query=query,
                response=response,
                interaction_type=f"{self.name.lower()}_analysis",
                metadata={
                    "domain_category": domain_category,
                    "analysis_focus": analysis_focus,
                    "context_used": bool(context_parts)
                }
            )
            
            # Store vector embedding for future searches
            self.store_vector_embedding(
                user_id=user_id,
                content=f"{self.name} Query: {query}\nAnalysis: {response}",
                metadata={
                    "agent": self.name,
                    "domain": "[YOUR_DOMAIN_KEY]",  # e.g., "weather_analysis"
                    "category": domain_category,
                    "focus": analysis_focus
                }
            )
            
            return self.format_state_response(
                state=state,
                response=response,
                additional_data={
                    "orchestration": {
                        "strategy": f"{self.name.lower()}_analysis",
                        "selected_agents": [self.name],
                        "domain_category": domain_category,
                        "analysis_focus": analysis_focus,
                        "context_used": bool(context_parts)
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def can_handle(self, query: str) -> float:
        """
        Determine if this agent can handle the query with confidence scoring
        
        Args:
            query: User query string
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = super().can_handle(query)
        query_lower = query.lower()
        
        # High-confidence domain-specific terms
        high_confidence_terms = [
            "[HIGH_CONFIDENCE_TERM_1]",    # e.g., "weather forecast"
            "[HIGH_CONFIDENCE_TERM_2]",    # e.g., "temperature prediction"
            "[HIGH_CONFIDENCE_TERM_3]"     # e.g., "climate analysis"
        ]
        if any(term in query_lower for term in high_confidence_terms):
            base_confidence = min(base_confidence + 0.4, 1.0)
        
        # Medium-confidence terms
        medium_confidence_terms = [
            "[MEDIUM_CONFIDENCE_TERM_1]",  # e.g., "sunny"
            "[MEDIUM_CONFIDENCE_TERM_2]",  # e.g., "rainy"
            "[MEDIUM_CONFIDENCE_TERM_3]"   # e.g., "cold"
        ]
        if any(term in query_lower for term in medium_confidence_terms):
            base_confidence = min(base_confidence + 0.3, 1.0)
        
        # Related activity terms
        activity_terms = [
            "[ACTIVITY_TERM_1]",           # e.g., "outdoor activities"
            "[ACTIVITY_TERM_2]",           # e.g., "vacation planning"
            "[ACTIVITY_TERM_3]"            # e.g., "event planning"
        ]
        if any(term in query_lower for term in activity_terms):
            base_confidence = min(base_confidence + 0.2, 1.0)
        
        return base_confidence
    
    def _detect_domain_category(self, query: str) -> str:
        """
        Detect the specific category within your domain
        
        Args:
            query: User query
            
        Returns:
            Category string
        """
        query_lower = query.lower()
        
        # Define categories specific to your domain
        if any(term in query_lower for term in ["[CATEGORY_1_TERM_1]", "[CATEGORY_1_TERM_2]"]):
            return "[CATEGORY_1]"  # e.g., "short_term_forecast"
        elif any(term in query_lower for term in ["[CATEGORY_2_TERM_1]", "[CATEGORY_2_TERM_2]"]):
            return "[CATEGORY_2]"  # e.g., "long_term_climate"
        elif any(term in query_lower for term in ["[CATEGORY_3_TERM_1]", "[CATEGORY_3_TERM_2]"]):
            return "[CATEGORY_3]"  # e.g., "severe_weather"
        else:
            return "general"
    
    def _detect_analysis_focus(self, query: str) -> str:
        """
        Detect the focus area of the analysis
        
        Args:
            query: User query
            
        Returns:
            Focus area string
        """
        query_lower = query.lower()
        
        # Define focus areas for your domain
        if any(term in query_lower for term in ["[FOCUS_1_TERM_1]", "[FOCUS_1_TERM_2]"]):
            return "[FOCUS_AREA_1]"  # e.g., "forecast_accuracy"
        elif any(term in query_lower for term in ["[FOCUS_2_TERM_1]", "[FOCUS_2_TERM_2]"]):
            return "[FOCUS_AREA_2]"  # e.g., "activity_planning"
        elif any(term in query_lower for term in ["[FOCUS_3_TERM_1]", "[FOCUS_3_TERM_2]"]):
            return "[FOCUS_AREA_3]"  # e.g., "travel_weather"
        else:
            return "general_inquiry"
    
    # Add your domain-specific methods here
    def [YOUR_CUSTOM_METHOD_1](self, [parameters]) -> [return_type]:
        """
        Custom method for your domain-specific functionality
        
        Args:
            [parameters]: Description of parameters
            
        Returns:
            [return_type]: Description of return value
        """
        # Implement your custom logic here
        pass
    
    def [YOUR_CUSTOM_METHOD_2](self, [parameters]) -> [return_type]:
        """
        Another custom method for your domain
        
        Args:
            [parameters]: Description of parameters
            
        Returns:
            [return_type]: Description of return value
        """
        # Implement your custom logic here
        pass
    
    def get_domain_recommendations(self, category: str, context: Dict[str, Any]) -> List[str]:
        """
        Generate domain-specific recommendations
        
        Args:
            category: The detected domain category
            context: Additional context information
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Add category-specific recommendations
        if category == "[CATEGORY_1]":
            recommendations.extend([
                "[RECOMMENDATION_1_FOR_CATEGORY_1]",
                "[RECOMMENDATION_2_FOR_CATEGORY_1]"
            ])
        elif category == "[CATEGORY_2]":
            recommendations.extend([
                "[RECOMMENDATION_1_FOR_CATEGORY_2]",
                "[RECOMMENDATION_2_FOR_CATEGORY_2]"
            ])
        elif category == "[CATEGORY_3]":
            recommendations.extend([
                "[RECOMMENDATION_1_FOR_CATEGORY_3]",
                "[RECOMMENDATION_2_FOR_CATEGORY_3]"
            ])
        
        # Add general recommendations
        recommendations.extend([
            "[GENERAL_RECOMMENDATION_1]",
            "[GENERAL_RECOMMENDATION_2]"
        ])
        
        return recommendations
