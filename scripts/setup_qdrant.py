"""
Production Script: Initialize and verify Qdrant collections
Run this once to setup vector database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.src.rag import get_vector_store, validate_config

def main():
    """Initialize Qdrant collections and verify connection"""
    
    print("=" * 60)
    print("QDRANT SETUP - Alloy-Agent")
    print("=" * 60)
    
    # Step 1: Validate configuration
    print("\n[1/3] Validating configuration...")
    try:
        validate_config()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Step 2: Connect to Qdrant
    print("\n[2/3] Connecting to Qdrant Cloud...")
    try:
        vector_store = get_vector_store()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  - Verify QDRANT_URL in .env")
        print("  - Verify QDRANT_API_KEY in .env")
        print("  - Check internet connection")
        return False
    
    # Step 3: Verify collections exist
    print("\n[3/3] Verifying collections...")
    from backend.src.rag.config import (
        COLLECTION_MANUALS, COLLECTION_SOPS,
        COLLECTION_LOGS, COLLECTION_FAULTS
    )
    
    collections = [COLLECTION_MANUALS, COLLECTION_SOPS, COLLECTION_LOGS, COLLECTION_FAULTS]
    verified = 0
    
    for collection in collections:
        try:
            # Use collection_exists which works with our API key
            if vector_store.collection_exists(collection):
                verified += 1
        except:
            pass
    
    if verified == 4:
        print(f"✓ All 4 collections verified")
    else:
        print(f"⚠️  Only {verified}/4 collections found")
    
    # Verify collections
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    from backend.src.rag.config import (
        COLLECTION_MANUALS, COLLECTION_SOPS,
        COLLECTION_LOGS, COLLECTION_FAULTS
    )
    
    collections = [
        COLLECTION_MANUALS,
        COLLECTION_SOPS,
        COLLECTION_LOGS,
        COLLECTION_FAULTS
    ]
    
    all_exist = True
    for collection in collections:
        try:
            if vector_store.collection_exists(collection):
                info = vector_store.get_collection_info(collection)
                print(f"✓ {collection:25} | {info['points_count']} documents")
            else:
                print(f"❌ {collection:25} | NOT FOUND")
                all_exist = False
        except Exception as e:
            print(f"❌ {collection:25} | Error: {e}")
            all_exist = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_exist:
        print("✅ SUCCESS: Qdrant setup complete!")
        print("\nNext steps:")
        print("  1. Run: python scripts/upload_data.py")
        print("  2. Add knowledge documents to data/raw/manuals/")
        print("  3. Add SOPs to data/raw/sops/")
    else:
        print("⚠️  Some collections missing. Check errors above.")
    print("=" * 60)
    
    return all_exist

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
