"""
Knowledge Loader Service
Loads historical incidents and spare parts into RAG system.
"""

import json
import logging
import csv
import uuid
from pathlib import Path
from typing import List, Dict, Any

from backend.src.rag.config import INCIDENTS_PATH, SPARE_PARTS_PATH
from backend.src.rag.embedder import get_embedder
from backend.src.rag.vector_store import get_vector_store
from backend.src.rag.config import COLLECTION_CHUNKS

logger = logging.getLogger(__name__)


class KnowledgeLoader:
    """Load historical knowledge into vector store."""
    
    def __init__(self):
        self.embedder = get_embedder()
        self.store = get_vector_store()
        self.loaded_flag = Path(__file__).parent.parent.parent / "data" / ".knowledge_loaded"
    
    def is_already_loaded(self) -> bool:
        """Check if knowledge has been loaded."""
        return self.loaded_flag.exists()
    
    def mark_as_loaded(self):
        """Mark knowledge as loaded."""
        self.loaded_flag.touch()
        logger.info("✓ Marked knowledge as loaded")
    
    def load_historical_incidents(self) -> int:
        """Load incidents.json into Qdrant."""
        if not INCIDENTS_PATH.exists():
            logger.warning(f"Incidents file not found: {INCIDENTS_PATH}")
            return 0
        
        with open(INCIDENTS_PATH, 'r') as f:
            incidents = json.load(f)
        
        logger.info(f"Loading {len(incidents)} historical incidents...")
        
        # Create document for incidents collection
        doc_id = str(uuid.uuid4())
        
        # Format each incident as a text chunk
        chunks = []
        embeddings = []
        metadatas = []
        
        for incident in incidents:
            text = (
                f"INCIDENT: {incident['incident_id']}\n"
                f"Date: {incident['date']}\n"
                f"Equipment: {incident['equipment']} ({incident.get('equipment_tag', 'unknown')})\n\n"
                f"SYMPTOMS:\n{incident['symptoms']}\n\n"
                f"ROOT CAUSE:\n{incident['root_cause']}\n\n"
                f"CONTRIBUTING FACTORS:\n{incident['contributing_factors']}\n\n"
                f"ACTION TAKEN:\n{incident['action_taken']}\n\n"
                f"DOWNTIME: {incident['downtime_hours']} hours\n\n"
                f"RECURRENCE PREVENTION:\n{incident['recurrence_prevention']}"
            )
            
            chunks.append(text)
            embeddings.append(self.embedder.embed(text))
            metadatas.append({
                "source": "historical_incidents",
                "doc_type": "incident_record",
                "equipment_tag": incident.get('equipment_tag', 'unknown'),
                "incident_id": incident['incident_id'],
                "incident_date": incident['date'],
                "page_number": 1,
                "bbox": None
            })
        
        # Upsert into vector store
        self.store.upsert_document_with_chunks(
            doc_id=doc_id,
            doc_metadata={
                "source": "historical_incidents.json",
                "doc_type": "incident_database",
                "title": "Historical Failure Database"
            },
            chunk_texts=chunks,
            chunk_embeddings=embeddings,
            chunk_metadatas=metadatas,
            chunks_collection=COLLECTION_CHUNKS
        )
        
        logger.info(f"✓ Loaded {len(incidents)} historical incidents into RAG")
        return len(incidents)
    
    def load_spare_parts_catalog(self) -> int:
        """Load spare_parts.csv into Qdrant."""
        if not SPARE_PARTS_PATH.exists():
            logger.warning(f"Spare parts file not found: {SPARE_PARTS_PATH}")
            return 0
        
        with open(SPARE_PARTS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            parts = list(reader)
        
        logger.info(f"Loading {len(parts)} spare parts...")
        
        doc_id = str(uuid.uuid4())
        chunks = []
        embeddings = []
        metadatas = []
        
        for part in parts:
            text = (
                f"PART: {part['part_name']}\n"
                f"Part Number: {part['part_number']}\n"
                f"Equipment Type: {part['equipment_type']}\n"
                f"Stock: {part['stock_quantity']} units (Min: {part['min_stock']})\n"
                f"Location: {part['warehouse_location']}\n"
                f"Unit Cost: ₹{part['unit_cost']}\n"
                f"Supplier: {part['supplier']}\n"
                f"Lead Time: {part['lead_time_days']} days"
            )
            
            chunks.append(text)
            embeddings.append(self.embedder.embed(text))
            metadatas.append({
                "source": "spare_parts_catalog",
                "doc_type": "spare_parts",
                "part_number": part['part_number'],
                "equipment_type": part['equipment_type'],
                "page_number": 1,
                "bbox": None
            })
        
        self.store.upsert_document_with_chunks(
            doc_id=doc_id,
            doc_metadata={
                "source": "spare_parts.csv",
                "doc_type": "parts_catalog",
                "title": "Spare Parts Inventory"
            },
            chunk_texts=chunks,
            chunk_embeddings=embeddings,
            chunk_metadatas=metadatas,
            chunks_collection=COLLECTION_CHUNKS
        )
        
        logger.info(f"✓ Loaded {len(parts)} spare parts into RAG")
        return len(parts)
    
    def load_all(self, force: bool = False) -> Dict[str, Any]:
        """Load all knowledge if not already loaded."""
        if self.is_already_loaded() and not force:
            logger.info("Knowledge already loaded (use force=True to reload)")
            return {
                "status": "skipped",
                "reason": "already_loaded",
                "incidents": 0,
                "spare_parts": 0
            }
        
        incidents_count = self.load_historical_incidents()
        parts_count = self.load_spare_parts_catalog()
        
        if not force:
            self.mark_as_loaded()
        
        return {
            "status": "loaded",
            "incidents": incidents_count,
            "spare_parts": parts_count
        }


# Singleton
_loader: KnowledgeLoader = None

def get_knowledge_loader() -> KnowledgeLoader:
    global _loader
    if _loader is None:
        _loader = KnowledgeLoader()
    return _loader
