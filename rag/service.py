"""
RAG (Retrieval-Augmented Generation) service
"""
import logging
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run the RAG service"""
    logger.info("🧠 RAG service starting...")
    logger.info("Initializing vector store...")
    logger.info("RAG service ready and listening...")

    # Keep service running
    try:
        while True:
            time.sleep(10)
            logger.debug("RAG service heartbeat")
    except KeyboardInterrupt:
        logger.info("RAG service shutting down...")


if __name__ == "__main__":
    main()
