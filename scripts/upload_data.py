"""
Upload knowledge base documents to Qdrant
Processes PDFs, markdown files, and JSONL data
"""

import sys
from pathlib import Path
import json
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.src.rag import (
    get_vector_store, 
    get_embedder, 
    get_document_processor,
    COLLECTION_DOCUMENTS,
    COLLECTION_CHUNKS
)

def upload_historical_logs():
    """Upload training data as historical maintenance logs"""
    print("\n" + "="*60)
    print("UPLOADING HISTORICAL LOGS")
    print("="*60)
    
    log_file = project_root / "data" / "training" / "train.jsonl"
    
    if not log_file.exists():
        print(f"❌ File not found: {log_file}")
        print("Note: Training data should be in Google Drive")
        return 0
    
    print(f"Reading: {log_file.name}")
    
    # Load logs
    logs = []
    with open(log_file, 'r') as f:
        for line in f:
            logs.append(json.loads(line))
    
    print(f"Loaded {len(logs)} maintenance records")
    
    processor = get_document_processor()
    embedder = get_embedder()
    vector_store = get_vector_store()
    
    total_uploaded = 0
    
    # Process first 100 logs for demo
    for i, log in enumerate(logs[:100]):
        document_id = f"log_{i:04d}"
        
        # Process log
        chunk = processor.process_maintenance_log(log)
        
        # Parent document metadata
        doc_metadata = {
            'document_type': 'historical_log',
            'equipment_type': log.get('metadata', {}).get('equipment_type', 'Unknown'),
            'log_index': i,
            'source': 'training_data'
        }
        
        # Generate embedding for the chunk
        embedding = embedder.embed_text(chunk['text'])
        
        # Upload as parent-child
        result = vector_store.add_document_with_chunks(
            document_id=document_id,
            document_metadata=doc_metadata,
            chunks_data=[{
                'text': chunk['text'],
                'embedding': embedding,
                'metadata': chunk['metadata']
            }]
        )
        
        total_uploaded += 1
        
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/100 logs...")
    
    print(f"✓ Uploaded {total_uploaded} historical logs")
    return total_uploaded

def upload_manuals():
    """Upload equipment manuals from PDFs"""
    print("\n" + "="*60)
    print("UPLOADING EQUIPMENT MANUALS")
    print("="*60)
    
    manuals_dir = project_root / "data" / "raw" / "manuals"
    
    if not manuals_dir.exists():
        print(f"❌ Directory not found: {manuals_dir}")
        return 0
    
    pdf_files = list(manuals_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {manuals_dir}")
        return 0
    
    print(f"Found {len(pdf_files)} PDF files")
    
    processor = get_document_processor()
    embedder = get_embedder()
    vector_store = get_vector_store()
    
    # Try to create collection (will skip if exists or 403)
    try:
        vector_store.create_collection(COLLECTION_CHUNKS)
    except Exception as e:
        print(f"⚠️  Collection setup issue: {e}")
        print(f"Attempting to proceed with upload anyway...")
    
    total_uploaded = 0
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        
        try:
            document_id = f"manual_{pdf_file.stem}"
            
            # Process PDF into chunks
            metadata = {
                'document_type': 'manual',
                'equipment_type': pdf_file.stem.replace('_', ' ').title()
            }
            chunks = processor.process_pdf(pdf_file, metadata)
            
            # Parent document metadata
            doc_metadata = {
                'document_type': 'equipment_manual',
                'equipment_type': metadata['equipment_type'],
                'filename': pdf_file.name,
                'source': str(pdf_file)
            }
            
            # Generate embeddings for all chunks
            texts = [c['text'] for c in chunks]
            embeddings = embedder.embed_batch(texts, batch_size=16)
            
            # Prepare chunks data
            chunks_data = [
                {
                    'text': chunks[i]['text'],
                    'embedding': embeddings[i],
                    'metadata': chunks[i]['metadata']
                }
                for i in range(len(chunks))
            ]
            
            # Upload as parent-child
            result = vector_store.add_document_with_chunks(
                document_id=document_id,
                document_metadata=doc_metadata,
                chunks_data=chunks_data
            )
            
            total_uploaded += 1
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
            continue
    
    return total_uploaded

def upload_sops():
    """Upload maintenance SOPs from markdown files"""
    print("\n" + "="*60)
    print("UPLOADING MAINTENANCE SOPs")
    print("="*60)
    
    sops_dir = project_root / "data" / "raw" / "sops"
    
    if not sops_dir.exists():
        print(f"❌ Directory not found: {sops_dir}")
        return 0
    
    md_files = list(sops_dir.glob("*.md"))
    
    if not md_files:
        print(f"❌ No markdown files found in {sops_dir}")
        return 0
    
    print(f"Found {len(md_files)} markdown files")
    
    processor = get_document_processor()
    embedder = get_embedder()
    vector_store = get_vector_store()
    
    # Collection should already exist from manuals upload
    # But try to create just in case
    try:
        vector_store.create_collection(COLLECTION_CHUNKS)
    except:
        pass  # Ignore errors, collection likely exists
    
    total_uploaded = 0
    
    for md_file in md_files:
        print(f"\nProcessing: {md_file.name}")
        
        try:
            document_id = f"sop_{md_file.stem}"
            
            # Process markdown into chunks
            chunks = processor.process_sop_markdown(md_file)
            
            # Parent document metadata
            doc_metadata = {
                'document_type': 'sop',
                'title': chunks[0]['metadata'].get('title', md_file.stem),
                'equipment_type': chunks[0]['metadata'].get('equipment_type', 'General'),
                'filename': md_file.name,
                'source': str(md_file)
            }
            
            # Generate embeddings
            texts = [c['text'] for c in chunks]
            embeddings = embedder.embed_batch(texts, batch_size=16)
            
            # Prepare chunks data
            chunks_data = [
                {
                    'text': chunks[i]['text'],
                    'embedding': embeddings[i],
                    'metadata': chunks[i]['metadata']
                }
                for i in range(len(chunks))
            ]
            
            # Upload as parent-child
            result = vector_store.add_document_with_chunks(
                document_id=document_id,
                document_metadata=doc_metadata,
                chunks_data=chunks_data
            )
            
            total_uploaded += 1
            
        except Exception as e:
            print(f"❌ Error processing {md_file.name}: {e}")
            continue
    
    return total_uploaded

def verify_collections():
    """Verify uploaded data"""
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    import requests
    from backend.src.rag.config import QDRANT_URL, QDRANT_API_KEY
    
    collections = [COLLECTION_DOCUMENTS, COLLECTION_CHUNKS]
    
    for collection in collections:
        try:
            response = requests.get(
                f"{QDRANT_URL}/collections/{collection}",
                headers={"api-key": QDRANT_API_KEY}
            )
            if response.status_code == 200:
                data = response.json()
                count = data['result']['points_count']
                print(f"✓ {collection:25} | {count:6} points")
            else:
                print(f"❌ {collection:25} | Error")
        except Exception as e:
            print(f"❌ {collection:25} | {str(e)[:40]}")

def main():
    """Main upload workflow"""
    print("="*60)
    print("ALLOY-AGENT: DATA UPLOAD TO QDRANT")
    print("="*60)
    print("\nℹ️  Skipping training data (already used for fine-tuning)")
    print("   Only uploading: Manuals + SOPs\n")
    
    # Skip historical logs (already used in fine-tuning)
    logs_count = 0
    
    # Upload manuals (if PDFs exist)
    manuals_count = upload_manuals()
    
    # Upload SOPs (if markdown files exist)
    sops_count = upload_sops()
    
    # Verify
    verify_collections()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Equipment Manuals: {manuals_count} documents")
    print(f"Maintenance SOPs: {sops_count} documents")
    print(f"Total: {manuals_count + sops_count} documents")
    print("="*60)
    
    if manuals_count + sops_count > 0:
        print("\n✅ SUCCESS: RAG knowledge base is ready!")
        print("\nKnowledge Base Contents:")
        print(f"  • {manuals_count} Equipment Manuals (technical specs, procedures)")
        print(f"  • {sops_count} Standard Operating Procedures")
        print("\nNext steps:")
        print("  1. Build agents: LLM client + RAG pipeline")
        print("  2. Test RAG retrieval: python scripts/test_rag_retrieval.py")
        print("  3. Build backend API")
        print("  4. Build React frontend")
    else:
        print("\n⚠️  WARNING: No data uploaded")

if __name__ == "__main__":
    main()
