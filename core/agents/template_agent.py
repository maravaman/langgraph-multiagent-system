"""
Template Agent - Example for creating new agents
Constraint: Template showing how to easily create new agents inheriting from BaseAgent
This template demonstrates the standard structure for all new agents
"""
import logging
from typing import Dict, Any, List
from ..base_agent import BaseAgent, GraphState
from ..memory import MemoryManager

logger = logging.getLogger(__name__)

class TemplateAgent(BaseAgent):
    """
    Template agent showing the standard structure for creating new agents
    Replace 'Template' with your agent's specific name and functionality
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize TemplateAgent with memory management and search capabilities
        
        Args:
            memory_manager: MemoryManager instance for STM and LTM operations
        """
        super().__init__(memory_manager, "TemplateAgent")
        
        # Override base capabilities with agent-specific ones
        self._capabilities = [
            "template_functionality",  # Replace with actual capabilities
            "example_processing",      # Add your agent's specific abilities
            "demonstration_features"   # List all key features your agent provides
        ]
        
        # Describe what your agent does
        self._description = "Template agent demonstrating the standard structure for creating new agents with memory management and search"
        
        logger.info("TemplateAgent initialized with enhanced memory management and search capabilities")
    
    def process(self, state: GraphState) -> GraphState:
        """
        Main processing method - implement your agent's core functionality here
        
        Args:
            state: Current GraphState containing user query and context
            
        Returns:
            Updated GraphState with your agent's response
        """
        # Step 1: Validate incoming state (inherited from BaseAgent)
        if not self.validate_state(state):
            return self.handle_error(state, Exception("Invalid state provided"))
        
        # Step 2: Extract query and user information
        query = state.get("question", "")
        user_id = state.get("user_id", 0)
        
        # Step 3: Log processing activity (inherited from BaseAgent)
        self.log_processing(query, user_id)
        
        try:
            # Step 4: Search for relevant content in memory (inherited from BaseAgent)
            search_results = self.search_similar_content(query, user_id)
            
            # Step 5: Get historical context if needed (inherited from BaseAgent)
            historical_context = self.get_historical_context(user_id, days=30)
            
            # Step 6: Build context for your specific agent processing
            context = self._build_agent_context(query, search_results, historical_context)
            
            # Step 7: Generate response using LLM or fallback (inherited from BaseAgent)
            if hasattr(self, 'generate_response_with_context'):
                response = self.generate_response_with_context(
                    query=query,
                    context=context,
                    temperature=0.7  # Adjust temperature based on your needs
                )
            else:
                response = self._generate_fallback_response(query, context)
            
            # Step 8: Enhance response with agent-specific formatting
            enhanced_response = self._enhance_agent_response(response, query)
            
            # Step 9: Store interaction using inherited memory management
            self.store_interaction(
                user_id=user_id,
                query=query,
                response=enhanced_response,
                interaction_type='template_processing',  # Replace with your interaction type
                metadata={
                    "processing_type": "template_example",  # Add relevant metadata
                    "features_used": self._extract_features_used(query),
                    "similar_queries": len(search_results.get("similar_content", []))
                }
            )
            
            # Step 10: Store as vector embedding for future searches (inherited from BaseAgent)
            self.store_vector_embedding(
                user_id=user_id,
                content=f"Template processing: {query}",  # Customize the content description
                metadata={
                    "type": "template_query",  # Replace with your content type
                    "features": self._extract_features_used(query)
                }
            )
            
            # Step 11: Return formatted state response (inherited from BaseAgent)
            return self.format_state_response(
                state,
                enhanced_response,
                {"processing_type": "template_example"}  # Add any additional state data
            )
            
        except Exception as e:
            logger.error(f"Error in TemplateAgent processing: {e}")
            return self.handle_error(state, e)  # Inherited error handling
    
    def get_capabilities(self) -> List[str]:
        """
        Return agent capabilities (required by BaseAgent)
        
        Returns:
            List of TemplateAgent capabilities
        """
        return self._capabilities
    
    # PRIVATE METHODS - Implement your agent-specific logic here
    
    def _build_agent_context(self, query: str, search_results: Dict, historical_context: List) -> str:
        """
        Build context specific to your agent's processing needs
        
        Args:
            query: User's query
            search_results: Similar content from memory
            historical_context: Previous interactions
            
        Returns:
            Formatted context string for your agent
        """
        context_parts = []
        
        # Add similar content from memory
        if search_results.get("similar_content"):
            context_parts.append("Similar content found:")
            for item in search_results["similar_content"][:3]:
                content = item.get('content', '')[:150]
                context_parts.append(f"- {content}")
        
        # Add historical context if relevant
        if historical_context:
            context_parts.append("Previous interactions:")
            for interaction in historical_context[:2]:
                input_text = interaction.get('input_text', '')[:100]
                context_parts.append(f"- Previous query: {input_text}")
        
        # Add agent-specific processing guidelines
        context_parts.extend([
            "",
            "Template Processing Guidelines:",  # Replace with your guidelines
            "- Process user queries according to agent specialty",
            "- Provide informative and helpful responses",
            "- Use memory and search capabilities effectively",
            "- Follow consistent formatting and structure"
        ])
        
        return "\n".join(context_parts)
    
    def _generate_fallback_response(self, query: str, context: str) -> str:
        """
        Generate fallback response when LLM is not available
        Customize this for your agent's specific functionality
        
        Args:
            query: User query
            context: Processing context
            
        Returns:
            Fallback response for your agent
        """
        response_parts = []
        
        # Add agent-specific header
        response_parts.append("🤖 Template Agent Processing:")
        
        # Analyze query for specific features (customize for your agent)
        query_lower = query.lower()
        
        if "example" in query_lower:
            response_parts.append("📋 Example Processing: This demonstrates how template agents handle example queries.")
        
        if "help" in query_lower or "how" in query_lower:
            response_parts.append("❓ Help Information: Template agents provide assistance based on their specialized capabilities.")
        
        if "process" in query_lower:
            response_parts.append("⚙️ Processing Features: Template agents use memory management and search capabilities.")
        
        # Add general processing information
        if len(response_parts) == 1:  # Only header added
            response_parts.append("Template agent provides specialized processing with memory management and search capabilities.")
        
        # Add note about enhanced functionality
        response_parts.append("\n💡 For enhanced responses with AI processing, ensure Ollama is running.")
        
        return "\n\n".join(response_parts)
    
    def _enhance_agent_response(self, response: str, query: str) -> str:
        """
        Enhance response with agent-specific formatting
        Customize this for your agent's presentation style
        
        Args:
            response: Generated response
            query: Original query
            
        Returns:
            Enhanced response with agent formatting
        """
        enhanced_parts = [f"🤖 **Template Agent Response** 🤖\n"]  # Replace icon and title
        
        enhanced_parts.append(f"**Processing Result**: {response}\n")
        
        # Add agent-specific features summary
        features_used = self._extract_features_used(query)
        if features_used:
            enhanced_parts.append(f"**Features Used**: {', '.join(features_used)}\n")
        
        # Add agent-specific tips or information
        enhanced_parts.append("**Template Agent Tips:**")  # Replace with your agent's tips
        enhanced_parts.append("- Leverage memory for context-aware responses")
        enhanced_parts.append("- Use search capabilities for relevant information")
        enhanced_parts.append("- Provide consistent and helpful interactions\n")
        
        enhanced_parts.append("**Template Agent** | Demonstrating standardized agent architecture")  # Replace with your agent description
        
        return "\n".join(enhanced_parts)
    
    def _extract_features_used(self, query: str) -> List[str]:
        """
        Extract which agent features were used in processing
        Customize this for your agent's specific features
        
        Args:
            query: User query
            
        Returns:
            List of features used in processing
        """
        query_lower = query.lower()
        features = []
        
        # Define feature keywords for your agent (customize this)
        feature_keywords = {
            "template_processing": ["template", "example", "demo"],
            "help_features": ["help", "how", "what", "explain"],
            "memory_usage": ["remember", "previous", "history", "before"],
            "search_functionality": ["find", "search", "similar", "related"]
        }
        
        for feature, keywords in feature_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                features.append(feature)
        
        return features if features else ["general_processing"]
    
    # PUBLIC METHODS - Add agent-specific functionality here
    
    def custom_agent_method(self, parameter: str, user_id: int) -> Dict[str, Any]:
        """
        Example of custom agent-specific method
        Replace this with methods specific to your agent's functionality
        
        Args:
            parameter: Custom parameter for your method
            user_id: User identifier
            
        Returns:
            Results specific to your agent's functionality
        """
        try:
            # Use inherited memory and search capabilities
            search_results = self.search_similar_content(parameter, user_id)
            
            # Process according to your agent's logic
            result = {
                "agent": self.name,
                "parameter": parameter,
                "user_id": user_id,
                "search_results": search_results.get("similar_content", []),
                "custom_processing": "Template agent custom method executed successfully"
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Custom agent method failed: {e}")
            return {"error": str(e), "agent": self.name}
    
    def analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """
        Example analysis method
        Replace with methods that make sense for your agent
        
        Args:
            query: User query to analyze
            
        Returns:
            Analysis results
        """
        try:
            query_lower = query.lower()
            
            # Simple complexity analysis (customize for your agent)
            complexity_indicators = {
                "word_count": len(query.split()),
                "question_words": len([w for w in query_lower.split() if w in ['what', 'how', 'when', 'where', 'why', 'who']]),
                "complexity_level": "high" if len(query.split()) > 20 else "medium" if len(query.split()) > 10 else "simple"
            }
            
            return {
                "analysis": complexity_indicators,
                "agent": self.name,
                "query": query
            }
            
        except Exception as e:
            logger.warning(f"Query complexity analysis failed: {e}")
            return {"error": str(e), "agent": self.name}

# INSTRUCTIONS FOR CREATING NEW AGENTS:
#
# 1. Copy this template file to a new file: your_agent_name_agent.py
# 2. Replace "TemplateAgent" with "YourAgentNameAgent"
# 3. Update the capabilities list with your agent's specific abilities
# 4. Modify the description to reflect your agent's purpose
# 5. Customize the processing logic in the process() method
# 6. Update the fallback response generation for your agent's domain
# 7. Enhance the response formatting to match your agent's style
# 8. Add any custom methods your agent needs
# 9. Update the feature extraction logic for your domain
# 10. Test your agent and register it in the system
#
# Your agent will automatically inherit:
# - Memory management (STM and LTM)
# - Vector similarity search
# - Cross-agent search capabilities
# - Error handling and logging
# - State validation and formatting
# - LLM integration when available
#
# This makes adding new agents fast, consistent, and maintainable!
