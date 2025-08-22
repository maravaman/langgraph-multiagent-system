#!/usr/bin/env python3
"""
Quick Test for SearchAgent Functionality
"""

import requests
import json
import time

def test_search_agent_direct():
    """Test SearchAgent with specific search keywords"""
    base_url = "http://localhost:8003"
    
    print("🔍 TESTING SEARCH AGENT DIRECTLY")
    print("=" * 50)
    
    # Test with existing user from previous test
    test_user = {
        'username': 'testuser123',
        'password': 'test123'
    }
    
    try:
        # Try to login with existing user
        login_resp = requests.post(f"{base_url}/auth/login", json=test_user, timeout=10)
        
        if login_resp.status_code != 200:
            # Create user if doesn't exist
            print("Creating new test user...")
            reg_resp = requests.post(f"{base_url}/auth/register", json={
                'username': test_user['username'],
                'email': 'test@example.com',
                'password': test_user['password']
            }, timeout=10)
            
            if reg_resp.status_code != 200:
                print(f"❌ Could not create user: {reg_resp.text}")
                return
            
            # Login again
            login_resp = requests.post(f"{base_url}/auth/login", json=test_user, timeout=10)
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.text}")
            return
        
        token_data = login_resp.json()
        headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
        
        # Get user info
        me_resp = requests.get(f"{base_url}/auth/me", headers=headers, timeout=10)
        user_data = me_resp.json()
        print(f"✅ Authenticated as: {user_data['username']} (ID: {user_data['id']})")
        
        # Test queries designed to trigger SearchAgent specifically
        search_test_queries = [
            "search history",  # Simple search keyword
            "recall what we discussed",  # Recall keyword
            "find similar past conversations",  # Multiple search keywords
            "remember our previous discussions",  # Remember keyword
            "show me my conversation history"  # Clear search intent
        ]
        
        print(f"\n📋 Testing {len(search_test_queries)} search-focused queries:")
        
        for i, query in enumerate(search_test_queries, 1):
            print(f"\n{i}. Query: \"{query}\"")
            
            try:
                start = time.time()
                chat_resp = requests.post(f"{base_url}/ai/chat", json={
                    'user': user_data['username'],
                    'user_id': user_data['id'],
                    'question': query
                }, headers=headers, timeout=30)
                
                if chat_resp.status_code == 200:
                    result = chat_resp.json()
                    elapsed = time.time() - start
                    
                    agent_used = result.get('agent', 'Unknown')
                    strategy = result.get('orchestration', {}).get('strategy', 'unknown')
                    routing_scores = result.get('orchestration', {}).get('routing_scores', {})
                    
                    print(f"   Agent Used: {agent_used}")
                    print(f"   Strategy: {strategy}")
                    print(f"   Routing Scores: {routing_scores}")
                    print(f"   Processing Time: {elapsed:.3f}s")
                    
                    # Check if SearchAgent was activated
                    if agent_used == 'SearchAgent':
                        print("   ✅ SearchAgent activated successfully!")
                        
                        # Check response format
                        response = result.get('response', '')
                        if response.startswith('{'):
                            try:
                                json_data = json.loads(response)
                                search_results = json_data.get('search_results', {})
                                total_matches = search_results.get('total_matches', 0)
                                print(f"   ✅ JSON Response with {total_matches} matches")
                            except json.JSONDecodeError:
                                print("   ⚠️ Response appears to be JSON but couldn't parse")
                        else:
                            print("   ⚠️ Response is not in JSON format")
                    
                    elif 'multi_agent_responses' in result:
                        # Check if SearchAgent is in multi-agent responses
                        multi_responses = result['multi_agent_responses']
                        search_agent_found = any(r.get('agent') == 'SearchAgent' for r in multi_responses)
                        if search_agent_found:
                            print("   ✅ SearchAgent found in multi-agent coordination!")
                        else:
                            print("   ℹ️ SearchAgent not selected in multi-agent coordination")
                            agents_used = [r.get('agent') for r in multi_responses]
                            print(f"   Agents used: {agents_used}")
                    else:
                        print(f"   ℹ️ Routed to {agent_used} instead")
                        
                        # Check if search score was calculated
                        search_score = routing_scores.get('SearchAgent', 0)
                        print(f"   SearchAgent Score: {search_score}")
                
                else:
                    print(f"   ❌ Request failed: HTTP {chat_resp.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(0.5)  # Small delay between requests
        
        print(f"\n✅ Search agent test completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_search_agent_direct()
