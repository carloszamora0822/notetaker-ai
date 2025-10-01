#!/usr/bin/env python3
"""Integration tests across components"""

import requests
import json
from pathlib import Path
import time
import sys

BASE_URL = "http://localhost:8000"


def test_health():
    """Test backend health endpoint"""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data.get("ok") == True, "Health check should return ok=True"
        print("✓ Health check passed")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Health check failed: Cannot connect to backend")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_ingest():
    """Test file upload"""
    try:
        files = {"file": ("test.txt", b"Test content for integration test", "text/plain")}
        data = {"class_code": "TEST"}

        resp = requests.post(f"{BASE_URL}/ingest", files=files, data=data, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        result = resp.json()
        assert "stored" in result or "success" in result, "Response should indicate success"
        print("✓ Ingest test passed")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Ingest test failed: Cannot connect to backend")
        return False
    except Exception as e:
        print(f"❌ Ingest test failed: {e}")
        return False


def test_rag_query():
    """Test RAG search"""
    try:
        payload = {"q": "test query", "scope": "all"}
        resp = requests.post(f"{BASE_URL}/rag/query", json=payload, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        result = resp.json()
        assert "answer" in result or "results" in result, "Response should contain answer or results"
        print("✓ RAG query test passed")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ RAG query test failed: Cannot connect to backend")
        return False
    except Exception as e:
        print(f"❌ RAG query test failed: {e}")
        return False


def test_latex_pipeline():
    """Test LaTeX generation"""
    try:
        queue_dir = Path("latex/queue")
        queue_dir.mkdir(parents=True, exist_ok=True)
        
        input_file = queue_dir / "test_input.json"
        input_data = {
            "summary": "# Test Summary\n\nThis is a test summary for LaTeX generation.",
            "metadata": {
                "class_code": "TEST",
                "date": "2025-09-30",
                "title": "Integration Test"
            },
            "output_name": "test_integration"
        }
        input_file.write_text(json.dumps(input_data, indent=2))
        print("  Created test input file, waiting for LaTeX processing...")

        # Wait for processing (max 10 seconds)
        result_file = queue_dir / "test_result.json"
        max_wait = 10
        waited = 0
        
        while waited < max_wait:
            if result_file.exists():
                result = json.loads(result_file.read_text())
                if result.get("success"):
                    print("✓ LaTeX pipeline test passed")
                    # Clean up
                    input_file.unlink(missing_ok=True)
                    result_file.unlink(missing_ok=True)
                    return True
                else:
                    print(f"❌ LaTeX pipeline test failed: {result.get('error', 'Unknown error')}")
                    return False
            time.sleep(1)
            waited += 1
        
        print("⚠️  LaTeX pipeline test timeout (LaTeX service may not be running)")
        input_file.unlink(missing_ok=True)
        return False
        
    except Exception as e:
        print(f"❌ LaTeX pipeline test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("==> Running Integration Tests")
    print("")
    
    tests = [
        ("Health Check", test_health),
        ("File Ingest", test_ingest),
        ("RAG Query", test_rag_query),
        ("LaTeX Pipeline", test_latex_pipeline)
    ]

    results = []
    for name, test_func in tests:
        print(f"Running {name}...")
        result = test_func()
        results.append(result)
        print("")

    print("==> Test Summary")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All integration tests passed")
        return 0
    else:
        print("\n❌ Some integration tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
