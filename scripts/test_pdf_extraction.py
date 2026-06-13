"""
Test PDF extraction quality on all manuals
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.src.rag import get_document_processor

def test_single_pdf(pdf_path: Path, processor):
    """Test extraction on a single PDF"""
    print("\n" + "="*80)
    print(f"Testing: {pdf_path.name}")
    print("="*80)
    
    try:
        # Extract text
        text = processor.extract_pdf_text(pdf_path)
        
        # Show stats
        print(f"\n📊 Extraction Stats:")
        print(f"  Total characters: {len(text):,}")
        print(f"  Estimated pages: {text.count('--- Page')}")
        print(f"  Tables detected: {text.count('**Table')}")
        print(f"  Estimated tokens: {len(text) // 4:,}")
        
        # Show first 500 chars
        print(f"\n📄 First 500 characters:")
        print("-" * 80)
        print(text[:500])
        print("-" * 80)
        
        # Show tables if any
        if "**Table" in text:
            print(f"\n📊 Sample table (first occurrence):")
            print("-" * 80)
            table_start = text.find("**Table")
            table_section = text[table_start:table_start + 500]
            print(table_section)
            print("-" * 80)
        
        # Test chunking
        chunks = processor.chunk_text(text, {'source': pdf_path.name})
        print(f"\n🔪 Chunking Results:")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Avg chunk size: {sum(c['tokens'] for c in chunks) // len(chunks) if chunks else 0} tokens")
        print(f"  First chunk preview:")
        print("-" * 80)
        if chunks:
            print(chunks[0]['text'][:300] + "...")
        print("-" * 80)
        
        return True, len(text), len(chunks)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, 0, 0

def main():
    """Test all PDFs in manuals directory"""
    print("="*80)
    print("PDF EXTRACTION QUALITY TEST")
    print("="*80)
    
    manuals_dir = project_root / "data" / "raw" / "manuals"
    
    if not manuals_dir.exists():
        print(f"❌ Directory not found: {manuals_dir}")
        return
    
    pdf_files = sorted(list(manuals_dir.glob("*.pdf")))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {manuals_dir}")
        return
    
    print(f"\n📚 Found {len(pdf_files)} PDF files")
    print(f"📁 Directory: {manuals_dir}")
    
    # Initialize processor
    processor = get_document_processor()
    
    # Test first 3 PDFs (sample)
    print(f"\n🔬 Testing first 3 PDFs (sample)...")
    
    results = []
    for i, pdf_path in enumerate(pdf_files[:3], 1):
        success, text_len, num_chunks = test_single_pdf(pdf_path, processor)
        results.append({
            'file': pdf_path.name,
            'success': success,
            'text_length': text_len,
            'num_chunks': num_chunks
        })
        
        if i < 3:
            input(f"\n✋ Press Enter to test next PDF...")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['file']}")
        if r['success']:
            print(f"    {r['text_length']:,} chars → {r['num_chunks']} chunks")
    
    successful = sum(1 for r in results if r['success'])
    print(f"\n✅ Success: {successful}/{len(results)} PDFs")
    
    # List remaining PDFs
    if len(pdf_files) > 3:
        print(f"\n📋 Remaining {len(pdf_files) - 3} PDFs (not tested):")
        for pdf in pdf_files[3:]:
            print(f"  • {pdf.name}")
    
    print("\n💡 All PDFs look good? Run upload_data.py to ingest into Qdrant!")

if __name__ == "__main__":
    main()
