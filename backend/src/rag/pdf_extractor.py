"""
Production-grade PDF extractor with bounding box tracking.
Every chunk stores: text, page_num, bbox (x0,y0,x1,y1), element_type.
This enables citation highlighting in the frontend.
"""

import fitz  # PyMuPDF
import json
import hashlib
import re
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentElement:
    """A single extracted element from a PDF page."""
    element_id: str          # sha256 of (doc_id + page + bbox)
    doc_id: str              # source document identifier
    doc_name: str            # human-readable filename
    page_num: int            # 1-indexed
    element_type: str        # "text" | "table" | "heading" | "figure_caption"
    text: str
    bbox: list[float]        # [x0, y0, x1, y1] in PDF points
    bbox_norm: list[float]   # normalized 0-1 for frontend rendering
    page_width: float
    page_height: float
    font_size: float = 0.0
    font_flags: int = 0      # bold=1, italic=2, etc.
    block_num: int = 0
    reading_order: int = 0
    metadata: dict = field(default_factory=dict)

    def is_heading(self) -> bool:
        return self.element_type == "heading"

    def is_bold(self) -> bool:
        return bool(self.font_flags & 2**4)  # fitz bold flag


@dataclass
class ExtractedPage:
    page_num: int
    width: float
    height: float
    elements: list[DocumentElement]
    raw_text: str


class PDFExtractor:
    """
    Layout-aware PDF extractor. Preserves:
    - Reading order (top-to-bottom, left-to-right with column detection)
    - Bounding boxes for every text block
    - Heading detection via font size heuristics
    - Table detection (basic — use Camelot for complex tables)
    - Per-page dimensions for frontend PDF viewer overlay
    """

    # Font size thresholds (relative to body text)
    HEADING_SIZE_RATIO = 1.15   # 15% larger than body = heading
    MIN_TEXT_LENGTH = 10        # skip tiny fragments

    def __init__(self, doc_id: Optional[str] = None):
        self.doc_id = doc_id

    def extract(self, pdf_path: str) -> list[DocumentElement]:
        path = Path(pdf_path)
        doc_name = path.stem
        doc_id = self.doc_id or hashlib.sha256(path.name.encode()).hexdigest()[:12]

        logger.info(f"Extracting: {path.name} (doc_id={doc_id})")

        doc = fitz.open(str(path))
        all_elements: list[DocumentElement] = []

        # Pass 1: collect all font sizes across doc to find body size
        all_font_sizes = []
        for page in doc:
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            for block in blocks:
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        sz = span.get("size", 0)
                        if sz > 0:
                            all_font_sizes.append(sz)

        body_font_size = self._estimate_body_size(all_font_sizes)
        logger.info(f"Estimated body font size: {body_font_size:.1f}pt")

        # Pass 2: extract elements with full metadata
        global_reading_order = 0
        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            pw, ph = page.rect.width, page.rect.height

            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

            # Sort blocks by reading order: top→bottom, with column awareness
            text_blocks = [b for b in blocks if b.get("type") == 0]
            sorted_blocks = self._sort_reading_order(text_blocks, pw)

            for block_idx, block in enumerate(sorted_blocks):
                block_bbox = block["bbox"]  # [x0, y0, x1, y1]
                block_text_parts = []
                dominant_size = 0.0
                dominant_flags = 0

                for line in block.get("lines", []):
                    line_texts = []
                    for span in line.get("spans", []):
                        t = span.get("text", "").strip()
                        if t:
                            line_texts.append(t)
                            sz = span.get("size", 0)
                            if sz > dominant_size:
                                dominant_size = sz
                                dominant_flags = span.get("flags", 0)
                    if line_texts:
                        block_text_parts.append(" ".join(line_texts))

                full_text = "\n".join(block_text_parts).strip()
                if len(full_text) < self.MIN_TEXT_LENGTH:
                    continue

                # Determine element type
                element_type = self._classify_element(
                    full_text, dominant_size, body_font_size, dominant_flags
                )

                # Generate stable element ID
                elem_id = hashlib.sha256(
                    f"{doc_id}:{page_num}:{block_bbox}:{full_text[:50]}".encode()
                ).hexdigest()[:16]

                # Normalize bbox to 0-1 for frontend
                bbox_norm = [
                    block_bbox[0] / pw,
                    block_bbox[1] / ph,
                    block_bbox[2] / pw,
                    block_bbox[3] / ph,
                ]

                elem = DocumentElement(
                    element_id=elem_id,
                    doc_id=doc_id,
                    doc_name=doc_name,
                    page_num=page_num,
                    element_type=element_type,
                    text=full_text,
                    bbox=list(block_bbox),
                    bbox_norm=bbox_norm,
                    page_width=pw,
                    page_height=ph,
                    font_size=dominant_size,
                    font_flags=dominant_flags,
                    block_num=block_idx,
                    reading_order=global_reading_order,
                    metadata={"source_file": path.name}
                )
                all_elements.append(elem)
                global_reading_order += 1

        doc.close()
        logger.info(f"Extracted {len(all_elements)} elements from {page_num} pages")
        return all_elements

    def _estimate_body_size(self, sizes: list[float]) -> float:
        """Find modal font size = body text size."""
        if not sizes:
            return 11.0
        from collections import Counter
        # Bucket to nearest 0.5pt
        bucketed = [round(s * 2) / 2 for s in sizes]
        return Counter(bucketed).most_common(1)[0][0]

    def _classify_element(
        self, text: str, font_size: float, body_size: float, flags: int
    ) -> str:
        is_bold = bool(flags & 2**4)
        is_large = font_size > body_size * self.HEADING_SIZE_RATIO

        if (is_large or is_bold) and len(text) < 200:
            return "heading"
        if text.lower().startswith(("figure", "fig.", "table", "note:")):
            return "figure_caption"
        return "text"

    def _sort_reading_order(self, blocks: list, page_width: float) -> list:
        """
        Multi-column aware reading order sort.
        Detects if page has 2 columns by checking if blocks cluster
        into left/right halves.
        """
        if not blocks:
            return blocks

        mid = page_width / 2
        left = [b for b in blocks if b["bbox"][0] < mid * 0.8]
        right = [b for b in blocks if b["bbox"][0] >= mid * 0.8]

        # If roughly equal split → 2-column layout
        if len(left) > 1 and len(right) > 1 and abs(len(left) - len(right)) < len(blocks) * 0.4:
            left_sorted = sorted(left, key=lambda b: b["bbox"][1])
            right_sorted = sorted(right, key=lambda b: b["bbox"][1])
            return left_sorted + right_sorted

        # Single column: just top-to-bottom
        return sorted(blocks, key=lambda b: (b["bbox"][1], b["bbox"][0]))


def extract_pdf_to_json(pdf_path: str, output_dir: str) -> str:
    """Convenience: extract and save to JSON sidecar file."""
    extractor = PDFExtractor()
    elements = extractor.extract(pdf_path)

    out_path = Path(output_dir) / (Path(pdf_path).stem + "_elements.json")
    with open(out_path, "w") as f:
        json.dump([asdict(e) for e in elements], f, indent=2)

    logger.info(f"Saved {len(elements)} elements → {out_path}")
    return str(out_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_pdf_to_json(sys.argv[1], ".")
        print(f"Output: {result}")
