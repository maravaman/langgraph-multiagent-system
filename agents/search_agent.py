"""
Search Agent
Specializes in vector-based similarity search for finding similar content 
from user history and providing pattern analysis.
"""

from typing import Dict, Any, List
import logging
import json
from core.base_agent import BaseAgent, GraphState

logger = logging.getLogger(__name__)


class SearchAgent(BaseAgent):
    """Agent specialized in semantic search and pattern analysis"""
    
    def __init__(self, memory_manager=None, name: str = "SearchAgent"):
        super().__init__(memory_manager, name)
        self._description = "Vector-based similarity search agent for history matching and pattern analysis"
        self._capabilities = [
            "semantic_search",
            "pattern_recognition", 
            "similarity_matching",
            "content_analysis",
            "historical_insights",
            "trend_identification"
        ]
    
    @property
    def keywords(self) -> List[str]:
        """Keywords that trigger this agent"""
        return [
            "search", "history", "previous", "before", "recall", "remember",
            "similar", "past", "find", "lookup", "pattern", "trend"
        ]
    
    @property
    def system_prompt(self) -> str:
        """System prompt for this agent"""
        return """You are SearchAgent, specialized in finding similar content from user history and identifying patterns.
        Your capabilities include:
        - Semantic search across all user interactions
        - Pattern recognition in historical data
        - Similarity matching using vector embeddings
        - Content analysis and summarization
        - Trend identification over time
        - Cross-agent search capabilities
        
        Return insights in a structured, analytical format that helps users understand patterns and connections."""
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self._capabilities
    
    def process(self, state: GraphState) -> GraphState:
        """Process search and pattern analysis queries"""
        if not self.validate_state(state):
            return self.handle_error(state, ValueError("Invalid state received"))
        
        query = state.get("question", "")
        user_id = state.get("user_id", 0)
        
        try:
            self.log_processing(query, user_id)
            
            # Perform comprehensive search
            search_results = self._perform_comprehensive_search(query, user_id)
            
            # Analyze patterns in the results
            pattern_analysis = self._analyze_patterns(search_results, query)
            
            # Format response with search insights
            response = self._format_search_response(search_results, pattern_analysis, query)
            
            # Store the search interaction
            self.store_interaction(
                user_id=user_id,
                query=query,
                response=response,
                interaction_type="search_analysis",
                metadata={
                    "search_type": self._detect_search_type(query),
                    "results_count": len(search_results.get("items", []))
                }
            )
            
            return self.format_state_response(
                state=state,
                response=response,
                additional_data={
                    "orchestration": {
                        "strategy": "semantic_search_analysis",
                        "selected_agents": [self.name],
                        "search_type": self._detect_search_type(query),
                        "results_found": len(search_results.get("items", []))
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def can_handle(self, query: str) -> float:
        """
        Determine if this agent can handle the query
        Enhanced logic for search-related detection
        """
        base_confidence = super().can_handle(query)
        
        query_lower = query.lower()
        
        # High-confidence search terms
        high_confidence_terms = ["find similar", "search history", "what did i ask", "previous conversation"]
        if any(term in query_lower for term in high_confidence_terms):
            base_confidence = min(base_confidence + 0.5, 1.0)
        
        # Memory-related terms
        memory_terms = ["remember", "recall", "history", "before", "previous"]
        if any(term in query_lower for term in memory_terms):
            base_confidence = min(base_confidence + 0.3, 1.0)
        
        # Pattern analysis terms
        pattern_terms = ["pattern", "trend", "similar", "like this"]
        if any(term in query_lower for term in pattern_terms):
            base_confidence = min(base_confidence + 0.2, 1.0)
        
        return base_confidence
    
    def _perform_comprehensive_search(self, query: str, user_id: int) -> Dict[str, Any]:
        """Perform comprehensive search across all available data"""
        search_results = {
            "query": query,
            "user_id": user_id,
            "items": [],
            "summary": {},
            "agents_searched": []
        }
        
        try:
            # Search current agent's history
            current_results = self.search_similar_content(query, user_id, limit=10)
            if current_results.get("similar_content"):
                search_results["items"].extend(current_results["similar_content"])
                search_results["agents_searched"].append(self.name)
            
            # Cross-agent search if memory manager supports it
            if hasattr(self.memory, 'search_across_agents'):
                cross_agent_results = self.memory.search_across_agents(user_id, query, limit=15)
                if cross_agent_results:
                    search_results["items"].extend(cross_agent_results)
                    search_results["agents_searched"].append("cross_agent_search")
            
            # Search recent interactions across time
            recent_stm = self.memory.get_recent_stm(user_id, None, hours=48)  # All agents, 48 hours
            recent_ltm = self.memory.get_recent_ltm(user_id, None, days=30)   # All agents, 30 days
            
            # Text-based similarity for recent data
            query_lower = query.lower()
            for item in recent_stm:
                if isinstance(item, str) and query_lower in item.lower():
                    search_results["items"].append({
                        "content": item,
                        "type": "stm",
                        "relevance": item.lower().count(query_lower)
                    })
            
            for item in recent_ltm:
                if isinstance(item, dict) and "value" in item:
                    content = item["value"]
                    if query_lower in content.lower():
                        search_results["items"].append({
                            "content": content,
                            "type": "ltm",
                            "relevance": content.lower().count(query_lower),
                            "timestamp": item.get("timestamp")
                        })
            
            # Remove duplicates and sort by relevance
            unique_items = []
            seen_content = set()
            
            for item in search_results["items"]:
                content = item.get("content", "")[:200]  # First 200 chars for deduplication
                if content not in seen_content:
                    seen_content.add(content)
                    unique_items.append(item)
            
            # Sort by relevance
            unique_items.sort(key=lambda x: x.get("relevance", 0), reverse=True)
            search_results["items"] = unique_items[:20]  # Limit to top 20 results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            search_results["error"] = str(e)
        
        return search_results
    
    def _analyze_patterns(self, search_results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze patterns in search results"""
        pattern_analysis = {
            "themes": [],
            "frequency_analysis": {},
            "temporal_patterns": {},
            "insights": []
        }
        
        items = search_results.get("items", [])
        if not items:
            return pattern_analysis
        
        # Theme analysis
        all_content = " ".join([item.get("content", "") for item in items]).lower()
        
        # Simple keyword frequency (could be enhanced with NLP)
        words = all_content.split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top themes
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        pattern_analysis["themes"] = [word for word, freq in sorted_words if freq > 1]
        
        # Frequency analysis
        pattern_analysis["frequency_analysis"] = {
            "total_matches": len(items),
            "stm_matches": len([item for item in items if item.get("type") == "stm"]),
            "ltm_matches": len([item for item in items if item.get("type") == "ltm"])
        }
        
        # Generate insights
        if pattern_analysis["frequency_analysis"]["total_matches"] > 0:
            pattern_analysis["insights"].append(f"Found {len(items)} relevant items in your history")
            
        if pattern_analysis["themes"]:
            pattern_analysis["insights"].append(f"Common themes: {', '.join(pattern_analysis['themes'][:3])}")
        
        return pattern_analysis
    
    def _format_search_response(self, search_results: Dict[str, Any], pattern_analysis: Dict[str, Any], query: str) -> str:
        """Format the search response in a structured way"""
        
        items = search_results.get("items", [])
        insights = pattern_analysis.get("insights", [])
        
        if not items:
            return f"I searched your history for '{query}' but didn't find any closely matching content. This might be a new topic for you, or you might want to try rephrasing your search."
        
        response_parts = [
            f"🔍 **Search Results for: '{query}'**",
            f"Found {len(items)} relevant items in your history.\n"
        ]
        
        # Add top results
        response_parts.append("**Most Relevant Results:**")
        for i, item in enumerate(items[:5], 1):
            content = item.get("content", "")
            # Truncate long content
            if len(content) > 200:
                content = content[:200] + "..."
            
            item_type = item.get("type", "unknown").upper()
            response_parts.append(f"{i}. [{item_type}] {content}")
        
        # Add pattern insights
        if insights:
            response_parts.append("\n**Pattern Analysis:**")
            for insight in insights:
                response_parts.append(f"• {insight}")
        
        # Add themes if available
        themes = pattern_analysis.get("themes", [])
        if themes:
            response_parts.append(f"\n**Common Themes:** {', '.join(themes[:5])}")
        
        return "\n".join(response_parts)
    
    def _detect_search_type(self, query: str) -> str:
        """Detect the type of search being requested"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["pattern", "trend", "common"]):
            return "pattern_analysis"
        elif any(term in query_lower for term in ["recent", "latest", "new"]):
            return "recent_search"
        elif any(term in query_lower for term in ["similar", "like", "related"]):
            return "similarity_search"
        elif any(term in query_lower for term in ["history", "all", "everything"]):
            return "comprehensive_search"
        else:
            return "general_search"
    
    def search_by_timeframe(self, user_id: int, timeframe: str, query: str = "") -> Dict[str, Any]:
        """Search within specific timeframe"""
        results = {"timeframe": timeframe, "items": []}
        
        if timeframe == "recent":
            items = self.memory.get_recent_stm(user_id, None, hours=24)
        elif timeframe == "week":
            items = self.memory.get_recent_ltm(user_id, None, days=7)
        elif timeframe == "month":
            items = self.memory.get_recent_ltm(user_id, None, days=30)
        else:
            items = []
        
        if query:
            query_lower = query.lower()
            filtered_items = []
            for item in items:
                content = str(item) if not isinstance(item, dict) else item.get("value", "")
                if query_lower in content.lower():
                    filtered_items.append(item)
            results["items"] = filtered_items
        else:
            results["items"] = items
        
        return results
