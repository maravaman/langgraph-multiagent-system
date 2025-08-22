"""
Forest Analyzer Agent
Specializes in analyzing forest ecosystems, biodiversity, conservation status,
and providing scientific insights with practical recommendations.
"""

from typing import Dict, Any, List
import logging
from core.base_agent import BaseAgent, GraphState

logger = logging.getLogger(__name__)


class ForestAnalyzerAgent(BaseAgent):
    """Agent specialized in forest ecosystem analysis and recommendations"""
    
    def __init__(self, memory_manager=None, name: str = "ForestAnalyzer"):
        super().__init__(memory_manager, name)
        self._description = "Forest ecosystem analysis agent providing scientific insights and conservation recommendations"
        self._capabilities = [
            "forest_ecosystem_analysis",
            "biodiversity_assessment",
            "conservation_recommendations",
            "wildlife_identification",
            "ecological_research_support",
            "forest_management_advice"
        ]
    
    @property
    def keywords(self) -> List[str]:
        """Keywords that trigger this agent"""
        return [
            "forest", "tree", "woodland", "ecosystem", "biodiversity",
            "conservation", "wildlife", "nature", "jungle", "rainforest",
            "deforestation", "species", "habitat", "flora", "fauna"
        ]
    
    @property
    def system_prompt(self) -> str:
        """System prompt for this agent"""
        return """You are ForestAnalyzer, an expert forest ecologist and conservation scientist.
        Analyze forest ecosystems and provide insights about:
        - Biodiversity and species composition
        - Ecosystem health and conservation status
        - Threats and conservation challenges
        - Wildlife habitats and corridors
        - Sustainable forest management practices
        - Scientific research findings and recommendations
        
        Provide scientifically accurate information while making it accessible to various audiences."""
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self._capabilities
    
    def process(self, state: GraphState) -> GraphState:
        """Process forest-related queries"""
        if not self.validate_state(state):
            return self.handle_error(state, ValueError("Invalid state received"))
        
        query = state.get("question", "")
        user_id = state.get("user_id", 0)
        
        try:
            self.log_processing(query, user_id)
            
            # Search for similar past queries
            search_results = self.search_similar_content(query, user_id, limit=3)
            
            # Get historical context for forest-related discussions
            historical_context = self.get_historical_context(user_id, days=7)
            
            # Build context from search results and historical data
            context_parts = []
            if search_results.get("similar_content"):
                context_parts.append("Previous forest-related discussions:")
                for item in search_results["similar_content"][:2]:
                    if isinstance(item, dict) and "content" in item:
                        context_parts.append(f"- {item['content'][:150]}...")
            
            if historical_context:
                context_parts.append("Your forest research history:")
                for item in historical_context[-2:]:
                    if isinstance(item, dict) and "value" in item:
                        context_parts.append(f"- {item['value'][:150]}...")
            
            context = "\n".join(context_parts) if context_parts else ""
            
            # Generate response using specialized forest knowledge
            response = self.generate_response_with_context(
                query=query,
                context=context,
                temperature=0.6  # Slightly lower temperature for more factual responses
            )
            
            # Store the interaction with forest-specific metadata
            self.store_interaction(
                user_id=user_id,
                query=query,
                response=response,
                interaction_type="forest_analysis",
                metadata={"analysis_type": self._detect_analysis_type(query)}
            )
            
            # Store vector embedding for future forest research
            self.store_vector_embedding(
                user_id=user_id,
                content=f"Forest Analysis Query: {query}\nAnalysis: {response}",
                metadata={
                    "agent": self.name, 
                    "domain": "forest_ecology",
                    "analysis_type": self._detect_analysis_type(query)
                }
            )
            
            return self.format_state_response(
                state=state,
                response=response,
                additional_data={
                    "orchestration": {
                        "strategy": "forest_ecosystem_analysis",
                        "selected_agents": [self.name],
                        "analysis_type": self._detect_analysis_type(query),
                        "context_used": bool(context_parts)
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def can_handle(self, query: str) -> float:
        """
        Determine if this agent can handle the query
        Enhanced logic for forest-related detection
        """
        base_confidence = super().can_handle(query)
        
        query_lower = query.lower()
        
        # High-confidence forest terms
        high_confidence_terms = ["forest ecosystem", "biodiversity", "conservation", "deforestation"]
        if any(term in query_lower for term in high_confidence_terms):
            base_confidence = min(base_confidence + 0.4, 1.0)
        
        # Species and wildlife terms
        species_terms = ["species", "wildlife", "habitat", "flora", "fauna"]
        if any(term in query_lower for term in species_terms):
            base_confidence = min(base_confidence + 0.3, 1.0)
        
        # Scientific research terms
        research_terms = ["research", "study", "analysis", "ecological"]
        if any(term in query_lower for term in research_terms):
            base_confidence = min(base_confidence + 0.2, 1.0)
        
        return base_confidence
    
    def _detect_analysis_type(self, query: str) -> str:
        """Detect the type of forest analysis requested"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["biodiversity", "species", "flora", "fauna"]):
            return "biodiversity_analysis"
        elif any(term in query_lower for term in ["conservation", "protection", "threat"]):
            return "conservation_assessment"
        elif any(term in query_lower for term in ["ecosystem", "ecological", "environment"]):
            return "ecosystem_analysis"
        elif any(term in query_lower for term in ["management", "sustainable", "forestry"]):
            return "forest_management"
        else:
            return "general_forest_inquiry"
    
    def analyze_forest_health(self, forest_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze forest health based on provided data
        
        Args:
            forest_data: Dictionary containing forest metrics
            
        Returns:
            Dictionary with health assessment
        """
        health_assessment = {
            "overall_health": "unknown",
            "key_indicators": [],
            "recommendations": [],
            "concerns": []
        }
        
        # This would integrate with real forest data APIs or databases
        # For now, provide a template structure
        
        if "tree_cover" in forest_data:
            tree_cover = forest_data["tree_cover"]
            if tree_cover > 0.8:
                health_assessment["key_indicators"].append("High tree cover percentage")
            elif tree_cover < 0.3:
                health_assessment["concerns"].append("Low tree cover indicates degradation")
        
        return health_assessment
    
    def get_conservation_recommendations(self, forest_type: str, threats: List[str]) -> List[str]:
        """
        Get conservation recommendations for specific forest types and threats
        
        Args:
            forest_type: Type of forest (tropical, temperate, boreal, etc.)
            threats: List of identified threats
            
        Returns:
            List of conservation recommendations
        """
        recommendations = []
        
        # Base recommendations by forest type
        if forest_type.lower() == "tropical":
            recommendations.extend([
                "Establish protected corridors between forest fragments",
                "Implement community-based forest management",
                "Monitor illegal logging activities"
            ])
        elif forest_type.lower() == "temperate":
            recommendations.extend([
                "Maintain diverse age structure in forest stands",
                "Control invasive species populations",
                "Implement sustainable harvesting practices"
            ])
        
        # Threat-specific recommendations
        for threat in threats:
            if "logging" in threat.lower():
                recommendations.append("Strengthen law enforcement against illegal logging")
            elif "fire" in threat.lower():
                recommendations.append("Develop fire management and prevention strategies")
            elif "invasive" in threat.lower():
                recommendations.append("Implement invasive species control programs")
        
        return list(set(recommendations))  # Remove duplicates
