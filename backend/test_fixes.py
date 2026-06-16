import requests
import time

BASE_URL = "http://localhost:8000"

print("Testing RAG triggers...\n")

queries = [
    "What does the manual say about maintenance?",
    "Explain the specifications in the document",
    "Tell me about this PDF"
]

for query in queries:
    print(f"Query: {query}")
    
    response = requests.post(
        f"{BASE_URL}/api/agents/chat",
        json={"message": query, "session_id": f"test_{int(time.time())}"},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        sources = data.get('metadata', {}).get('sources_count', 0)
        answer = data.get('response', '')[:100]
        
        if sources > 0:
            print(f"  ✓ RAG triggered ({sources} sources)")
        else:
            print(f"  ✗ No RAG sources")
        
        if "help with equipment" in answer:
            print(f"  ✗ Generic fallback response")
        else:
            print(f"  ✓ Real answer: {answer}...")
    
    print()
    time.sleep(0.5)
