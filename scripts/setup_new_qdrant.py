"""
Setup collections on new Qdrant cluster
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.src.rag import get_vector_store, COLLECTION_CHUNKS

def main():
    print("="*60)
    print("SETTING UP NEW QDRANT CLUSTER")
    print("="*60)
    
    try:
        # Connect
        vector_store = get_vector_store()
        
        # Create chunks collection (we only need this one now)
        print(f"\nCreating collection: {COLLECTION_CHUNKS}")
        vector_store.create_collection(COLLECTION_CHUNKS, vector_size=384)
        
        # Verify
        print(f"\n✅ Setup complete!")
        print(f"\nChecking collection info...")
        info = vector_store.get_collection_info(COLLECTION_CHUNKS)
        print(f"  Collection: {info['name']}")
        print(f"  Points: {info['points_count']}")
        print(f"  Status: {info['status']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
