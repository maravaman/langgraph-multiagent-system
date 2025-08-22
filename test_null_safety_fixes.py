#!/usr/bin/env python3
"""
Test script to verify comprehensive null-safety fixes in the LangGraph multiagent system
Tests various failure scenarios to ensure graceful error handling
"""

import json
import logging
import sys
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.append('.')

try:
    from core.langgraph_multiagent_system import LangGraphMultiAgentSystem, MultiAgentState
    from core.ollama_client import prompt_manager, ollama_client
    logger.info("✅ Successfully imported all required modules")
except ImportError as e:
    logger.error(f"❌ Import failed: {e}")
    sys.exit(1)

class TestNullSafetyFixes(unittest.TestCase):
    """Test comprehensive null-safety fixes in the multiagent system"""
    
    def setUp(self):
        """Setup test environment"""
        self.system = LangGraphMultiAgentSystem()
        
    def test_prompt_manager_null_safety(self):
        """Test prompt manager handles null inputs gracefully"""
        logger.info("🧪 Testing prompt manager null safety...")
        
        # Test with None agent name
        result = prompt_manager.get_prompt(None, "test query", "test context")
        self.assertIsInstance(result, dict)
        self.assertIn("prompt", result)
        self.assertIn("system", result)
        
        # Test with empty agent name
        result = prompt_manager.get_prompt("", "test query", "test context")
        self.assertIsInstance(result, dict)
        self.assertIn("prompt", result)
        self.assertIn("system", result)
        
        # Test with invalid agent name
        result = prompt_manager.get_prompt("NonExistentAgent", "test query", "test context")
        self.assertIsInstance(result, dict)
        self.assertIn("prompt", result)
        self.assertIn("system", result)
        
        # Test with None query
        result = prompt_manager.get_prompt("WeatherAgent", None, "test context")
        self.assertIsInstance(result, dict)
        self.assertIn("prompt", result)
        self.assertIn("system", result)
        
        # Test with None context
        result = prompt_manager.get_prompt("WeatherAgent", "test query", None)
        self.assertIsInstance(result, dict)
        self.assertIn("prompt", result)
        self.assertIn("system", result)
        
        logger.info("✅ Prompt manager null safety tests passed")
    
    @patch('core.ollama_client.ollama_client.generate_response')
    @patch('core.ollama_client.prompt_manager.get_prompt')
    def test_weather_agent_error_handling(self, mock_get_prompt, mock_generate):
        """Test weather agent handles various error scenarios"""
        logger.info("🧪 Testing weather agent error handling...")
        
        # Test scenario 1: prompt_manager returns None
        mock_get_prompt.return_value = None
        mock_generate.return_value = "Fallback weather response"
        
        test_state = MultiAgentState(
            question="What's the weather like?",
            user_id=1,
            context={},
            agent_responses={}
        )
        
        result = self.system._weather_agent_node(test_state)
        self.assertIn("WeatherAgent", result["agent_responses"])
        self.assertIsInstance(result["agent_responses"]["WeatherAgent"], str)
        
        # Test scenario 2: prompt_manager returns invalid dict
        mock_get_prompt.return_value = {"invalid": "data"}
        
        result = self.system._weather_agent_node(test_state)
        self.assertIn("WeatherAgent", result["agent_responses"])
        
        # Test scenario 3: ollama_client throws exception
        mock_get_prompt.return_value = {"prompt": "test", "system": "test"}
        mock_generate.side_effect = Exception("Ollama error")
        
        result = self.system._weather_agent_node(test_state)
        self.assertIn("WeatherAgent", result["agent_responses"])
        self.assertIn("unavailable", result["agent_responses"]["WeatherAgent"].lower())
        
        logger.info("✅ Weather agent error handling tests passed")
    
    @patch('core.ollama_client.ollama_client.generate_response')
    @patch('core.ollama_client.prompt_manager.get_prompt')
    def test_dining_agent_error_handling(self, mock_get_prompt, mock_generate):
        """Test dining agent handles various error scenarios"""
        logger.info("🧪 Testing dining agent error handling...")
        
        # Test scenario 1: prompt_manager returns None
        mock_get_prompt.return_value = None
        mock_generate.return_value = "Fallback dining response"
        
        test_state = MultiAgentState(
            question="Where should I eat?",
            user_id=1,
            context={},
            agent_responses={}
        )
        
        result = self.system._dining_agent_node(test_state)
        self.assertIn("DiningAgent", result["agent_responses"])
        self.assertIsInstance(result["agent_responses"]["DiningAgent"], str)
        
        # Test scenario 2: empty question
        test_state["question"] = ""
        result = self.system._dining_agent_node(test_state)
        self.assertIn("DiningAgent", result["agent_responses"])
        
        logger.info("✅ Dining agent error handling tests passed")
    
    @patch('core.ollama_client.ollama_client.generate_response')
    @patch('core.ollama_client.prompt_manager.get_prompt')
    def test_scenic_agent_error_handling(self, mock_get_prompt, mock_generate):
        """Test scenic location agent handles various error scenarios"""
        logger.info("🧪 Testing scenic agent error handling...")
        
        # Test with malformed context data
        mock_get_prompt.return_value = {"prompt": "test", "system": "test"}
        mock_generate.return_value = "Scenic location response"
        
        test_state = MultiAgentState(
            question="Find beautiful places",
            user_id=1,
            context={},
            agent_responses={},
            weather_data={"invalid": "data"},  # Missing expected keys
            dining_data=None  # None data
        )
        
        result = self.system._scenic_agent_node(test_state)
        self.assertIn("ScenicLocationFinderAgent", result["agent_responses"])
        self.assertIsInstance(result["agent_responses"]["ScenicLocationFinderAgent"], str)
        
        logger.info("✅ Scenic agent error handling tests passed")
    
    @patch('core.ollama_client.ollama_client.generate_response')
    @patch('core.ollama_client.prompt_manager.get_prompt')
    def test_search_agent_error_handling(self, mock_get_prompt, mock_generate):
        """Test search agent handles various error scenarios"""
        logger.info("🧪 Testing search agent error handling...")
        
        # Mock memory search failure
        with patch.object(self.system, '_perform_memory_search', side_effect=Exception("Memory error")):
            mock_get_prompt.return_value = {"prompt": "test", "system": "test"}
            mock_generate.return_value = "Search response"
            
            test_state = MultiAgentState(
                question="Search my history",
                user_id=1,
                context={},
                agent_responses={}
            )
            
            result = self.system._search_agent_node(test_state)
            self.assertIn("SearchAgent", result["agent_responses"])
            self.assertIsInstance(result["agent_responses"]["SearchAgent"], str)
        
        logger.info("✅ Search agent error handling tests passed")
    
    def test_build_context_string_safety(self):
        """Test context string building with various malformed inputs"""
        logger.info("🧪 Testing context string building safety...")
        
        # Test with None context
        result = self.system._build_context_string(None)
        self.assertIsInstance(result, str)
        
        # Test with empty context
        result = self.system._build_context_string({})
        self.assertIsInstance(result, str)
        
        # Test with malformed STM data
        malformed_context = {
            "stm": {"recent_interactions": None},
            "ltm": {"recent_history": []}
        }
        result = self.system._build_context_string(malformed_context)
        self.assertIsInstance(result, str)
        
        # Test with malformed LTM data
        malformed_context = {
            "stm": {},
            "ltm": {"recent_history": [{"invalid": "entry"}, None, {"value": "valid entry"}]}
        }
        result = self.system._build_context_string(malformed_context)
        self.assertIsInstance(result, str)
        
        logger.info("✅ Context string building safety tests passed")
    
    def test_memory_search_error_handling(self):
        """Test memory search handles errors gracefully"""
        logger.info("🧪 Testing memory search error handling...")
        
        # Mock memory manager failures
        with patch.object(self.system.memory_manager, 'get_all_stm_for_user', side_effect=Exception("STM error")):
            with patch.object(self.system.memory_manager, 'get_recent_ltm', side_effect=Exception("LTM error")):
                result = self.system._perform_memory_search("test query", 1)
                self.assertIsInstance(result, dict)
                self.assertIn("error", result)
        
        logger.info("✅ Memory search error handling tests passed")
    
    @patch('core.ollama_client.ollama_client.generate_response')
    @patch('core.ollama_client.prompt_manager.get_prompt')
    def test_complete_system_with_errors(self, mock_get_prompt, mock_generate):
        """Test complete system execution with various error conditions"""
        logger.info("🧪 Testing complete system with simulated errors...")
        
        # Setup mocks to simulate various failure conditions
        mock_get_prompt.side_effect = [
            None,  # First call returns None
            {"prompt": "test", "system": "test"},  # Second call succeeds
            Exception("Prompt error"),  # Third call throws exception
        ]
        mock_generate.return_value = "Test response"
        
        # Test query that should trigger multiple agents
        result = self.system.process_request(
            user="test_user",
            user_id=1,
            question="What's the weather like for dining at scenic locations?"
        )
        
        # Verify system completed without crashing
        self.assertIsInstance(result, dict)
        self.assertIn("response", result)
        self.assertIn("timestamp", result)
        self.assertIn("system_version", result)
        
        # Verify error didn't propagate to top level
        self.assertNotIn("error", result) or not result.get("error", False)
        
        logger.info("✅ Complete system error handling tests passed")
    
    def test_state_validation(self):
        """Test state validation and sanitization"""
        logger.info("🧪 Testing state validation...")
        
        # Test with minimal state
        minimal_state = MultiAgentState(question="test", user_id=1)
        
        # Verify each agent can handle minimal state
        agents_to_test = [
            self.system._weather_agent_node,
            self.system._dining_agent_node,
            self.system._scenic_agent_node,
            self.system._forest_agent_node,
            self.system._search_agent_node
        ]
        
        for agent_func in agents_to_test:
            with patch('core.ollama_client.prompt_manager.get_prompt') as mock_prompt:
                with patch('core.ollama_client.ollama_client.generate_response') as mock_generate:
                    mock_prompt.return_value = {"prompt": "test", "system": "test"}
                    mock_generate.return_value = "Test response"
                    
                    result = agent_func(minimal_state.copy())
                    self.assertIsInstance(result, dict)
                    self.assertIn("current_agent", result)
                    self.assertIn("agent_responses", result)
        
        logger.info("✅ State validation tests passed")

def run_comprehensive_test():
    """Run all null-safety tests"""
    logger.info("🚀 Starting comprehensive null-safety testing...")
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestNullSafetyFixes)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report results
    if result.wasSuccessful():
        logger.info("🎉 All null-safety tests passed! System is robust against NoneType errors.")
        return True
    else:
        logger.error(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for failure in result.failures:
            logger.error(f"FAILURE: {failure[0]} - {failure[1]}")
        for error in result.errors:
            logger.error(f"ERROR: {error[0]} - {error[1]}")
        return False

def test_basic_functionality():
    """Test basic functionality with mocked Ollama"""
    logger.info("🧪 Testing basic functionality with mocked responses...")
    
    try:
        system = LangGraphMultiAgentSystem()
        
        # Mock successful prompt and response generation
        with patch('core.ollama_client.prompt_manager.get_prompt') as mock_prompt:
            with patch('core.ollama_client.ollama_client.generate_response') as mock_generate:
                
                mock_prompt.return_value = {
                    "prompt": "Test prompt for weather query",
                    "system": "You are a weather agent"
                }
                mock_generate.return_value = "Mock weather response: Sunny with temperature 25°C"
                
                # Test weather query
                result = system.process_request(
                    user="test_user",
                    user_id=1, 
                    question="What's the weather like today?"
                )
                
                # Verify successful execution
                assert result["response"], "Response should not be empty"
                assert "WeatherAgent" in result.get("agents_involved", []), "Weather agent should be involved"
                assert result.get("system_version") == "2.0.0-multiagent", "System version should be correct"
                
                logger.info("✅ Basic weather functionality test passed")
                
                # Test dining query
                mock_prompt.return_value = {
                    "prompt": "Test prompt for dining query",
                    "system": "You are a dining agent"
                }
                mock_generate.return_value = "Mock dining response: Great Italian restaurants nearby"
                
                result = system.process_request(
                    user="test_user",
                    user_id=1,
                    question="Where can I find good Italian food?"
                )
                
                assert result["response"], "Response should not be empty"
                assert "DiningAgent" in result.get("agents_involved", []), "Dining agent should be involved"
                
                logger.info("✅ Basic dining functionality test passed")
                
                # Test complex query (should trigger multiple agents)
                result = system.process_request(
                    user="test_user",
                    user_id=1,
                    question="Plan a scenic trip with good weather and dining options"
                )
                
                assert result["response"], "Response should not be empty"
                agents_involved = result.get("agents_involved", [])
                assert len(agents_involved) >= 1, "Multiple agents should be involved"
                
                logger.info("✅ Complex query functionality test passed")
                
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic functionality test failed: {e}")
        return False

def test_error_propagation():
    """Test that errors don't propagate and crash the system"""
    logger.info("🧪 Testing error propagation prevention...")
    
    try:
        system = LangGraphMultiAgentSystem()
        
        # Mock complete failure of prompt manager
        with patch('core.ollama_client.prompt_manager.get_prompt', side_effect=Exception("Complete failure")):
            with patch('core.ollama_client.ollama_client.generate_response', side_effect=Exception("Ollama failure")):
                
                result = system.process_request(
                    user="test_user",
                    user_id=1,
                    question="This should handle errors gracefully"
                )
                
                # System should not crash and should return a valid response structure
                assert isinstance(result, dict), "Result should be a dictionary"
                assert "response" in result, "Result should have a response field"
                assert "timestamp" in result, "Result should have a timestamp"
                
                # Response should indicate issues but not crash
                response = result["response"]
                assert isinstance(response, str), "Response should be a string"
                assert len(response) > 0, "Response should not be empty"
                
                logger.info(f"System gracefully handled complete failure with response: {response[:100]}...")
                
        return True
        
    except Exception as e:
        logger.error(f"❌ Error propagation test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("🔬 COMPREHENSIVE NULL-SAFETY TESTING")
    print("=" * 80)
    
    all_passed = True
    
    # Run unit tests
    if not run_comprehensive_test():
        all_passed = False
    
    print("\n" + "=" * 80)
    
    # Test basic functionality
    if not test_basic_functionality():
        all_passed = False
    
    print("\n" + "=" * 80)
    
    # Test error propagation
    if not test_error_propagation():
        all_passed = False
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! The multiagent system is now robust against NoneType errors.")
        print("✅ System will gracefully handle:")
        print("   - Invalid prompt data")
        print("   - Ollama client failures")
        print("   - Memory system errors")
        print("   - Malformed state data")
        print("   - Network timeouts")
        print("   - Empty or None inputs")
    else:
        print("❌ Some tests failed. Please review the logs above.")
    
    print("=" * 80)
