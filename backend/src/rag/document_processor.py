"""
Document Processor: Production-Grade Document Parsing
Handles PDFs with tables, images, complex layouts using Docling + fallbacks

Features:
- Docling (IBM) for advanced PDF parsing
- Table extraction and conversion to markdown
- Image OCR for diagrams and charts
- Multiple fallback parsers
- Smart chunking with context preservation
"""

from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import json
import re
import io
import base64

# Core PDF processing
try:
    from docling.document_converter import DocumentConverter
    HAS_DOCLING = True
except ImportError:
    HAS_DOCLING = False
    print("Warning: Docling not installed. Using fallback parsers.")

try:
    import PyPDF2
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

# Table extraction
try:
    import tabula
    import camelot
    HAS_TABLE_EXTRACTION = True
except ImportError:
    HAS_TABLE_EXTRACTION = False
    print("Warning: Table extraction libraries not installed.")

# Image OCR
try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("Warning: OCR not available. Install: pip install pillow pytesseract")

from .config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNKS_PER_DOC


class DocumentProcessor:
    """Production-grade document processing with multiple parsing strategies"""
    
    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
        use_docling: bool = True,
        extract_tables: bool = True,
        ocr_images: bool = True
    ):
        """
        Initialize document processor
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            use_docling: Use Docling for PDF parsing (recommended)
            extract_tables: Extract and convert tables to markdown
            ocr_images: Use OCR on images
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_docling = use_docling and HAS_DOCLING
        self.extract_tables = extract_tables and HAS_TABLE_EXTRACTION
        self.ocr_images = ocr_images and HAS_OCR
        
        # Initialize Docling converter if available
        if self.use_docling:
            self.docling_converter = DocumentConverter()
            print("✓ Using Docling for advanced PDF parsing")
        else:
            print("⚠️  Docling not available, using fallback parsers")
    
    def extract_pdf_with_docling(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract PDF using Docling (best quality, handles tables/images)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with text, tables, images, and metadata
        """
        if not self.use_docling:
            raise ImportError("Docling not available")
        
        try:
            # Convert PDF
            result = self.docling_converter.convert(str(pdf_path))
            
            # Extract content
            doc_data = {
                'text': result.document.export_to_markdown(),  # Full text with tables as markdown
                'pages': len(result.pages) if hasattr(result, 'pages') else 0,
                'tables': [],
                'images': [],
                'metadata': {
                    'parser': 'docling',
                    'source': pdf_path.name
                }
            }
            
            # Extract tables separately if available
            if hasattr(result, 'tables'):
                for table in result.tables:
                    doc_data['tables'].append({
                        'markdown': table.export_to_markdown(),
                        'page': table.page_number if hasattr(table, 'page_number') else None
                    })
            
            return doc_data
            
        except Exception as e:
            print(f"Docling parsing failed: {e}")
            return None
    
    def extract_pdf_with_pdfplumber(self, pdf_path: Path) -> str:
        """
        Fallback: Extract text with pdfplumber (handles tables well)
        
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
        Fallback: Basic text extraction with PyPDF2
        
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
    
    def extract_tables_from_pdf(self, pdf_path: Path) -> List[str]:
        """
        Extract tables using specialized libraries
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of tables as markdown strings
        """
        if not self.extract_tables:
            return []
        
        tables_markdown = []
        
        # Try Camelot first (best for complex tables)
        try:
            tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='lattice')
            for table in tables:
                df = table.df
                tables_markdown.append(df.to_markdown(index=False))
        except Exception as e:
            print(f"Camelot failed: {e}, trying tabula...")
            
            # Fallback to Tabula
            try:
                tables = tabula.read_pdf(str(pdf_path), pages='all', multiple_tables=True)
                for df in tables:
                    tables_markdown.append(df.to_markdown(index=False))
            except Exception as e:
                print(f"Tabula also failed: {e}")
        
        return tables_markdown
    
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
        Main PDF extraction with cascading fallbacks
        
        Priority:
        1. Docling (best quality, tables, images)
        2. pdfplumber (good tables, decent text)
        3. PyPDF2 (basic text only)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text (with tables as markdown)
        """
        print(f"Extracting: {pdf_path.name}")
        
        # Try Docling first
        if self.use_docling:
            try:
                doc_data = self.extract_pdf_with_docling(pdf_path)
                if doc_data and doc_data['text']:
                    print(f"  ✓ Docling: {doc_data['pages']} pages, {len(doc_data['tables'])} tables")
                    return doc_data['text']
            except Exception as e:
                print(f"  ⚠️  Docling failed: {e}")
        
        # Fallback to pdfplumber
        if HAS_PDF:
            try:
                text = self.extract_pdf_with_pdfplumber(pdf_path)
                if text:
                    print(f"  ✓ pdfplumber: {len(text)} chars")
                    return text
            except Exception as e:
                print(f"  ⚠️  pdfplumber failed: {e}")
            
            # Last resort: PyPDF2
            try:
                text = self.extract_pdf_with_pypdf(pdf_path)
                print(f"  ✓ PyPDF2: {len(text)} chars (basic extraction)")
                return text
            except Exception as e:
                print(f"  ❌ All PDF parsers failed: {e}")
                raise
        
        raise ImportError("No PDF parsing libraries available")
    
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
