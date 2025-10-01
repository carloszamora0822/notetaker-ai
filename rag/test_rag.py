"""
Simple test script for RAG functionality
"""
import logging

logging.basicConfig(level=logging.INFO)

# Test imports
try:
    print("Testing imports...")
    from rag.search import get_status, index_document, search
    print("✅ All imports successful!")
    
    # Test get_status (should work even without model)
    print("\nTesting get_status()...")
    status = get_status()
    print(f"Status: {status}")
    
    print("\n" + "="*50)
    print("BASIC TESTS PASSED")
    print("="*50)
    print("\nNote: To fully test the system, you need to:")
    print("1. Download the embedding model to rag/models/bge-small-en-v1.5/")
    print("2. Run: python rag/indexer.py")
    print("3. Test search and index_document functions")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
