#!/usr/bin/env python3
"""
Simple, Clean Ollama Client
Direct interaction with Ollama without multi-agent orchestration or verbose logging
"""
import requests
import json
import sys

class SimpleOllamaClient:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.default_model = "llama3:latest"
        self.timeout = 30

    def is_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_clean_response(self, prompt: str, model: str = None) -> str:
        """Get a clean, direct response from Ollama"""
        if not self.is_available():
            return "❌ Ollama server is not available. Please start Ollama first."
        
        try:
            model_name = model or self.default_model
            
            # Simple, clean payload
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
            else:
                return f"❌ Ollama API error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "⏱️ Request timed out"
        except requests.exceptions.ConnectionError:
            return "🔌 Connection error - is Ollama running?"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def chat_mode(self):
        """Interactive chat mode"""
        print("🤖 Simple Ollama Chat")
        print("Type 'quit' or 'exit' to stop\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖:", end=" ", flush=True)
                response = self.get_clean_response(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    client = SimpleOllamaClient()
    
    if len(sys.argv) > 1:
        # Command line mode
        query = " ".join(sys.argv[1:])
        response = client.get_clean_response(query)
        print(response)
    else:
        # Interactive chat mode
        client.chat_mode()

if __name__ == "__main__":
    main()
