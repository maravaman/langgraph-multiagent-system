# 🤖 **Agent Creation Guide**

## Quick Start Guide for Creating Custom Agents

This guide will help you create powerful custom agents for the multi-agent system using the provided template.

---

## 📋 **Prerequisites**

✅ **Basic Python Knowledge**  
✅ **Understanding of your domain/expertise area**  
✅ **Template file**: `templates/sample_agent_template.py`  

---

## 🚀 **Step-by-Step Creation Process**

### **Step 1: Copy the Template**

```bash
# Copy the template to create your agent
cp templates/sample_agent_template.py agents/your_agent_name.py
```

### **Step 2: Replace All Placeholders**

Open your new agent file and replace all `[PLACEHOLDER]` values:

#### **🎯 Basic Information**
- `[YOUR_AGENT_NAME]` → Your agent class name (e.g., `WeatherAnalyzer`)
- `[YOUR_DOMAIN_NAME]` → Domain description (e.g., "Weather Analysis")
- `[YOUR_DOMAIN_DESCRIPTION]` → What your agent specializes in
- `[BRIEF_DESCRIPTION_OF_YOUR_AGENT]` → Short agent description
- `[YOUR_DOMAIN_AREA]` → Your expertise area
- `[YOUR_DOMAIN_KEY]` → Domain key for metadata (e.g., "weather_analysis")

#### **🔧 Capabilities (5 required)**
Replace `[CAPABILITY_1]` through `[CAPABILITY_5]` with your agent's specific abilities:

**Examples:**
```python
# Weather Agent
"weather_forecasting", "climate_analysis", "weather_alerts", "seasonal_patterns", "location_weather"

# Recipe Agent  
"recipe_search", "nutrition_analysis", "dietary_restrictions", "meal_planning", "cooking_tips"

# Stock Agent
"market_analysis", "stock_research", "portfolio_optimization", "risk_assessment", "trend_analysis"
```

#### **🎯 Keywords (7+ recommended)**
Replace `[KEYWORD_1]` through `[KEYWORD_7]` with terms users might use:

**Examples:**
```python
# Weather Agent
["weather", "temperature", "forecast", "rain", "climate", "storm", "sunny", "cloudy", "wind"]

# Recipe Agent
["recipe", "cooking", "ingredients", "food", "meal", "nutrition", "diet", "cuisine"]

# Stock Agent
["stock", "investment", "market", "portfolio", "trading", "finance", "shares", "equity"]
```

#### **💡 Expertise Areas (5 required)**
Replace `[EXPERTISE_AREA_1]` through `[EXPERTISE_AREA_5]`:

**Examples:**
```python
# Weather Agent
- "Weather pattern analysis and forecasting"
- "Climate data interpretation and trends"  
- "Seasonal weather analysis"
- "Location-specific weather insights"
- "Weather impact on activities and planning"
```

#### **🎯 Confidence Terms**
Replace confidence level terms for query matching:

**High Confidence Terms:**
```python
# Weather Agent
["weather forecast", "temperature prediction", "climate analysis"]

# Recipe Agent  
["recipe recommendation", "cooking instructions", "meal planning"]
```

**Medium Confidence Terms:**
```python
# Weather Agent
["sunny", "rainy", "cold", "hot", "windy"]

# Recipe Agent
["ingredients", "cooking", "meal", "food"]
```

**Activity Terms:**
```python
# Weather Agent
["outdoor activities", "vacation planning", "event planning"]

# Recipe Agent
["dinner planning", "party food", "healthy eating"]
```

#### **📊 Categories and Focus Areas**
Define 3 main categories and focus areas for your domain:

**Categories:**
```python
# Weather Agent
"[CATEGORY_1]": "short_term_forecast"    # today, tomorrow
"[CATEGORY_2]": "long_term_climate"      # seasonal, yearly  
"[CATEGORY_3]": "severe_weather"         # storms, alerts

# Recipe Agent
"[CATEGORY_1]": "quick_meals"            # under 30 min
"[CATEGORY_2]": "special_occasions"      # holidays, parties
"[CATEGORY_3]": "dietary_restrictions"   # vegan, gluten-free
```

**Focus Areas:**
```python  
# Weather Agent
"[FOCUS_AREA_1]": "forecast_accuracy"    # prediction quality
"[FOCUS_AREA_2]": "activity_planning"    # outdoor events
"[FOCUS_AREA_3]": "travel_weather"       # location-specific

# Recipe Agent
"[FOCUS_AREA_1]": "nutritional_value"    # health focus
"[FOCUS_AREA_2]": "cooking_difficulty"   # skill level
"[FOCUS_AREA_3]": "ingredient_sourcing"  # availability
```

### **Step 3: Implement Custom Methods**

Replace `[YOUR_CUSTOM_METHOD_1]` and `[YOUR_CUSTOM_METHOD_2]` with your domain-specific functions:

**Example - Weather Agent:**
```python
def get_weather_forecast(self, location: str, days: int = 7) -> Dict[str, Any]:
    """Get weather forecast for specific location"""
    # Your weather API integration logic
    return forecast_data

def analyze_weather_pattern(self, historical_data: List[Dict]) -> Dict[str, Any]:
    """Analyze historical weather patterns"""  
    # Your pattern analysis logic
    return pattern_analysis
```

**Example - Recipe Agent:**
```python
def search_recipes(self, ingredients: List[str], dietary_restrictions: List[str] = None) -> List[Dict]:
    """Search recipes based on available ingredients"""
    # Your recipe search logic
    return matching_recipes

def calculate_nutrition(self, recipe_data: Dict) -> Dict[str, float]:
    """Calculate nutritional information for recipe"""
    # Your nutrition calculation logic  
    return nutrition_info
```

### **Step 4: Update Agent Configuration**

Add your agent to `core/agents.json`:

```json
{
  "agents": [
    {
      "id": "YourAgentNameAgent",
      "name": "Your Agent Display Name", 
      "module": "agents.your_agent_filename",
      "description": "Brief description of what your agent does",
      "capabilities": ["capability_1", "capability_2", "capability_3"],
      "priority": 4
    }
  ],
  "edges": {
    "YourAgentNameAgent": ["SearchAgent"],
    "ScenicLocationFinderAgent": ["YourAgentNameAgent", "ForestAnalyzerAgent", "SearchAgent"]
  },
  "edge_conditions": {
    "ScenicLocationFinderAgent->YourAgentNameAgent": "contains your domain keywords",
    "YourAgentNameAgent->SearchAgent": "needs historical context"
  }
}
```

### **Step 5: Test Your Agent**

Create a simple test:

```python
# test_your_agent.py
from agents.your_agent_name import YourAgentNameAgent
from core.memory_manager import MemoryManager

# Initialize agent
memory_manager = MemoryManager()
agent = YourAgentNameAgent(memory_manager)

# Test query handling
test_query = "your test query here"
confidence = agent.can_handle(test_query)
print(f"Confidence: {confidence}")

# Test processing (mock state)
state = {
    "question": test_query,
    "user_id": 1,
    "session_id": "test_session"
}

result = agent.process(state)
print(f"Response: {result.get('answer', 'No response')}")
```

---

## 🎯 **Real-World Examples**

### **Example 1: Weather Agent**
```python
class WeatherAnalyzerAgent(BaseAgent):
    def __init__(self, memory_manager=None, name: str = "WeatherAnalyzer"):
        super().__init__(memory_manager, name)
        self._description = "Advanced weather analysis and forecasting agent"
        self._capabilities = [
            "weather_forecasting",
            "climate_analysis", 
            "weather_alerts",
            "seasonal_patterns",
            "location_weather"
        ]
    
    @property
    def keywords(self) -> List[str]:
        return [
            "weather", "temperature", "forecast", "rain", "climate",
            "storm", "sunny", "cloudy", "wind", "humidity", "pressure"
        ]
```

### **Example 2: Recipe Agent**
```python
class RecipeRecommenderAgent(BaseAgent):
    def __init__(self, memory_manager=None, name: str = "RecipeRecommender"):
        super().__init__(memory_manager, name)
        self._description = "Culinary expert for recipe recommendations and cooking guidance"
        self._capabilities = [
            "recipe_search",
            "nutrition_analysis",
            "dietary_restrictions", 
            "meal_planning",
            "cooking_tips"
        ]
    
    @property  
    def keywords(self) -> List[str]:
        return [
            "recipe", "cooking", "ingredients", "food", "meal",
            "nutrition", "diet", "cuisine", "chef", "kitchen"
        ]
```

### **Example 3: Stock Analysis Agent**
```python
class StockAnalyzerAgent(BaseAgent):
    def __init__(self, memory_manager=None, name: str = "StockAnalyzer"):
        super().__init__(memory_manager, name)
        self._description = "Financial markets and investment analysis specialist"
        self._capabilities = [
            "market_analysis",
            "stock_research",
            "portfolio_optimization",
            "risk_assessment", 
            "trend_analysis"
        ]
    
    @property
    def keywords(self) -> List[str]:
        return [
            "stock", "investment", "market", "portfolio", "trading",
            "finance", "shares", "equity", "dividend", "earnings"
        ]
```

---

## ✅ **Validation Checklist**

Before deploying your agent, ensure:

- [ ] **All placeholders replaced** with actual values
- [ ] **5 capabilities** defined and relevant to your domain  
- [ ] **7+ keywords** that users would actually search for
- [ ] **3 categories** and **3 focus areas** properly defined
- [ ] **Custom methods** implemented with your business logic
- [ ] **Agent added** to `core/agents.json` configuration
- [ ] **Edge connections** defined for multi-agent communication  
- [ ] **Basic testing** completed and working
- [ ] **Error handling** works properly
- [ ] **Memory integration** storing interactions correctly

---

## 🔧 **Advanced Customization**

### **Custom API Integrations**
```python
def integrate_external_api(self, query_params: Dict) -> Dict:
    """Integrate with external APIs for your domain"""
    import requests
    
    try:
        response = requests.get("https://api.yourdomain.com/data", params=query_params)
        return response.json()
    except Exception as e:
        logger.error(f"API integration failed: {e}")
        return {}
```

### **Custom Data Processing**
```python
def process_domain_data(self, raw_data: List[Dict]) -> Dict[str, Any]:
    """Process domain-specific data formats"""
    processed = {
        "summary": [],
        "insights": [],
        "recommendations": []
    }
    
    # Your custom data processing logic
    for item in raw_data:
        # Process each data item
        pass
        
    return processed
```

### **Custom Scoring Logic**
```python
def calculate_relevance_score(self, query: str, content: Dict) -> float:
    """Custom relevance scoring for your domain"""
    score = 0.0
    
    # Your custom scoring algorithm
    # Consider domain-specific factors
    
    return min(score, 1.0)
```

---

## 🚀 **Deployment Steps**

1. **Test Locally**: Ensure your agent works in isolation
2. **Integration Test**: Test with other agents in the system  
3. **Configuration Update**: Update `agents.json` with proper connections
4. **System Restart**: Restart the FastAPI server to load new agent
5. **End-to-End Test**: Test multi-agent queries involving your agent
6. **Monitor Performance**: Check logs and response quality

---

## 🎉 **You're Done!**

Your custom agent is now ready to participate in the democratic multi-agent system! It will automatically:

✅ **Compete fairly** with other agents based on query relevance  
✅ **Collaborate** when multiple agents are needed  
✅ **Learn** from user interactions through memory integration  
✅ **Scale** with the system as usage grows  

---

## 📞 **Need Help?**

- Check existing agents in the `agents/` directory for examples
- Review `core/base_agent.py` for available methods and properties  
- Test with simple queries first, then increase complexity
- Use logging to debug issues: `logger.info("Debug message")`

**Happy Agent Building! 🎯**
