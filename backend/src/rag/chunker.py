"""
Production-grade chunker for industrial maintenance documents.

Strategy: Hierarchical Semantic Chunking
-----------------------------------------
1. Respect document structure (headings become chunk boundaries)
2. Semantic overlap: each chunk knows its parent heading context
3. Preserve bbox from ALL source elements → enables citation highlighting
4. Chunk metadata includes: page_num, bboxes, source_elements, doc_id

Why this beats naive fixed-size chunking:
- "Bearing inspection procedure" + "Step 1" in same chunk, not split
- Parent heading injected as context prefix (boosts retrieval)
- Table rows kept together
- Overlap carries the last sentence from previous chunk
"""

import re
import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional
import logging

from backend.src.rag.pdf_extractor import DocumentElement

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """
    A retrieval unit ready for embedding and vector storage.
    """
    chunk_id: str                       # stable hash-based ID
    doc_id: str
    doc_name: str

    # ── Content ──────────────────────────────────────────────────────────────
    text: str                           # the actual chunk text
    context_prefix: str                 # heading context prepended for embedding
    text_for_embedding: str             # context_prefix + text

    # ── Citation metadata ────────────────────────────────────────────────────
    page_nums: list[int]               # pages this chunk spans
    bboxes: list[dict]                 # [{page: N, bbox: [x0,y0,x1,y1], bbox_norm: [...]}]
    source_element_ids: list[str]      # which extracted elements make up this chunk

    # ── Document structure ───────────────────────────────────────────────────
    section_heading: str               # nearest parent heading
    section_depth: int                 # heading depth (H1=1, H2=2, ...)
    chunk_index: int                   # position within document
    element_types: list[str]           # mix of "text", "heading", "figure_caption"

    # ── Search metadata ──────────────────────────────────────────────────────
    metadata: dict = field(default_factory=dict)

    def to_qdrant_payload(self) -> dict:
        """Serialize for Qdrant point payload."""
        d = asdict(self)
        # Qdrant payload must be flat-ish; nest only what's needed
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "doc_name": self.doc_name,
            "text": self.text,
            "context_prefix": self.context_prefix,
            "page_nums": self.page_nums,
            "bboxes": self.bboxes,          # ← frontend uses this for highlighting
            "source_element_ids": self.source_element_ids,
            "section_heading": self.section_heading,
            "section_depth": self.section_depth,
            "chunk_index": self.chunk_index,
            "element_types": self.element_types,
            **self.metadata,
        }


class HierarchicalChunker:
    """
    Chunks DocumentElements using heading-aware grouping + token-based splitting.

    Algorithm:
    1. Walk elements in reading order
    2. On heading: flush current chunk, update context stack
    3. Accumulate text until MAX_TOKENS exceeded
    4. On overflow: split with OVERLAP tokens carried forward
    5. Each chunk embeds as: "[SECTION: {heading}]\n{text}"
    """

    MAX_TOKENS = 400          # ~300 words, safe for most embedding models
    OVERLAP_TOKENS = 60       # ~45 words carried into next chunk
    MIN_CHUNK_TOKENS = 40     # don't create tiny orphan chunks

    # Rough token estimate: 1 token ≈ 4 chars
    CHARS_PER_TOKEN = 4

    def __init__(
        self,
        max_tokens: int = MAX_TOKENS,
        overlap_tokens: int = OVERLAP_TOKENS,
    ):
        self.max_chars = max_tokens * self.CHARS_PER_TOKEN
        self.overlap_chars = overlap_tokens * self.CHARS_PER_TOKEN
        self.min_chars = self.MIN_CHUNK_TOKENS * self.CHARS_PER_TOKEN

    # ─────────────────────────────────────────────────────────────────────────

    def chunk(self, elements: list[DocumentElement]) -> list[Chunk]:
        """Main entry point."""
        chunks: list[Chunk] = []
        heading_stack: list[str] = []   # [H1, H2, H3]
        current_elements: list[DocumentElement] = []
        chunk_index = 0

        for elem in elements:
            if elem.is_heading():
                # Flush accumulated elements as chunk(s)
                if self._has_content(current_elements):
                    new_chunks = self._flush(
                        current_elements, heading_stack, chunk_index
                    )
                    chunks.extend(new_chunks)
                    chunk_index += len(new_chunks)

                # Update heading context
                heading_stack = self._update_heading_stack(heading_stack, elem)
                current_elements = []
            else:
                current_elements.append(elem)

        # Flush remainder
        if self._has_content(current_elements):
            new_chunks = self._flush(current_elements, heading_stack, chunk_index)
            chunks.extend(new_chunks)

        logger.info(f"Created {len(chunks)} chunks from {len(elements)} elements")
        return chunks

    # ─────────────────────────────────────────────────────────────────────────

    def _flush(
        self,
        elements: list[DocumentElement],
        heading_stack: list[str],
        start_index: int,
    ) -> list[Chunk]:
        """Convert a group of elements into one or more chunks."""
        context = self._build_context(heading_stack)
        full_text = "\n".join(e.text for e in elements)

        # If fits in one chunk
        if len(full_text) <= self.max_chars:
            chunk = self._make_chunk(elements, context, full_text, start_index)
            return [chunk] if chunk else []

        # Otherwise split by sentences with overlap
        return self._split_with_overlap(elements, context, full_text, start_index)

    def _split_with_overlap(
        self,
        elements: list[DocumentElement],
        context: str,
        full_text: str,
        start_index: int,
    ) -> list[Chunk]:
        """Sentence-boundary split with overlap, preserving element bbox mapping."""
        sentences = self._split_sentences(full_text)
        chunks = []
        current_sentences = []
        current_len = 0
        chunk_idx = start_index

        for sent in sentences:
            sent_len = len(sent)
            if current_len + sent_len > self.max_chars and current_sentences:
                # Flush current window
                window_text = " ".join(current_sentences)
                chunk = self._make_chunk(elements, context, window_text, chunk_idx)
                if chunk:
                    chunks.append(chunk)
                    chunk_idx += 1

                # Carry overlap: last N chars worth of sentences
                overlap_sents = self._get_overlap_sentences(current_sentences)
                current_sentences = overlap_sents + [sent]
                current_len = sum(len(s) for s in current_sentences)
            else:
                current_sentences.append(sent)
                current_len += sent_len

        # Final window
        if current_sentences:
            window_text = " ".join(current_sentences)
            chunk = self._make_chunk(elements, context, window_text, chunk_idx)
            if chunk:
                chunks.append(chunk)

        return chunks

    def _make_chunk(
        self,
        elements: list[DocumentElement],
        context: str,
        text: str,
        index: int,
    ) -> Optional["Chunk"]:
        text = text.strip()
        if len(text) < self.min_chars:
            return None

        # Get first element for doc_id / doc_name
        ref = elements[0]

        # Gather all bbox metadata from source elements
        bboxes = []
        seen_elem_ids = set()
        page_nums = set()
        elem_ids = []
        elem_types = []

        for elem in elements:
            # Only include elements whose text appears in this chunk window
            if elem.element_id not in seen_elem_ids and elem.text[:30] in text:
                bboxes.append({
                    "page": elem.page_num,
                    "bbox": elem.bbox,
                    "bbox_norm": elem.bbox_norm,
                    "element_id": elem.element_id,
                })
                seen_elem_ids.add(elem.element_id)
                page_nums.add(elem.page_num)
                elem_ids.append(elem.element_id)
                elem_types.append(elem.element_type)

        # Fallback: if text matching fails, use all element bboxes
        if not bboxes:
            for elem in elements:
                bboxes.append({
                    "page": elem.page_num,
                    "bbox": elem.bbox,
                    "bbox_norm": elem.bbox_norm,
                    "element_id": elem.element_id,
                })
                page_nums.add(elem.page_num)
                elem_ids.append(elem.element_id)
                elem_types.append(elem.element_type)

        text_for_embedding = f"{context}\n{text}" if context else text

        chunk_id = hashlib.sha256(
            f"{ref.doc_id}:{index}:{text[:100]}".encode()
        ).hexdigest()[:20]

        return Chunk(
            chunk_id=chunk_id,
            doc_id=ref.doc_id,
            doc_name=ref.doc_name,
            text=text,
            context_prefix=context,
            text_for_embedding=text_for_embedding,
            page_nums=sorted(page_nums),
            bboxes=bboxes,
            source_element_ids=elem_ids,
            section_heading=context.replace("[SECTION: ", "").rstrip("]") if context else "",
            section_depth=context.count(" > "),
            chunk_index=index,
            element_types=list(set(elem_types)),
            metadata={
                "source_file": ref.metadata.get("source_file", ""),
                "doc_name": ref.doc_name,
            },
        )

    # ─────────────────────────────────────────────────────────────────────────

    def _build_context(self, heading_stack: list[str]) -> str:
        if not heading_stack:
            return ""
        heading = " > ".join(h for h in heading_stack if h)
        return f"[SECTION: {heading}]"

    def _update_heading_stack(
        self, stack: list[str], heading_elem: DocumentElement
    ) -> list[str]:
        """Maintain heading hierarchy based on font size."""
        text = heading_elem.text.strip()
        # Simple heuristic: large font = H1, medium = H2, rest = H3
        sz = heading_elem.font_size
        if sz >= 18:
            return [text]
        elif sz >= 14:
            return [stack[0] if stack else "", text]
        else:
            base = stack[:2] if len(stack) >= 2 else stack + [""] * (2 - len(stack))
            return base + [text]

    def _has_content(self, elements: list[DocumentElement]) -> bool:
        return any(len(e.text.strip()) >= self.min_chars for e in elements)

    def _split_sentences(self, text: str) -> list[str]:
        """Split on sentence boundaries, keeping delimiters."""
        pattern = r'(?<=[.!?])\s+'
        parts = re.split(pattern, text)
        return [p.strip() for p in parts if p.strip()]

    def _get_overlap_sentences(self, sentences: list[str]) -> list[str]:
        """Return last N sentences that fit in overlap budget."""
        overlap = []
        total = 0
        for s in reversed(sentences):
            if total + len(s) > self.overlap_chars:
                break
            overlap.insert(0, s)
            total += len(s)
        return overlap


def chunk_elements(
    elements: list[DocumentElement],
    max_tokens: int = 400,
    overlap_tokens: int = 60,
) -> list[Chunk]:
    chunker = HierarchicalChunker(max_tokens=max_tokens, overlap_tokens=overlap_tokens)
    return chunker.chunk(elements)


def save_chunks(chunks: list[Chunk], output_path: str):
    with open(output_path, "w") as f:
        json.dump([asdict(c) for c in chunks], f, indent=2)
    logger.info(f"Saved {len(chunks)} chunks → {output_path}")
