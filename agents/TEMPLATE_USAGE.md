# 🚀 Quick Agent Creation Guide

## Using the Agent Template (`agent_template.py`)

### ⚡ **Quick Start (5 minutes)**

1. **Copy the template:**
   ```bash
   cp agents/agent_template.py agents/my_new_agent.py
   ```

2. **Replace UPPERCASE placeholders with your values:**
   ```python
   # FROM:
   class YOUR_AGENT_NAMEAgent(BaseAgent):
   
   # TO:
   class WeatherAnalyzerAgent(BaseAgent):
   ```

3. **Add to configuration:**
   - Copy the JSON template at bottom of file
   - Add to `core/agents.json`

4. **Restart server and test!**

---

## 📝 **Replacement Guide**

### **Basic Info**
- `YOUR_AGENT_NAME` → `WeatherAnalyzer` (your agent name)
- `YOUR_DOMAIN_HERE` → `weather analysis and forecasting`
- `YOUR_AGENT_DESCRIPTION_HERE` → `Advanced weather forecasting agent`
- `YOUR_DOMAIN_AREA` → `meteorology and climate science`
- `YOUR_DOMAIN_KEY` → `weather` (for metadata)

### **Capabilities (5 required)**
```python
# Replace these 5:
"YOUR_CAPABILITY_1" → "weather_forecasting"
"YOUR_CAPABILITY_2" → "climate_analysis"  
"YOUR_CAPABILITY_3" → "weather_alerts"
"YOUR_CAPABILITY_4" → "seasonal_patterns"
"YOUR_CAPABILITY_5" → "location_weather"
```

### **Keywords (7+ required)**
```python
# Replace with words users would search:
"YOUR_KEYWORD_1" → "weather"
"YOUR_KEYWORD_2" → "temperature"
"YOUR_KEYWORD_3" → "forecast"
"YOUR_KEYWORD_4" → "rain"
"YOUR_KEYWORD_5" → "climate"
"YOUR_KEYWORD_6" → "storm"
"YOUR_KEYWORD_7" → "sunny"
```

### **Expertise Areas (5 required)**
```python
# Replace with your knowledge areas:
"YOUR_EXPERTISE_1" → "Weather pattern analysis and forecasting"
"YOUR_EXPERTISE_2" → "Climate data interpretation"
"YOUR_EXPERTISE_3" → "Seasonal trend analysis"
"YOUR_EXPERTISE_4" → "Location-specific weather insights"
"YOUR_EXPERTISE_5" → "Weather impact on activities"
```

### **Confidence Terms**
```python
# High confidence (exact matches):
"YOUR_HIGH_CONFIDENCE_TERM_1" → "weather forecast"
"YOUR_HIGH_CONFIDENCE_TERM_2" → "temperature prediction"
"YOUR_HIGH_CONFIDENCE_TERM_3" → "climate analysis"

# Medium confidence (related terms):
"YOUR_MEDIUM_TERM_1" → "sunny"
"YOUR_MEDIUM_TERM_2" → "rainy"  
"YOUR_MEDIUM_TERM_3" → "cold"

# Activity terms (what people do):
"YOUR_ACTIVITY_TERM_1" → "outdoor planning"
"YOUR_ACTIVITY_TERM_2" → "vacation planning"
"YOUR_ACTIVITY_TERM_3" → "event planning"
```

### **Categories and Focus Areas**
```python
# Categories (3 main types in your domain):
"YOUR_CATEGORY_1" → "short_term_forecast"
"CATEGORY_1_TERM_1" → "today"
"CATEGORY_1_TERM_2" → "tomorrow"

"YOUR_CATEGORY_2" → "long_term_forecast"  
"CATEGORY_2_TERM_1" → "weekly"
"CATEGORY_2_TERM_2" → "monthly"

"YOUR_CATEGORY_3" → "severe_weather"
"CATEGORY_3_TERM_1" → "storm"
"CATEGORY_3_TERM_2" → "emergency"

# Focus areas (3 main purposes):
"YOUR_FOCUS_AREA_1" → "activity_planning"
"FOCUS_1_TERM_1" → "outdoor"
"FOCUS_1_TERM_2" → "activities"

"YOUR_FOCUS_AREA_2" → "travel_planning"
"FOCUS_2_TERM_1" → "travel"
"FOCUS_2_TERM_2" → "vacation"

"YOUR_FOCUS_AREA_3" → "safety_alerts"
"FOCUS_3_TERM_1" → "warning"
"FOCUS_3_TERM_2" → "safety"
```

---

## 🎯 **Domain Examples**

### 🌤️ **Weather Agent**
```python
YOUR_AGENT_NAME → WeatherAnalyzer
Keywords: weather, temperature, forecast, rain, climate, storm, sunny
Capabilities: weather_forecasting, climate_analysis, weather_alerts
```

### 🍳 **Recipe Agent**
```python
YOUR_AGENT_NAME → RecipeRecommender  
Keywords: recipe, cooking, ingredients, food, meal, cuisine, chef
Capabilities: recipe_search, nutrition_analysis, meal_planning
```

### 📈 **Stock Agent**
```python
YOUR_AGENT_NAME → StockAnalyzer
Keywords: stock, investment, market, portfolio, trading, finance, shares  
Capabilities: market_analysis, stock_research, portfolio_optimization
```

### 🎵 **Music Agent**
```python
YOUR_AGENT_NAME → MusicRecommender
Keywords: music, song, artist, playlist, album, genre, concert
Capabilities: music_discovery, playlist_generation, artist_analysis
```

---

## 📋 **Configuration Setup**

### 1. **Add to `core/agents.json`:**
```json
{
  "agents": [
    // ... existing agents ...
    {
      "id": "WeatherAnalyzerAgent",
      "name": "Weather Analyzer Agent",
      "module": "agents.weather_analyzer",
      "description": "Advanced weather forecasting and climate analysis",
      "capabilities": ["weather_forecasting", "climate_analysis", "weather_alerts"],
      "priority": 4
    }
  ]
}
```

### 2. **Add edge connections:**
```json
{
  "edges": {
    "WeatherAnalyzerAgent": ["SearchAgent"],
    "ScenicLocationFinderAgent": ["WeatherAnalyzerAgent", "ForestAnalyzerAgent", "SearchAgent"]
  }
}
```

### 3. **Add edge conditions:**
```json
{
  "edge_conditions": {
    "ScenicLocationFinderAgent->WeatherAnalyzerAgent": "contains weather-related keywords",
    "WeatherAnalyzerAgent->SearchAgent": "needs historical weather context"
  }
}
```

---

## ✅ **Quick Test**

Create a test file:
```python
# test_my_agent.py
from agents.my_new_agent import MyNewAgentAgent

agent = MyNewAgentAgent()
print(f"Agent: {agent.name}")
print(f"Keywords: {agent.keywords}")
print(f"Confidence for 'weather today': {agent.can_handle('weather today')}")
```

---

## 🎉 **You're Done!**

Your agent is now ready to:
- ✅ **Compete fairly** with other agents
- ✅ **Handle relevant queries** automatically  
- ✅ **Store interactions** in memory
- ✅ **Collaborate** with other agents
- ✅ **Scale** with the system

**Just restart the FastAPI server and start testing!** 🚀
