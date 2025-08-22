"""
Mock Ollama Client for testing without external dependencies
Provides realistic responses for each agent type
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MockOllamaClient:
    """Mock Ollama client that provides realistic responses without external dependencies"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.default_model = "llama3:latest"
        self.timeout = 30
        self.response_templates = self._load_response_templates()
    
    def _load_response_templates(self) -> Dict[str, Dict[str, str]]:
        """Load response templates for different agents"""
        return {
            "WeatherAgent": {
                "default": """🌤️ **Weather Analysis**

Based on your query about weather conditions, here's the current information:

**Current Conditions:**
- Temperature: 22°C (72°F)
- Conditions: Partly cloudy with scattered sunshine
- Humidity: 65%
- Wind: Light breeze from the southwest at 8 km/h
- Visibility: Excellent (10+ km)

**Today's Forecast:**
- High: 26°C (79°F)
- Low: 18°C (64°F)
- Precipitation: 20% chance of light showers in the afternoon
- UV Index: Moderate (5/10)

**Planning Recommendations:**
- Great weather for outdoor activities
- Light jacket recommended for evening
- Sunscreen advised for extended outdoor exposure
- Perfect conditions for sightseeing and photography

**Activity Impact:**
- Excellent for hiking and outdoor dining
- Good visibility for scenic photography
- Comfortable temperatures for walking tours""",
                
                "forecast": """📅 **Weather Forecast**

Here's your extended weather outlook:

**Next 3 Days:**
- **Today:** Partly cloudy, 22°C/18°C, 20% rain chance
- **Tomorrow:** Mostly sunny, 25°C/19°C, 10% rain chance  
- **Day After:** Sunny intervals, 24°C/17°C, 15% rain chance

**Weekly Trend:**
- Generally pleasant conditions with temperatures in the low-mid 20s°C
- Minimal rainfall expected
- Light to moderate winds
- Good air quality

**Best Times for Activities:**
- Morning (8-11 AM): Cool and fresh, perfect for hiking
- Afternoon (2-5 PM): Warmest period, ideal for sightseeing
- Evening (6-8 PM): Pleasant temperatures for outdoor dining"""
            },
            
            "DiningAgent": {
                "default": """🍽️ **Dining Recommendations**

Based on your culinary preferences, here are excellent dining options:

**Recommended Restaurants:**

**1. The Garden Bistro** ⭐⭐⭐⭐⭐
- **Cuisine:** Contemporary European with local influences
- **Ambiance:** Elegant outdoor garden setting with string lights
- **Specialties:** Seasonal tasting menu, locally-sourced ingredients
- **Price Range:** $$$ (Fine dining)
- **Best For:** Romantic dinners, special occasions

**2. Coastal Kitchen** ⭐⭐⭐⭐
- **Cuisine:** Fresh seafood and Mediterranean
- **Ambiance:** Casual waterfront dining with scenic views
- **Specialties:** Daily catch, wood-fired dishes, craft cocktails
- **Price Range:** $$ (Moderate)
- **Best For:** Family meals, casual dining with a view

**3. Local Harvest Café** ⭐⭐⭐⭐
- **Cuisine:** Farm-to-table, vegetarian-friendly
- **Ambiance:** Cozy, rustic interior with community tables
- **Specialties:** Organic salads, artisanal breads, local wines
- **Price Range:** $ (Casual)
- **Best For:** Healthy lunch options, coffee meetings

**Weather Considerations:**
- Perfect weather for outdoor dining at The Garden Bistro
- Coastal Kitchen's terrace will be ideal in these conditions
- All venues have both indoor and outdoor seating options

**Local Food Culture:**
- Emphasis on fresh, seasonal ingredients
- Strong farm-to-table movement
- Excellent local wine and craft beer scene""",
                
                "cuisine": """🌮 **Cuisine Analysis**

Exploring the rich culinary landscape:

**Local Specialties:**
- Fresh seafood from nearby waters
- Seasonal produce from local farms  
- Traditional cooking methods with modern twists
- Artisanal breads and pastries

**Must-Try Dishes:**
1. **Locally-caught Fish** - Prepared with herbs and citrus
2. **Seasonal Vegetable Tart** - Using market-fresh ingredients
3. **Artisan Cheese Board** - Featuring regional varieties
4. **Traditional Stew** - Slow-cooked with local spices

**Dining Experiences:**
- **Fine Dining:** Multi-course tasting menus with wine pairings
- **Casual:** Bistro-style meals with shared plates
- **Street Food:** Local food trucks and market stalls
- **Cafés:** Artisanal coffee with homemade pastries"""
            },
            
            "ScenicLocationFinderAgent": {
                "default": """🏔️ **Scenic Location Recommendations**

Discover breathtaking destinations perfect for your visit:

**Top Scenic Locations:**

**1. Sunset Point Overlook** 🌅
- **Type:** Mountain viewpoint with panoramic vistas
- **Best Time:** Golden hour (1 hour before sunset)
- **Features:** 360-degree views, photography platform, picnic area
- **Access:** 15-minute uphill walk, moderate difficulty
- **Special:** Famous for spectacular sunrise and sunset views

**2. Crystal Lake Trail** 💎
- **Type:** Alpine lake surrounded by forest
- **Distance:** 3km loop trail (1.5 hours)
- **Features:** Clear mountain lake, wildlife viewing, peaceful setting
- **Difficulty:** Easy to moderate, family-friendly
- **Season:** Best visited spring through fall

**3. Heritage Village Lookout** 🏘️
- **Type:** Historic town overview with cultural significance
- **Features:** Traditional architecture, cultural center, artisan shops
- **Access:** Walking distance from town center
- **Activities:** Guided tours, photography, souvenir shopping

**Photography Tips:**
- Golden hour lighting (sunrise/sunset) for best shots
- Bring polarizing filter for lake reflections
- Weather conditions perfect for clear, crisp photos

**Weather Integration:**
- Current conditions ideal for all recommended locations
- Clear visibility enhances scenic views
- Comfortable temperatures for hiking and exploration""",
                
                "mountain": """⛰️ **Mountain Destinations**

Spectacular mountain experiences await:

**Premier Mountain Locations:**

**1. Eagle's Peak Summit**
- **Elevation:** 1,247m above sea level
- **Trail:** 4.2km to summit (2-3 hours)
- **Difficulty:** Moderate to challenging
- **Rewards:** Breathtaking 360-degree panoramic views
- **Wildlife:** Eagles, mountain goats, alpine flowers

**2. Pine Ridge Trail**
- **Type:** Scenic ridge walk through pine forests
- **Length:** 6km linear trail
- **Features:** Forest canopy, mountain streams, wildflower meadows
- **Best Season:** Late spring to early fall

**Safety & Preparation:**
- Weather conditions currently favorable
- Bring layers for temperature changes with elevation
- Adequate water and snacks recommended
- Trail maps available at visitor center"""
            },
            
            "ForestAnalyzerAgent": {
                "default": """🌲 **Forest Ecosystem Analysis**

Comprehensive analysis of forest environments and biodiversity:

**Ecosystem Overview:**
- **Forest Type:** Temperate mixed deciduous-coniferous forest
- **Dominant Species:** Oak, maple, pine, and fir trees
- **Canopy Coverage:** Dense (75-85% coverage)
- **Age Structure:** Mature forest with trees 50-150 years old

**Biodiversity Assessment:**
- **Flora:** 150+ plant species including rare understory plants
- **Fauna:** Home to deer, foxes, various bird species, and small mammals
- **Ecological Health:** Excellent - stable ecosystem with natural regeneration

**Conservation Status:**
- **Protection Level:** Well-preserved with active management
- **Threats:** Minimal - controlled access and protection measures
- **Management:** Sustainable forestry practices in designated areas

**Seasonal Characteristics:**
- **Spring:** Wildflower blooms, bird migration, new growth
- **Summer:** Full canopy, active wildlife, optimal biodiversity
- **Fall:** Spectacular foliage, seed dispersal, preparation for winter
- **Winter:** Dormant period, easier wildlife tracking, snow sports

**Visitor Recommendations:**
- **Best Times:** Early morning or late afternoon for wildlife viewing
- **Activities:** Nature photography, bird watching, forest bathing
- **Educational:** Guided nature walks available
- **Sustainability:** Follow Leave No Trace principles

**Current Conditions:**
- Weather ideal for forest exploration
- Active wildlife due to favorable conditions
- Excellent visibility through forest canopy""",
                
                "conservation": """🌿 **Conservation Analysis**

Forest conservation and environmental protection status:

**Conservation Efforts:**
- **Protected Status:** Designated nature reserve with strict guidelines
- **Management Plan:** 20-year sustainable forest management strategy
- **Restoration Projects:** Ongoing native species reintroduction

**Environmental Impact:**
- **Carbon Sequestration:** Significant CO2 absorption capacity
- **Water Cycle:** Critical watershed protection role
- **Biodiversity:** Habitat for endangered and threatened species

**Community Involvement:**
- Volunteer restoration programs
- Educational outreach initiatives
- Sustainable tourism practices"""
            },
            
            "SearchAgent": {
                "default": """🔍 **Search Analysis Results**

Based on your query, here's what I found in your interaction history:

**Search Summary:**
- **Query Processed:** Successfully analyzed your request
- **Historical Matches:** Found 3 relevant previous interactions
- **Pattern Recognition:** Identified recurring interests in outdoor activities

**Relevant Previous Interactions:**
1. **Recent Query:** "Best hiking trails in the area" (3 days ago)
   - **Context:** Similar interest in outdoor exploration
   - **Relevance:** High - matches current scenic location interest

2. **Related Search:** "Weather for weekend activities" (1 week ago)
   - **Context:** Weather planning for outdoor activities
   - **Relevance:** Medium - shows consistent weather consideration

3. **Historical Interest:** "Local restaurant recommendations" (2 weeks ago)
   - **Context:** Dining preferences in the same area
   - **Relevance:** Medium - indicates local area familiarity

**Pattern Analysis:**
- **Primary Interests:** Outdoor activities, scenic locations, weather planning
- **Geographic Focus:** Local area exploration and tourism
- **Planning Approach:** Comprehensive trip planning including multiple aspects

**Insights & Recommendations:**
- You consistently plan outdoor activities with weather considerations
- Interest in combining scenic locations with dining experiences
- Preference for local, authentic experiences over tourist traps
- Historical satisfaction with nature-based activities

**Connection to Current Query:**
Your current question aligns perfectly with your established interests in comprehensive trip planning that combines scenic locations, weather awareness, and quality dining experiences."""
            }
        }
    
    def is_available(self) -> bool:
        """Always return True for mock client"""
        return True
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Return mock model list"""
        return [
            {"name": "llama3:latest", "size": "4.7GB"},
            {"name": "mistral:latest", "size": "4.1GB"}
        ]
    
    def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None, 
        system_prompt: Optional[str] = None,
        context: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate mock response based on agent type and query"""
        try:
            # Determine agent type from system prompt
            agent_type = self._identify_agent_type(system_prompt or "", prompt)
            
            # Get appropriate template
            templates = self.response_templates.get(agent_type, {})
            
            # Choose specific template based on query content
            template_key = self._choose_template_key(prompt, templates)
            
            response = templates.get(template_key, templates.get("default", "Mock response generated successfully."))
            
            logger.info(f"Mock response generated for {agent_type}")
            return response
            
        except Exception as e:
            logger.error(f"Mock response generation error: {e}")
            return f"Mock response for query: {prompt[:100]}..."
    
    def _identify_agent_type(self, system_prompt: str, prompt: str) -> str:
        """Identify agent type from system prompt and query content"""
        system_lower = system_prompt.lower()
        prompt_lower = prompt.lower()
        
        if "weather" in system_lower or any(word in prompt_lower for word in ["weather", "temperature", "forecast", "climate"]):
            return "WeatherAgent"
        elif "dining" in system_lower or any(word in prompt_lower for word in ["restaurant", "food", "dining", "cuisine"]):
            return "DiningAgent"
        elif "scenic" in system_lower or any(word in prompt_lower for word in ["scenic", "location", "destination", "tourist"]):
            return "ScenicLocationFinderAgent"
        elif "forest" in system_lower or any(word in prompt_lower for word in ["forest", "ecosystem", "conservation", "biodiversity"]):
            return "ForestAnalyzerAgent"
        elif "search" in system_lower or any(word in prompt_lower for word in ["search", "history", "previous", "similar"]):
            return "SearchAgent"
        else:
            return "ScenicLocationFinderAgent"  # Default
    
    def _choose_template_key(self, prompt: str, templates: Dict[str, str]) -> str:
        """Choose specific template based on prompt content"""
        prompt_lower = prompt.lower()
        
        if "forecast" in prompt_lower and "WeatherAgent" in str(templates):
            return "forecast"
        elif "cuisine" in prompt_lower and "DiningAgent" in str(templates):
            return "cuisine"
        elif "mountain" in prompt_lower and "ScenicLocationFinderAgent" in str(templates):
            return "mountain"
        elif "conservation" in prompt_lower and "ForestAnalyzerAgent" in str(templates):
            return "conservation"
        else:
            return "default"

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Mock chat completion"""
        if messages:
            last_message = messages[-1].get('content', '')
            return self.generate_response(last_message)
        return "Mock chat completion response"

    def generate_embedding(self, text: str, model: str = "nomic-embed-text") -> List[float]:
        """Generate mock embeddings"""
        # Return mock embedding vector
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        # Convert hash to numbers and normalize to create mock embedding
        return [int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, min(32, len(hash_hex)), 2)]

class MockAgentPromptManager:
    """Mock prompt manager that works with the mock client"""
    
    def __init__(self):
        self.agent_prompts = {
            "SearchAgent": {
                "system": "You are a search agent specialized in finding similar content from user history.",
                "template": "Based on the user's history, find content similar to: {query}\n\nHistory context:\n{context}"
            },
            "ScenicLocationFinder": {
                "system": "You are a scenic location finding agent. You help users discover beautiful, interesting, and scenic places.",
                "template": "Help find scenic locations based on: {query}\n\nContext: {context}"
            },
            "ForestAnalyzer": {
                "system": "You are a forest analysis agent specializing in forest ecology, conservation, and forest-related information.",
                "template": "Analyze forest-related query: {query}\n\nContext: {context}"
            },
            "WeatherAgent": {
                "system": "You are WeatherAgent, a specialized weather analysis assistant. Provide accurate weather information.",
                "template": "Weather Query: {query}\n\nContext: {context}"
            },
            "DiningAgent": {
                "system": "You are DiningAgent, a culinary and restaurant specialist. Provide excellent dining recommendations.",
                "template": "Dining Query: {query}\n\nContext: {context}"
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

# Global mock instances
mock_ollama_client = MockOllamaClient()
mock_prompt_manager = MockAgentPromptManager()
