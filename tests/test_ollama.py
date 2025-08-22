#!/usr/bin/env python3
import requests
import json

payload = {
    'model': 'llama3:latest',
    'prompt': 'What is the capital of India? Answer in one sentence.',
    'stream': False,
    'options': {
        'temperature': 0.7,
        'num_predict': 50
    }
}

try:
    print("Testing Ollama connection...")
    response = requests.post(
        'http://localhost:11434/api/generate',
        json=payload,
        timeout=(5, 30),
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print('✅ SUCCESS: Ollama responded successfully')
        print(f'Response: {result.get("response", "No response")}')
        print(f'Response length: {len(result.get("response", ""))} characters')
    else:
        print(f'❌ ERROR: HTTP {response.status_code}')
        print(response.text)
        
except requests.exceptions.Timeout:
    print('⏰ ERROR: Request timed out')
except requests.exceptions.ConnectionError:
    print('🔌 ERROR: Cannot connect to Ollama')
except Exception as e:
    print(f'❌ ERROR: {e}')
