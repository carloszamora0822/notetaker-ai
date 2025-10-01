#!/usr/bin/env python3
"""
Test suite for AI title generation

Usage:
    python ops/scripts/test_title_generation.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from migrate_filenames import extract_date_and_class, generate_title, sanitize_filename


def test_title_generation():
    """Test AI title generation with various inputs"""
    print("=" * 60)
    print("Test 1: AI Title Generation")
    print("=" * 60)

    test_cases = [
        {
            "name": "Meeting notes",
            "content": """SHPE VP Meeting #4

Discussed national convention planning. Chairs need to finalize rubrics.
Fundraiser ideas: corn booth, raspados stand.
Next GBM scheduled for September 15th.""",
            "expected_keywords": ["SHPE", "Meeting", "Convention"],
        },
        {
            "name": "Lecture notes",
            "content": """CS 4320 - Database Systems
Lecture 5: Normalization

Normal forms (1NF, 2NF, 3NF, BCNF)
Functional dependencies
Decomposition algorithms""",
            "expected_keywords": ["Database", "Normalization"],
        },
        {
            "name": "Short content",
            "content": "Quick note about AI project deadline",
            "expected_keywords": ["AI", "project"],
        },
        {
            "name": "Long content",
            "content": """This is a very long note with lots of information about
various topics including machine learning, deep learning, neural networks,
transformers, attention mechanisms, and much more technical content that
goes on for many paragraphs."""
            * 10,
            "expected_keywords": ["machine", "learning"],
        },
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Content: {test['content'][:60]}...")

        try:
            title = generate_title(test["content"])
            print(f"✓ Generated: '{title}'")
            print(f"  Length: {len(title)} chars, {len(title.split())} words")

            # Check length
            if len(title) > 60:
                print(f"  ⚠️  Title too long ({len(title)} > 60)")
                failed += 1
                continue

            # Check if empty
            if not title or title == "Untitled Note":
                print(f"  ⚠️  Got default/empty title")
                failed += 1
                continue

            passed += 1

        except Exception as e:
            print(f"❌ Failed: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_date_extraction():
    """Test date and class extraction"""
    print("\n" + "=" * 60)
    print("Test 2: Date and Class Extraction")
    print("=" * 60)

    test_cases = [
        ("2025-10-01_AI.txt", "2025-10-01", "AI", True),
        ("2025-12-25_SHPE.txt", "2025-12-25", "SHPE", True),
        ("2025-10-01_CS4320.txt", "2025-10-01", "CS4320", True),
        ("invalid_file.txt", None, None, False),
        ("2025-10-01.txt", None, None, False),
        ("AI.txt", None, None, False),
    ]

    passed = 0
    failed = 0

    for filename, expected_date, expected_class, should_pass in test_cases:
        date, class_code = extract_date_and_class(filename)

        if should_pass:
            if date == expected_date and class_code == expected_class:
                print(f"✓ {filename}: {date}, {class_code}")
                passed += 1
            else:
                print(
                    f"❌ {filename}: got ({date}, {class_code}), expected ({expected_date}, {expected_class})"
                )
                failed += 1
        else:
            if date is None and class_code is None:
                print(f"✓ {filename}: correctly rejected")
                passed += 1
            else:
                print(f"❌ {filename}: should have been rejected")
                failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_filename_sanitization():
    """Test filename sanitization"""
    print("\n" + "=" * 60)
    print("Test 3: Filename Sanitization")
    print("=" * 60)

    test_cases = [
        ("SHPE Meeting Planning", "SHPE_Meeting_Planning"),
        ("Database: Normalization & Keys", "Database_Normalization_Keys"),
        ("AI/ML Project #4", "AIML_Project_4"),
        ("Notes (with special chars!)", "Notes_with_special_chars"),
        (
            "Very Long Title That Exceeds Fifty Characters For Sure",
            "Very_Long_Title_That_Exceeds_Fifty_Characters_F",
        ),
        ("Multiple   Spaces   Here", "Multiple_Spaces_Here"),
    ]

    passed = 0
    failed = 0

    for title, expected in test_cases:
        result = sanitize_filename(title)

        if result == expected:
            print(f"✓ '{title}' → '{result}'")
            passed += 1
        else:
            print(f"❌ '{title}' → '{result}' (expected '{expected}')")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_duplicate_handling():
    """Test duplicate title handling"""
    print("\n" + "=" * 60)
    print("Test 4: Duplicate Handling")
    print("=" * 60)

    # Test that different content generates different titles
    content1 = "Meeting about database normalization and SQL queries"
    content2 = "Meeting about AI project and machine learning models"

    try:
        title1 = generate_title(content1)
        title2 = generate_title(content2)

        print(f"Content 1: {content1}")
        print(f"  Title: '{title1}'")
        print(f"Content 2: {content2}")
        print(f"  Title: '{title2}'")

        if title1 != title2:
            print("✓ Different content produces different titles")
            return True
        else:
            print("❌ Same title for different content")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_special_characters():
    """Test handling of special characters in content"""
    print("\n" + "=" * 60)
    print("Test 5: Special Characters")
    print("=" * 60)

    test_cases = [
        "Meeting notes with émojis 🎉 and ünicode",
        "Content with <HTML> tags & symbols",
        "Notes with 'quotes' and \"double quotes\"",
        "Text with\ttabs\nand\nnewlines",
    ]

    passed = 0
    failed = 0

    for content in test_cases:
        try:
            title = generate_title(content)
            # Title should not have special chars
            if any(char in title for char in "<>\"'&\t\n"):
                print(f"❌ '{content[:30]}...'")
                print(f"   → '{title}' contains special characters")
                failed += 1
            else:
                print(f"✓ '{content[:30]}...'")
                print(f"   → '{title}'")
                passed += 1
        except Exception as e:
            print(f"❌ '{content[:30]}...': {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Title Generation Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Title Generation", test_title_generation),
        ("Date Extraction", test_date_extraction),
        ("Filename Sanitization", test_filename_sanitization),
        ("Duplicate Handling", test_duplicate_handling),
        ("Special Characters", test_special_characters),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\n{total_passed}/{total_tests} test suites passed")

    return 0 if total_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
