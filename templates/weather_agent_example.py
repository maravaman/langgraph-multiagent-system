"""
Weather Analyzer Agent - Complete Example
========================================
This is a complete, working example of an agent created using the sample_agent_template.py
This demonstrates how to properly fill in all placeholders and implement domain-specific logic.

Domain: Weather Analysis
Description: Advanced weather forecasting, climate analysis, and weather-related recommendations
"""

from typing import Dict, Any, List
import logging
import json
from datetime import datetime, timedelta
from core.base_agent import BaseAgent, GraphState

logger = logging.getLogger(__name__)


class WeatherAnalyzerAgent(BaseAgent):
    """
    Agent specialized in weather analysis, forecasting, and climate insights
    
    Provides comprehensive weather information, forecasts, climate analysis,
    and weather-related recommendations for activities and planning.
    """
    
    def __init__(self, memory_manager=None, name: str = "WeatherAnalyzer"):
        super().__init__(memory_manager, name)
        self._description = "Advanced weather forecasting and climate analysis agent"
        
        # Define weather analysis capabilities
        self._capabilities = [
            "weather_forecasting",     # Short and long-term weather predictions
            "climate_analysis",        # Climate patterns and trends analysis  
            "weather_alerts",          # Severe weather warnings and alerts
            "seasonal_patterns",       # Seasonal weather trend analysis
            "location_weather"         # Location-specific weather insights
        ]
    
    @property
    def keywords(self) -> List[str]:
        """
        Keywords that trigger this agent for weather-related queries
        """
        return [
            "weather", "temperature", "forecast", "rain", "climate",
            "storm", "sunny", "cloudy", "wind", "humidity", "pressure",
            "snow", "hot", "cold", "precipitation", "tornado", "hurricane"
        ]
    
    @property
    def system_prompt(self) -> str:
        """
        System prompt defining the weather agent's expertise and personality
        """
        return """You are WeatherAnalyzer, an expert meteorologist and climate specialist.
        
        Your expertise includes:
        - Weather pattern analysis and accurate forecasting
        - Climate data interpretation and long-term trends
        - Seasonal weather analysis and predictions
        - Location-specific weather insights and microclimates
        - Weather impact assessment for activities and planning
        
        Provide accurate, helpful, and actionable weather information.
        Always consider safety implications and provide relevant recommendations.
        Be informative yet accessible to different knowledge levels."""
    
    def get_capabilities(self) -> List[str]:
        """Return list of weather analysis capabilities"""
        return self._capabilities
    
    def process(self, state: GraphState) -> GraphState:
        """
        Main processing method for weather analysis queries
        
        Args:
            state: Current graph state containing user query and context
            
        Returns:
            Updated graph state with weather analysis response
        """
        if not self.validate_state(state):
            return self.handle_error(state, ValueError("Invalid state received"))
        
        query = state.get("question", "")
        user_id = state.get("user_id", 0)
        
        try:
            self.log_processing(query, user_id)
            
            # Search for similar weather queries in user history
            search_results = self.search_similar_content(query, user_id, limit=3)
            
            # Get historical weather research context
            historical_context = self.get_historical_context(user_id, days=7)
            
            # Build weather-specific context
            context_parts = []
            
            # Add similar weather content context
            if search_results.get("similar_content"):
                context_parts.append("Previous weather research:")
                for item in search_results["similar_content"][:2]:
                    if isinstance(item, dict) and "content" in item:
                        context_parts.append(f"- {item['content'][:150]}...")
            
            # Add historical weather context
            if historical_context:
                context_parts.append("Your recent weather history:")
                for item in historical_context[-2:]:
                    if isinstance(item, dict) and "value" in item:
                        context_parts.append(f"- {item['value'][:150]}...")
            
            # Add weather-specific analysis
            weather_type = self._detect_weather_category(query)
            if weather_type != "general":
                context_parts.append(f"Detected weather type: {weather_type}")
            
            # Add analysis focus
            analysis_focus = self._detect_analysis_focus(query)
            if analysis_focus != "general_inquiry":
                context_parts.append(f"Analysis focus: {analysis_focus}")
            
            # Add current weather context (simulated - in real implementation, call weather API)
            current_conditions = self._get_current_conditions_context(query)
            if current_conditions:
                context_parts.append(f"Current conditions context: {current_conditions}")
            
            context = "\n".join(context_parts) if context_parts else ""
            
            # Generate weather analysis response
            response = self.generate_response_with_context(
                query=query,
                context=context,
                temperature=0.6  # Balanced for factual accuracy and descriptive content
            )
            
            # Store interaction with weather-specific metadata
            self.store_interaction(
                user_id=user_id,
                query=query,
                response=response,
                interaction_type="weather_analysis",
                metadata={
                    "weather_category": weather_type,
                    "analysis_focus": analysis_focus,
                    "context_used": bool(context_parts),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Store vector embedding for future weather searches
            self.store_vector_embedding(
                user_id=user_id,
                content=f"Weather Query: {query}\nAnalysis: {response}",
                metadata={
                    "agent": self.name,
                    "domain": "weather_analysis",
                    "category": weather_type,
                    "focus": analysis_focus,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return self.format_state_response(
                state=state,
                response=response,
                additional_data={
                    "orchestration": {
                        "strategy": "weather_analysis",
                        "selected_agents": [self.name],
                        "weather_category": weather_type,
                        "analysis_focus": analysis_focus,
                        "context_used": bool(context_parts)
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def can_handle(self, query: str) -> float:
        """
        Determine confidence level for handling weather-related queries
        
        Args:
            query: User query string
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = super().can_handle(query)
        query_lower = query.lower()
        
        # High-confidence weather-specific terms
        high_confidence_terms = [
            "weather forecast", "temperature prediction", "climate analysis",
            "weather pattern", "storm warning", "precipitation forecast"
        ]
        if any(term in query_lower for term in high_confidence_terms):
            base_confidence = min(base_confidence + 0.4, 1.0)
        
        # Medium-confidence weather terms
        medium_confidence_terms = [
            "sunny", "rainy", "cold", "hot", "windy", "cloudy", "snowy"
        ]
        if any(term in query_lower for term in medium_confidence_terms):
            base_confidence = min(base_confidence + 0.3, 1.0)
        
        # Weather-related activity terms
        activity_terms = [
            "outdoor activities", "vacation planning", "event planning",
            "travel weather", "weekend forecast", "holiday weather"
        ]
        if any(term in query_lower for term in activity_terms):
            base_confidence = min(base_confidence + 0.2, 1.0)
        
        return base_confidence
    
    def _detect_weather_category(self, query: str) -> str:
        """
        Detect the specific weather category being discussed
        
        Args:
            query: User query
            
        Returns:
            Weather category string
        """
        query_lower = query.lower()
        
        # Define weather categories
        if any(term in query_lower for term in ["forecast", "tomorrow", "next week", "prediction"]):
            return "short_term_forecast"
        elif any(term in query_lower for term in ["climate", "seasonal", "annual", "long term"]):
            return "long_term_climate"
        elif any(term in query_lower for term in ["storm", "hurricane", "tornado", "severe", "alert", "warning"]):
            return "severe_weather"
        elif any(term in query_lower for term in ["travel", "vacation", "trip", "destination"]):
            return "travel_weather"
        elif any(term in query_lower for term in ["outdoor", "activities", "sports", "hiking", "camping"]):
            return "activity_weather"
        else:
            return "general"
    
    def _detect_analysis_focus(self, query: str) -> str:
        """
        Detect the focus area of the weather analysis
        
        Args:
            query: User query
            
        Returns:
            Focus area string
        """
        query_lower = query.lower()
        
        # Define focus areas for weather analysis
        if any(term in query_lower for term in ["accurate", "precision", "exactly", "specific"]):
            return "forecast_accuracy"
        elif any(term in query_lower for term in ["activity", "plan", "outdoor", "event"]):
            return "activity_planning"
        elif any(term in query_lower for term in ["travel", "destination", "location", "city"]):
            return "travel_weather"
        elif any(term in query_lower for term in ["safety", "warning", "danger", "risk"]):
            return "safety_assessment"
        elif any(term in query_lower for term in ["pattern", "trend", "history", "past"]):
            return "pattern_analysis"
        else:
            return "general_inquiry"
    
    def _get_current_conditions_context(self, query: str) -> str:
        """
        Get current weather conditions context (simulated for demo)
        In a real implementation, this would call a weather API
        
        Args:
            query: User query to determine relevant conditions
            
        Returns:
            Current conditions summary
        """
        # Simulated current conditions - in real implementation, call weather API
        conditions = {
            "temperature": "22°C",
            "humidity": "65%",
            "wind": "15 km/h NW",
            "conditions": "partly cloudy",
            "pressure": "1013 hPa"
        }
        
        # Return relevant conditions based on query
        if any(term in query.lower() for term in ["temperature", "hot", "cold"]):
            return f"Current temperature: {conditions['temperature']}"
        elif any(term in query.lower() for term in ["wind", "windy"]):
            return f"Current wind: {conditions['wind']}"
        elif any(term in query.lower() for term in ["humidity", "humid"]):
            return f"Current humidity: {conditions['humidity']}"
        else:
            return f"Current conditions: {conditions['conditions']}, {conditions['temperature']}"
    
    # Custom weather-specific methods
    def get_weather_forecast(self, location: str, days: int = 7) -> Dict[str, Any]:
        """
        Get weather forecast for specific location (demo implementation)
        In production, this would integrate with a real weather API
        
        Args:
            location: Location for forecast
            days: Number of days to forecast
            
        Returns:
            Weather forecast data
        """
        # Simulated forecast - replace with actual API call
        forecast = {
            "location": location,
            "forecast_days": days,
            "daily_forecasts": []
        }
        
        # Generate simulated daily forecasts
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            daily_forecast = {
                "date": date.strftime("%Y-%m-%d"),
                "high_temp": f"{20 + (i % 5)}°C",
                "low_temp": f"{15 + (i % 3)}°C",
                "conditions": ["sunny", "cloudy", "rainy", "partly cloudy"][i % 4],
                "precipitation_chance": f"{(i * 10) % 80}%"
            }
            forecast["daily_forecasts"].append(daily_forecast)
        
        return forecast
    
    def analyze_weather_patterns(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze historical weather patterns (demo implementation)
        
        Args:
            historical_data: List of historical weather records
            
        Returns:
            Weather pattern analysis
        """
        analysis = {
            "data_points": len(historical_data),
            "patterns_detected": [],
            "trends": {},
            "anomalies": [],
            "recommendations": []
        }
        
        # Simulated pattern analysis
        analysis["patterns_detected"] = [
            "Seasonal temperature variations",
            "Precipitation patterns correlate with elevation",
            "Wind patterns show seasonal shift"
        ]
        
        analysis["trends"] = {
            "temperature": "Slight warming trend over past 5 years",
            "precipitation": "Increasing variability in rainfall",
            "extreme_events": "More frequent heat waves detected"
        }
        
        analysis["recommendations"] = [
            "Monitor heat wave preparedness for summer months",
            "Consider seasonal activity planning adjustments",
            "Track precipitation patterns for agricultural planning"
        ]
        
        return analysis
    
    def get_weather_recommendations(self, weather_type: str, activity: str = None) -> List[str]:
        """
        Generate weather-specific recommendations
        
        Args:
            weather_type: Type of weather conditions
            activity: Planned activity (optional)
            
        Returns:
            List of weather recommendations
        """
        recommendations = []
        
        # Weather-type specific recommendations
        if weather_type == "severe_weather":
            recommendations.extend([
                "Stay indoors and avoid unnecessary travel",
                "Monitor weather alerts and warnings closely",
                "Prepare emergency supplies and communication plans",
                "Secure outdoor items and property"
            ])
        elif weather_type == "travel_weather":
            recommendations.extend([
                "Check destination weather before departure",
                "Pack appropriate clothing for weather conditions",
                "Monitor travel advisories and road conditions",
                "Consider weather impact on transportation schedules"
            ])
        elif weather_type == "activity_weather":
            recommendations.extend([
                "Plan outdoor activities during optimal weather windows",
                "Bring weather-appropriate gear and clothing",
                "Have backup indoor activities ready",
                "Stay hydrated and protect from sun/cold exposure"
            ])
        
        # Activity-specific recommendations
        if activity:
            activity_lower = activity.lower()
            if "hiking" in activity_lower or "outdoor" in activity_lower:
                recommendations.extend([
                    "Check trail conditions and weather forecasts",
                    "Inform someone of your outdoor plans",
                    "Bring extra layers and weather protection"
                ])
            elif "travel" in activity_lower:
                recommendations.extend([
                    "Allow extra time for weather-related delays",
                    "Check airline/transportation weather policies"
                ])
        
        # General weather recommendations
        recommendations.extend([
            "Stay informed with reliable weather sources",
            "Plan activities with weather contingencies"
        ])
        
        return recommendations
    
    def assess_weather_safety(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess safety implications of weather conditions
        
        Args:
            conditions: Current or forecasted weather conditions
            
        Returns:
            Weather safety assessment
        """
        safety_assessment = {
            "overall_safety": "unknown",
            "risk_factors": [],
            "precautions": [],
            "safe_activities": [],
            "avoid_activities": []
        }
        
        # Example safety analysis (would use real thresholds and conditions)
        temp = conditions.get("temperature", 0)
        wind_speed = conditions.get("wind_speed", 0)
        precipitation = conditions.get("precipitation_chance", 0)
        
        # Temperature safety
        if temp > 35:  # High temperature
            safety_assessment["risk_factors"].append("Extreme heat risk")
            safety_assessment["precautions"].append("Stay hydrated and seek shade")
            safety_assessment["avoid_activities"].append("Strenuous outdoor exercise")
        elif temp < 0:  # Freezing temperature
            safety_assessment["risk_factors"].append("Freezing temperature risk")
            safety_assessment["precautions"].append("Dress warmly and watch for ice")
            safety_assessment["avoid_activities"].append("Extended outdoor exposure")
        
        # Wind safety
        if wind_speed > 50:  # High wind
            safety_assessment["risk_factors"].append("High wind conditions")
            safety_assessment["precautions"].append("Secure loose objects")
            safety_assessment["avoid_activities"].append("Outdoor events with temporary structures")
        
        # Precipitation safety
        if precipitation > 80:  # High precipitation chance
            safety_assessment["risk_factors"].append("Heavy precipitation likely")
            safety_assessment["precautions"].append("Carry rain protection and drive carefully")
            safety_assessment["safe_activities"].append("Indoor activities")
        
        # Overall safety assessment
        if len(safety_assessment["risk_factors"]) == 0:
            safety_assessment["overall_safety"] = "safe"
        elif len(safety_assessment["risk_factors"]) <= 2:
            safety_assessment["overall_safety"] = "caution"
        else:
            safety_assessment["overall_safety"] = "high_risk"
        
        return safety_assessment
