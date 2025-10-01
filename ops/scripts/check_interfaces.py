#!/usr/bin/env python3
"""Validate that all interfaces match API contracts"""

import sys
from pathlib import Path


def check_rag_interface():
    """Verify RAG has required structure"""
    rag_init = Path("rag/__init__.py")
    if not rag_init.exists():
        print("❌ rag/__init__.py not found")
        return False

    # Check if search.py will exist (Sprint 1)
    search_file = Path("rag/search.py")
    if not search_file.exists():
        print("⚠️  rag/search.py not yet created (OK for Sprint 0)")

    print("✓ RAG structure valid")
    return True


def check_latex_queue():
    """Verify LaTeX directories exist"""
    required_dirs = [
        Path("latex/queue"),
        Path("latex/output"),
        Path("latex/templates"),
        Path("latex/scripts"),
    ]

    for d in required_dirs:
        if not d.exists():
            print(f"❌ Missing directory: {d}")
            return False

    # Check compile script
    compile_script = Path("latex/scripts/compile_watch.sh")
    if not compile_script.exists():
        print("❌ latex/scripts/compile_watch.sh not found")
        return False

    if not compile_script.stat().st_mode & 0o111:
        print("❌ latex/scripts/compile_watch.sh not executable")
        return False

    print("✓ LaTeX structure valid")
    return True


def check_backend_endpoints():
    """Verify backend defines required files"""
    backend_file = Path("backend/app/main.py")
    if not backend_file.exists():
        print("❌ backend/app/main.py not found")
        return False

    content = backend_file.read_text()
    required_patterns = ["FastAPI", "@app"]

    for pattern in required_patterns:
        if pattern not in content:
            print(f"❌ Backend missing: {pattern}")
            return False

    print("✓ Backend structure valid")
    return True


def check_frontend_templates():
    """Verify frontend has templates"""
    base_template = Path("frontend/templates/base.html")
    if not base_template.exists():
        print("❌ frontend/templates/base.html not found")
        return False

    print("✓ Frontend structure valid")
    return True


def check_config():
    """Verify configuration exists"""
    config_file = Path("config/app.yaml")
    if not config_file.exists():
        print("❌ config/app.yaml not found")
        return False

    print("✓ Configuration valid")
    return True


def main():
    print("==> Checking interface contracts...")
    print("")

    checks = [
        ("Config", check_config),
        ("Backend", check_backend_endpoints),
        ("RAG", check_rag_interface),
        ("LaTeX", check_latex_queue),
        ("Frontend", check_frontend_templates),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            results.append(False)
        print("")

    if all(results):
        print("✓ All interface checks passed")
        return 0
    else:
        print("❌ Some interface checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
