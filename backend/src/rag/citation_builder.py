"""
Citation Builder

Responsibility:
1. Format retrieved chunks as numbered context for the LLM prompt
2. Parse [1], [2] markers from LLM output
3. Build citation objects with page + bbox for frontend PDF highlighting

Frontend flow:
  User sees answer → "[See Ref 2, Page 4]" → clicks → PDF opens at page 4
  with yellow bounding box drawn over the exact paragraph.
"""

import re
from dataclasses import dataclass, field, asdict
from typing import Optional
import logging

from backend.src.rag.retriever import RetrievedChunk

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """A single citation reference attached to an answer span."""
    index: int               # [1], [2], ...
    doc_name: str
    doc_id: str
    chunk_id: str
    section_heading: str
    page_nums: list[int]
    bboxes: list[dict]       # [{page, bbox, bbox_norm}] — frontend uses for overlay
    text_snippet: str        # first 200 chars of the chunk
    rerank_score: float


@dataclass
class CitedAnswer:
    """The LLM's answer plus all citation metadata."""
    answer: str                          # raw answer text with [1][2] markers
    answer_html: str                     # answer with <cite> tags for rendering
    citations: list[Citation]
    sources_used: list[int]              # which [N] indices actually appear in answer


class CitationBuilder:
    """
    Wraps LLM calls with citation-aware prompting and output parsing.
    """

    SYSTEM_PROMPT = """You are an expert industrial maintenance AI for steel plant equipment.

Answer based ONLY on the provided context. When using information from a source, 
cite it inline as [1], [2], etc. matching the source number.

Rules:
- Be specific and technical. Use exact values from the context (temperatures, pressures, fault codes).
- If context doesn't contain the answer, say "This information is not available in the uploaded documents."
- Structure answers clearly: diagnosis → root cause → recommended action.
- Always cite the specific source for each claim.
- For step-by-step procedures, number each step.
"""

    def build_context_prompt(self, chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks as numbered context block for the LLM."""
        if not chunks:
            return "No relevant context found in the knowledge base."

        parts = ["CONTEXT SOURCES:\n"]
        for chunk in chunks:
            pages = ", ".join(str(p) for p in chunk.page_nums)
            parts.append(
                f"[{chunk.citation_index}] "
                f"Source: {chunk.doc_name} | "
                f"Section: {chunk.section_heading or 'General'} | "
                f"Page(s): {pages}\n"
                f"{chunk.text}\n"
            )

        return "\n---\n".join(parts)

    def build_full_prompt(
        self, query: str, chunks: list[RetrievedChunk]
    ) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) for the LLM."""
        context = self.build_context_prompt(chunks)
        user_prompt = f"{context}\n\nQUESTION: {query}\n\nProvide a detailed answer with citations [1], [2], etc.:"
        return self.SYSTEM_PROMPT, user_prompt

    def parse_citations(
        self, answer: str, chunks: list[RetrievedChunk]
    ) -> CitedAnswer:
        """
        Parse [N] markers in LLM output → Citation objects with bbox data.
        """
        chunk_map = {c.citation_index: c for c in chunks}

        # Find all [N] patterns used in the answer
        used_indices = list(set(
            int(m) for m in re.findall(r'\[(\d+)\]', answer)
            if int(m) in chunk_map
        ))

        citations = []
        for idx in sorted(used_indices):
            chunk = chunk_map[idx]
            citations.append(Citation(
                index=idx,
                doc_name=chunk.doc_name,
                doc_id=chunk.doc_id,
                chunk_id=chunk.chunk_id,
                section_heading=chunk.section_heading,
                page_nums=chunk.page_nums,
                bboxes=chunk.bboxes,
                text_snippet=chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                rerank_score=chunk.rerank_score,
            ))

        answer_html = self._render_citations_html(answer, chunk_map)

        return CitedAnswer(
            answer=answer,
            answer_html=answer_html,
            citations=citations,
            sources_used=used_indices,
        )

    def _render_citations_html(
        self, answer: str, chunk_map: dict[int, RetrievedChunk]
    ) -> str:
        """Replace [N] with clickable HTML citation badges."""
        def replace_citation(match):
            idx = int(match.group(1))
            if idx not in chunk_map:
                return match.group(0)
            chunk = chunk_map[idx]
            pages = ", ".join(str(p) for p in chunk.page_nums)
            return (
                f'<cite class="citation-badge" '
                f'data-citation-index="{idx}" '
                f'data-doc-id="{chunk.doc_id}" '
                f'data-page="{chunk.page_nums[0] if chunk.page_nums else 1}" '
                f'data-bboxes=\'{self._bbox_attr(chunk.bboxes)}\'>'
                f'[{idx}]</cite>'
            )

        return re.sub(r'\[(\d+)\]', replace_citation, answer)

    def _bbox_attr(self, bboxes: list[dict]) -> str:
        """JSON-serialize bboxes for data attribute."""
        import json
        return json.dumps(bboxes).replace("'", "&apos;")

    def format_sources_list(self, citations: list[Citation]) -> list[dict]:
        """
        Serializable list of sources for API response.
        Frontend renders this as the "Sources" panel.
        """
        return [
            {
                "index": c.index,
                "doc_name": c.doc_name,
                "doc_id": c.doc_id,
                "chunk_id": c.chunk_id,
                "section": c.section_heading,
                "pages": c.page_nums,
                "bboxes": c.bboxes,    # ← the gold: bbox coords per page
                "snippet": c.text_snippet,
                "score": round(c.rerank_score, 4),
            }
            for c in citations
        ]
