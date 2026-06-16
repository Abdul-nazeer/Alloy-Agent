"""
Comprehensive Feature Test Script
Tests all implemented features for the PDF chat upload and conversation history
"""

import sys
import requests
import time
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = f"test_session_{int(time.time())}"

# ANSI colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ {msg}{RESET}")


# ══════════════════════════════════════════════════════════════════════
# TEST 1: Health Check
# ══════════════════════════════════════════════════════════════════════

def test_health_checks():
    print_test("System Health Checks")
    
    endpoints = [
        "/health",
        "/api/sensors/health", 
        "/api/agents/health",
        "/api/v1/health"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print_success(f"{endpoint} - OK")
            else:
                print_error(f"{endpoint} - Status {response.status_code}")
        except Exception as e:
            print_error(f"{endpoint} - {str(e)}")


# ══════════════════════════════════════════════════════════════════════
# TEST 2: RAG Document Upload
# ══════════════════════════════════════════════════════════════════════

def test_rag_upload():
    print_test("RAG Document Upload")
    
    # Check if any PDFs exist in uploads directory
    upload_dir = Path(__file__).parent / "data" / "uploads"
    pdfs = list(upload_dir.glob("*.pdf")) if upload_dir.exists() else []
    
    if pdfs:
        print_success(f"Found {len(pdfs)} PDFs in uploads directory")
        for pdf in pdfs[:3]:
            print_info(f"  - {pdf.name}")
    else:
        print_error("No PDFs found in uploads directory")
        return None
    
    # Test document listing
    try:
        response = requests.get(f"{BASE_URL}/api/rag/documents", timeout=10)
        if response.status_code == 200:
            docs = response.json()
            print_success(f"Document listing works - {len(docs)} documents indexed")
            if docs:
                doc_id = docs[0].get('doc_id')
                doc_name = docs[0].get('doc_name')
                print_info(f"  Sample doc: {doc_name} (ID: {doc_id})")
                return doc_id, doc_name
        else:
            print_error(f"Document listing failed - Status {response.status_code}")
    except Exception as e:
        print_error(f"Document listing error: {str(e)}")
    
    return None


# ══════════════════════════════════════════════════════════════════════
# TEST 3: Conversational Agent with RAG
# ══════════════════════════════════════════════════════════════════════

def test_conversational_with_rag(doc_name):
    print_test("Conversational Agent with RAG (Document Queries)")
    
    # Test queries that should trigger RAG
    test_queries = [
        f"What is in the {doc_name} document?",
        "Tell me about this PDF",
        "What does the manual say about maintenance?",
        "Explain the specifications in the document"
    ]
    
    for query in test_queries:
        print_info(f"\nQuery: '{query}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/agents/chat",
                json={
                    "message": query,
                    "session_id": TEST_SESSION_ID
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '')
                metadata = data.get('metadata', {})
                sources_count = metadata.get('sources_count', 0)
                
                print_success(f"Response received ({len(answer)} chars)")
                print_info(f"  Answer preview: {answer[:150]}...")
                print_info(f"  Sources found: {sources_count}")
                
                if sources_count > 0:
                    print_success("RAG citations included ✓")
                else:
                    print_error("No RAG sources - RAG may not have triggered")
            else:
                print_error(f"Status {response.status_code}")
                
        except Exception as e:
            print_error(f"Error: {str(e)}")
        
        time.sleep(1)  # Rate limiting


# ══════════════════════════════════════════════════════════════════════
# TEST 4: Conversation History / Follow-up Questions
# ══════════════════════════════════════════════════════════════════════

def test_conversation_history():
    print_test("Conversation History & Follow-up Questions")
    
    conversation = [
        "What equipment types do you monitor?",
        "Tell me more about the first one",  # Follow-up - should use history
        "What sensors does it have?",  # Another follow-up
    ]
    
    session_id = f"history_test_{int(time.time())}"
    
    for i, query in enumerate(conversation, 1):
        print_info(f"\nMessage {i}: '{query}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/agents/chat",
                json={
                    "message": query,
                    "session_id": session_id  # Same session for all
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '')
                agents_used = data.get('metadata', {}).get('agents_used', [])
                
                print_success(f"Response received ({len(answer)} chars)")
                print_info(f"  Agents: {agents_used}")
                print_info(f"  Answer: {answer[:120]}...")
                
                # For follow-ups, check if answer makes sense contextually
                if i > 1 and ("first" in query.lower() or "it" in query.lower()):
                    if len(answer) > 20 and "don't" not in answer.lower():
                        print_success("Follow-up handled with context ✓")
                    else:
                        print_error("Follow-up may have lost context")
            else:
                print_error(f"Status {response.status_code}")
                
        except Exception as e:
            print_error(f"Error: {str(e)}")
        
        time.sleep(1)


# ══════════════════════════════════════════════════════════════════════
# TEST 5: Document Query Keywords
# ══════════════════════════════════════════════════════════════════════

def test_document_keywords():
    print_test("Document-Related Keywords Trigger RAG")
    
    # These should all trigger RAG even without equipment keywords
    keywords_queries = [
        ("pdf", "What's in this PDF?"),
        ("document", "Summarize the document"),
        ("manual", "What does the manual recommend?"),
        ("file", "Analyze the uploaded file"),
        ("specification", "Show me the specifications"),
    ]
    
    for keyword, query in keywords_queries:
        print_info(f"\nKeyword: '{keyword}' - Query: '{query}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/agents/chat",
                json={
                    "message": query,
                    "session_id": f"keyword_test_{keyword}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                sources_count = data.get('metadata', {}).get('sources_count', 0)
                
                if sources_count > 0:
                    print_success(f"Keyword '{keyword}' triggered RAG ({sources_count} sources)")
                else:
                    print_error(f"Keyword '{keyword}' did NOT trigger RAG")
            else:
                print_error(f"Status {response.status_code}")
                
        except Exception as e:
            print_error(f"Error: {str(e)}")
        
        time.sleep(0.5)


# ══════════════════════════════════════════════════════════════════════
# TEST 6: Streaming Endpoint
# ══════════════════════════════════════════════════════════════════════

def test_streaming():
    print_test("Streaming Chat Endpoint")
    
    query = "What equipment do you monitor?"
    
    print_info(f"Query: '{query}'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/agents/chat/stream",
            json={
                "message": query,
                "session_id": f"stream_test_{int(time.time())}"
            },
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print_success("Streaming started")
            
            chunks_received = 0
            total_chars = 0
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        chunks_received += 1
                        # Count characters (rough estimate)
                        total_chars += len(line_str)
            
            print_success(f"Streaming complete - {chunks_received} chunks, ~{total_chars} bytes")
        else:
            print_error(f"Streaming failed - Status {response.status_code}")
            
    except Exception as e:
        print_error(f"Streaming error: {str(e)}")


# ══════════════════════════════════════════════════════════════════════
# TEST 7: Equipment Diagnostics
# ══════════════════════════════════════════════════════════════════════

def test_diagnostics():
    print_test("Equipment Diagnostics")
    
    # Get equipment list first
    try:
        response = requests.get(f"{BASE_URL}/api/sensors/equipment", timeout=10)
        if response.status_code == 200:
            equipment = response.json()
            if equipment:
                test_eq = equipment[0]
                eq_id = test_eq.get('equipment_id')
                eq_type = test_eq.get('equipment_type')
                
                print_success(f"Found equipment: {eq_type} ({eq_id})")
                
                # Test anomaly detection
                print_info("\nTesting anomaly detection...")
                response = requests.post(
                    f"{BASE_URL}/api/agents/check-anomalies",
                    json={
                        "equipment_id": eq_id,
                        "equipment_type": eq_type,
                        "sensor_data": {
                            "temperature_c": 95.0,
                            "pressure_bar": 5.2,
                            "vibration_mm_s": 8.1,
                            "current_a": 45.0,
                            "rpm": 1450
                        }
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    anomalies = data.get('metadata', {}).get('anomalies_detected', 0)
                    print_success(f"Anomaly check complete - {anomalies} anomalies detected")
                else:
                    print_error(f"Anomaly check failed - Status {response.status_code}")
            else:
                print_error("No equipment found")
        else:
            print_error(f"Equipment list failed - Status {response.status_code}")
            
    except Exception as e:
        print_error(f"Diagnostics error: {str(e)}")


# ══════════════════════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  ALLOY AGENT - COMPREHENSIVE FEATURE TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Base URL: {BASE_URL}{RESET}")
    print(f"{YELLOW}Test Session: {TEST_SESSION_ID}{RESET}\n")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print_error("Backend is not responding correctly")
            sys.exit(1)
    except Exception as e:
        print_error(f"Cannot connect to backend at {BASE_URL}")
        print_error(f"Error: {str(e)}")
        print_info("\nMake sure backend is running:")
        print_info("  cd backend && python -m backend.src.api.main")
        sys.exit(1)
    
    print_success("Backend is running ✓\n")
    
    # Run all tests
    test_health_checks()
    
    doc_result = test_rag_upload()
    
    if doc_result:
        doc_id, doc_name = doc_result
        test_conversational_with_rag(doc_name)
    else:
        print_error("\nSkipping RAG tests - no documents found")
    
    test_conversation_history()
    test_document_keywords()
    test_streaming()
    test_diagnostics()
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  TEST SUITE COMPLETE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"\n{GREEN}All manual verification complete!{RESET}")
    print(f"{YELLOW}Check output above for any {RED}✗{YELLOW} failures{RESET}\n")


if __name__ == "__main__":
    main()
