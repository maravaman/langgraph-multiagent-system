"""
Ollama integration for local LLM responses
"""
import requests
import json
import logging
import os
from typing import Dict, List, Optional, Any

# Try to import decouple, fallback to os.getenv
try:
    from decouple import config
except ImportError:
    def config(key, default=None, cast=None):
        value = os.getenv(key, default)
        if cast and value is not None:
            return cast(value)
        return value

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with local Ollama server"""
    
    def __init__(self):
        self.base_url = config('OLLAMA_BASE_URL', default='http://localhost:11434')
        self.default_model = config('OLLAMA_DEFAULT_MODEL', default='llama3:latest')
        # Force higher timeout for agent processing
        self.timeout = config('OLLAMA_TIMEOUT', default=120, cast=int)
    
    def is_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama server not available: {e}")
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            return response.json().get('models', [])
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None, 
        system_prompt: Optional[str] = None,
        context: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate response from Ollama model"""
        try:
            model = model or self.default_model
            max_tokens = max_tokens or config('OLLAMA_MAX_TOKENS', default=1000, cast=int)
            temperature = temperature or config('OLLAMA_TEMPERATURE', default=0.7, cast=float)
            
            # Prepare the prompt with context if provided
            full_prompt = prompt
            if context:
                context_str = "\n".join(context)
                full_prompt = f"Context:\n{context_str}\n\nQuery: {prompt}"
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', 'No response generated')
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "Request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return f"Error generating response: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "An unexpected error occurred."
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Chat completion with message history"""
        try:
            model = model or self.default_model
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('message', {}).get('content', 'No response generated')
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            return f"Error in chat completion: {str(e)}"

    def generate_embedding(self, text: str, model: str = "nomic-embed-text") -> List[float]:
        """Generate embeddings for text using Ollama"""
        try:
            payload = {
                "model": model,
                "prompt": text
            }
            
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('embedding', [])
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

class AgentPromptManager:
    """Manages prompts and system messages for different agents"""
    
    def __init__(self):
        self.agent_prompts = {
            "SearchAgent": {
                "system": """You are a search agent specialized in finding similar content from user history.
                Analyze the query and find the most relevant historical interactions.
                Always return responses in valid JSON format with similarity scores.""",
                "template": """Based on the user's history, find content similar to: {query}
                
                History context:
                {context}
                
                Return a JSON response with relevant matches and similarity explanations."""
            },
            
            "ScenicLocationFinder": {
                "system": """You are a scenic location finding agent. You help users discover beautiful, 
                interesting, and scenic places based on their preferences and queries.""",
                "template": """Help find scenic locations based on: {query}
                
                Consider factors like:
                - Natural beauty and landscapes
                - Accessibility and safety
                - Season and weather considerations
                - User preferences from context: {context}
                
                Provide detailed recommendations with practical information."""
            },
            
            "ForestAnalyzer": {
                "system": """You are a forest analysis agent specializing in forest ecology, 
                conservation, and forest-related information.""",
                "template": """Analyze forest-related query: {query}
                
                Context from previous interactions: {context}
                
                Provide detailed analysis covering:
                - Ecosystem characteristics
                - Biodiversity considerations
                - Conservation status
                - Management recommendations if applicable"""
            },
            
            "WaterBodyAnalyzer": {
                "system": """You are a water body analysis agent specializing in hydrology, 
                water quality, and aquatic ecosystems.""",
                "template": """Analyze water body related query: {query}
                
                Previous context: {context}
                
                Cover aspects like:
                - Hydrological characteristics
                - Water quality parameters
                - Aquatic ecosystem health
                - Environmental factors and impacts"""
            },
            
            "OrchestratorAgent": {
                "system": """You are an orchestrator agent that routes queries to appropriate specialist agents.
                Analyze the query and determine which agents should handle it.""",
                "template": """Analyze this query for routing: {query}
                
                Available agents and their capabilities:
                - SearchAgent: Similarity search in user history
                - ScenicLocationFinder: Finding beautiful locations
                - ForestAnalyzer: Forest ecology and analysis
                - WaterBodyAnalyzer: Water bodies and hydrology
                
                Determine which agent(s) should handle this query and why.
                Return routing decision as JSON."""
            }
        }
    
    def get_prompt(self, agent_name: str, query: str, context: str = "") -> Dict[str, str]:
        """Get formatted prompt for an agent"""
        if agent_name not in self.agent_prompts:
            agent_name = "ScenicLocationFinder"  # Default fallback
        
        agent_config = self.agent_prompts[agent_name]
        formatted_prompt = agent_config["template"].format(
            query=query, 
            context=context or "No previous context available"
        )
        
        return {
            "system": agent_config["system"],
            "prompt": formatted_prompt
        }

# Global instances
ollama_client = OllamaClient()
prompt_manager = AgentPromptManager()
