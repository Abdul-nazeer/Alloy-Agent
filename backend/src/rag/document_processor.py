"""
Document Processor: Lightweight PDF Parsing (No GPU Required)
Handles PDFs with tables using PyPDF2 + pdfplumber

Features:
- PyPDF2 for basic text extraction
- pdfplumber for tables and complex layouts (CPU-only)
- Smart chunking with context preservation
- No GPU dependencies (production-ready for free hosting)
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import re

# Core PDF processing (lightweight, no GPU)
try:
    import PyPDF2
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("Warning: Install PDF libraries: pip install PyPDF2 pdfplumber")

from .config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNKS_PER_DOC


class DocumentProcessor:
    """Lightweight document processing (CPU-only, no GPU required)"""
    
    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
        extract_tables: bool = True
    ):
        """
        Initialize document processor
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            extract_tables: Extract and convert tables to markdown
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.extract_tables = extract_tables
        
        if not HAS_PDF:
            raise ImportError("Install: pip install PyPDF2 pdfplumber")
        
        print("✓ Document processor initialized (CPU-only, no GPU required)")
    
    def extract_pdf_with_pdfplumber(self, pdf_path: Path) -> str:
        """
        Extract text with pdfplumber (handles tables well, CPU-only)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                page_text = page.extract_text()
                if page_text:
                    text += f"\n\n--- Page {page_num} ---\n\n"
                    text += page_text
                
                # Extract tables as markdown
                if self.extract_tables:
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables, 1):
                        text += f"\n\n**Table {table_idx} (Page {page_num}):**\n"
                        text += self._table_to_markdown(table)
        
        return text.strip()
    
    def extract_pdf_with_pypdf(self, pdf_path: Path) -> str:
        """
        Basic text extraction with PyPDF2 (fallback)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n\n--- Page {page_num} ---\n\n"
                    text += page_text
        
        return text.strip()
    
    def _table_to_markdown(self, table: List[List[str]]) -> str:
        """Convert table array to markdown format"""
        if not table or not table[0]:
            return ""
        
        # Header
        markdown = "| " + " | ".join(str(cell) if cell else "" for cell in table[0]) + " |\n"
        markdown += "|" + "|".join([" --- " for _ in table[0]]) + "|\n"
        
        # Rows
        for row in table[1:]:
            markdown += "| " + " | ".join(str(cell) if cell else "" for cell in row) + " |\n"
        
        return markdown
    
    def extract_pdf_text(self, pdf_path: Path) -> str:
        """
        Main PDF extraction with fallback
        
        Priority:
        1. pdfplumber (good tables, decent text)
        2. PyPDF2 (basic text only)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text (with tables as markdown)
        """
        print(f"Extracting: {pdf_path.name}")
        
        # Try pdfplumber first
        try:
            text = self.extract_pdf_with_pdfplumber(pdf_path)
            if text:
                print(f"  ✓ pdfplumber: {len(text)} chars")
                return text
        except Exception as e:
            print(f"  ⚠️  pdfplumber failed: {e}")
        
        # Fallback to PyPDF2
        try:
            text = self.extract_pdf_with_pypdf(pdf_path)
            print(f"  ✓ PyPDF2: {len(text)} chars (basic extraction)")
            return text
        except Exception as e:
            print(f"  ❌ All PDF parsers failed: {e}")
            raise
    
    def extract_text_file(self, file_path: Path) -> str:
        """Extract text from text/markdown file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def extract_jsonl(self, jsonl_path: Path) -> List[Dict[str, Any]]:
        """Extract structured data from JSONL"""
        data = []
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        return data
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Smart chunking with context preservation
        Respects sentence boundaries and markdown structure
        
        Args:
            text: Input text
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunks with metadata
        """
        # Split by paragraphs first (preserve structure)
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Estimate tokens (rough: ~4 chars per token)
            para_tokens = len(para) // 4
            
            # Check if paragraph itself is too large
            if para_tokens > self.chunk_size:
                # Split large paragraph by sentences
                sentences = re.split(r'([.!?]\s+)', para)
                
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else "")
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    sentence_tokens = len(sentence) // 4
                    
                    if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                        # Save current chunk
                        chunks.append(self._create_chunk(current_chunk, metadata, current_tokens))
                        
                        # Start new chunk with overlap (last sentence for context)
                        overlap_match = re.search(r'[^.!?]*[.!?]\s*$', current_chunk)
                        overlap = overlap_match.group(0) if overlap_match else ""
                        current_chunk = overlap + sentence
                        current_tokens = len(overlap) // 4 + sentence_tokens
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
                        current_tokens += sentence_tokens
            else:
                # Paragraph fits, add it
                if current_tokens + para_tokens > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append(self._create_chunk(current_chunk, metadata, current_tokens))
                    
                    # Start new with this paragraph
                    current_chunk = para
                    current_tokens = para_tokens
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
                    current_tokens += para_tokens
            
            # Safety: prevent too many chunks
            if len(chunks) >= MAX_CHUNKS_PER_DOC:
                print(f"⚠️  Reached max chunks ({MAX_CHUNKS_PER_DOC}), truncating")
                break
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, metadata, current_tokens))
        
        return chunks
    
    def _create_chunk(self, text: str, metadata: Dict[str, Any], tokens: int) -> Dict[str, Any]:
        """Create chunk object with metadata"""
        chunk_metadata = metadata.copy() if metadata else {}
        chunk_metadata['chunk_size'] = tokens
        
        return {
            'text': text.strip(),
            'metadata': chunk_metadata,
            'tokens': tokens
        }
    
    def process_pdf(self, pdf_path: Path, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Process PDF file into chunks
        
        Args:
            pdf_path: Path to PDF
            metadata: Metadata for chunks
            
        Returns:
            List of chunks
        """
        print(f"Processing PDF: {pdf_path.name}")
        
        # Extract text (with tables as markdown)
        text = self.extract_pdf_text(pdf_path)
        
        # Add source to metadata
        if metadata is None:
            metadata = {}
        metadata['source'] = pdf_path.name
        metadata['source_type'] = 'pdf'
        metadata['file_size'] = pdf_path.stat().st_size
        
        # Chunk text
        chunks = self.chunk_text(text, metadata)
        
        print(f"  → Created {len(chunks)} chunks ({sum(c['tokens'] for c in chunks)} tokens total)")
        return chunks
    
    def process_maintenance_log(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process maintenance log entry into searchable chunk
        
        Args:
            log_entry: Log entry from training data
            
        Returns:
            Processed chunk
        """
        # Combine instruction, input, output with clear sections
        text = f"**Task:** {log_entry['instruction']}\n\n"
        text += f"**Equipment Data:**\n{log_entry['input']}\n\n"
        text += f"**Analysis:**\n{log_entry['output']}"
        
        # Extract metadata
        metadata = log_entry.get('metadata', {}).copy()
        metadata['source_type'] = 'maintenance_log'
        
        return {
            'text': text,
            'metadata': metadata,
            'tokens': len(text) // 4
        }
    
    def process_sop_markdown(self, md_path: Path) -> List[Dict[str, Any]]:
        """
        Process SOP markdown file
        
        Args:
            md_path: Path to markdown file
            
        Returns:
            List of chunks
        """
        print(f"Processing SOP: {md_path.name}")
        
        text = self.extract_text_file(md_path)
        
        # Extract title from first header
        title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        title = title_match.group(1) if title_match else md_path.stem
        
        # Extract equipment type from title or content
        equipment_match = re.search(r'(?:Equipment|System):\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        equipment = equipment_match.group(1).strip() if equipment_match else "General"
        
        metadata = {
            'source': md_path.name,
            'source_type': 'sop',
            'title': title,
            'equipment_type': equipment,
            'doc_category': 'procedure'
        }
        
        chunks = self.chunk_text(text, metadata)
        print(f"  → Created {len(chunks)} chunks")
        return chunks
    
    def process_directory(self, dir_path: Path, file_pattern: str = "*.pdf") -> List[Dict[str, Any]]:
        """
        Process all files in directory matching pattern
        
        Args:
            dir_path: Directory path
            file_pattern: Glob pattern for files
            
        Returns:
            All chunks from all files
        """
        all_chunks = []
        files = list(dir_path.glob(file_pattern))
        
        if not files:
            print(f"⚠️  No files matching '{file_pattern}' in {dir_path}")
            return all_chunks
        
        print(f"Processing {len(files)} files from {dir_path}...")
        
        for file_path in files:
            try:
                if file_pattern.endswith('.pdf'):
                    chunks = self.process_pdf(file_path)
                elif file_pattern.endswith('.md'):
                    chunks = self.process_sop_markdown(file_path)
                else:
                    print(f"Skipping unsupported file: {file_path.name}")
                    continue
                
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"  ❌ Failed to process {file_path.name}: {e}")
                continue
        
        print(f"✓ Total: {len(all_chunks)} chunks from {len(files)} files")
        return all_chunks


# Singleton instance
_processor_instance = None

def get_document_processor() -> DocumentProcessor:
    """Get singleton document processor instance"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = DocumentProcessor()
    return _processor_instance
