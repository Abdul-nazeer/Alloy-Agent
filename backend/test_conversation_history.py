"""Quick test for conversation history"""
import requests
import time

BASE_URL = "http://localhost:8000"
session_id = f"conv_test_{int(time.time())}"

conversation = [
    "What equipment do you monitor?",
    "Tell me more about the first type",
    "What sensors does it use?"
]

print(f"Testing conversation history with session: {session_id}\n")

for i, query in enumerate(conversation, 1):
    print(f"\n{'='*60}")
    print(f"Message {i}: {query}")
    print('='*60)
    
    response = requests.post(
        f"{BASE_URL}/api/agents/chat",
        json={"message": query, "session_id": session_id},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get('response', '')
        print(f"Response: {answer[:200]}...")
        
        # Check if follow-up worked
        if i > 1:
            if len(answer) > 50 and "help with equipment" not in answer:
                print("✓ Context preserved!")
            else:
                print("✗ Lost context - generic response")
    else:
        print(f"✗ Error: {response.status_code}")
    
    time.sleep(1)
