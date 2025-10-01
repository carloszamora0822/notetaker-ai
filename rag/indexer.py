"""
RAG Indexer - Model initialization and vector store setup
"""
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import chromadb
import yaml
from sentence_transformers import SentenceTransformer

# Import shared state instead of module-level globals
import rag.state as state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load configuration from app.yaml, use defaults if not found"""
    config_path = Path(__file__).parent.parent / "config" / "app.yaml"
    
    # Default configuration
    default_config = {
        "rag": {
            "model_path": "rag/models/bge-small-en-v1.5",
            "chunk_size": 500,
            "chunk_overlap": 50,
            "index_path": "rag/index/chroma",
            "collection_name": "notes",
            "max_results": 8
        }
    }
    
    if config_path.exists():
        try:
            config = yaml.safe_load(config_path.read_text())
            logger.info(f"[OK] Config loaded from: {config_path}")
            return config
        except Exception as e:
            logger.warning(f"[WARN] Failed to load config: {e}, using defaults")
            return default_config
    else:
        logger.warning(f"[WARN] Config not found at {config_path}, using defaults")
        return default_config


def verify_and_load_model() -> bool:
    """Verify model folder exists and load the embedding model"""
    try:
        cfg = load_config()
        state.config = cfg
        model_path_str = cfg["rag"]["model_path"]
        model_path = Path(model_path_str).resolve()
        
        if not model_path.exists():
            logger.error(f"\n[!] Missing model at: {model_path}")
            logger.error("Place 'bge-small-en-v1.5' folder in rag/models/")
            logger.error("\nTo download the model, run:")
            logger.error("  from sentence_transformers import SentenceTransformer")
            logger.error("  model = SentenceTransformer('BAAI/bge-small-en-v1.5')")
            logger.error("  model.save('rag/models/bge-small-en-v1.5')\n")
            return False
        
        logger.info(f"[OK] Model folder present: {model_path}")
        
        # Load the model into shared state
        logger.info("Loading embedding model...")
        state.model = SentenceTransformer(str(model_path))
        embedding_dim = state.model.get_sentence_embedding_dimension()
        logger.info(f"[OK] Model loaded: {embedding_dim} dims")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to load model: {e}")
        return False


def initialize_vector_store() -> bool:
    """Initialize Chroma vector store"""
    try:
        cfg = state.config if state.config else load_config()
        # Use index path from config or default
        index_path_str = cfg["rag"].get("index_path", "rag/index/chroma")
        index_path = Path(index_path_str)
        index_path.mkdir(parents=True, exist_ok=True)
        
        collection_name = cfg["rag"].get("collection_name", "notes")
        
        logger.info(f"Initializing vector store at: {index_path}")
        state.client = chromadb.PersistentClient(path=str(index_path))
        state.collection = state.client.get_or_create_collection(name=collection_name)
        
        doc_count = state.collection.count()
        logger.info(f"[OK] Vector store ready: {doc_count} documents")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize vector store: {e}")
        return False


def update_status(error: Optional[str] = None):
    """Write status file to logs/rag_status.json"""
    try:
        # Create logs directory if it doesn't exist
        logs_path = Path(__file__).parent.parent / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "model_loaded": state.model is not None,
            "index_size": state.collection.count() if state.collection else 0,
            "ready": state.model is not None and state.collection is not None,
            "last_error": error
        }
        
        status_file = logs_path / "rag_status.json"
        status_file.write_text(json.dumps(status, indent=2))
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to write status file: {e}")


def run_status_updater(interval: int = 30):
    """Continuously update status file every interval seconds"""
    logger.info(f"Starting status updater (interval: {interval}s)")
    
    while True:
        try:
            update_status()
            time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Status updater stopped")
            break
        except Exception as e:
            logger.error(f"[ERROR] Status updater error: {e}")
            time.sleep(interval)


def initialize_rag_system():
    """Initialize the complete RAG system"""
    logger.info("🧠 RAG System Initialization Starting...")
    
    # Task 1: Verify model folder
    if not verify_and_load_model():
        update_status(error="Model failed to load")
        return False
    
    # Task 3: Initialize Chroma vector store
    if not initialize_vector_store():
        update_status(error="Vector store initialization failed")
        return False
    
    # Task 4: Write initial status
    update_status()
    
    logger.info("✅ RAG System Initialization Complete!")
    return True


def main():
    """Main entry point"""
    try:
        # Initialize the system
        if not initialize_rag_system():
            logger.error("❌ RAG System initialization failed")
            exit(1)
        
        # Run status updater loop
        logger.info("Running status updater...")
        run_status_updater(interval=30)
        
    except KeyboardInterrupt:
        logger.info("\n👋 RAG Indexer shutting down...")
        update_status()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        update_status(error=str(e))
        exit(1)


if __name__ == "__main__":
    main()
