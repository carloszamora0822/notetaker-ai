#!/usr/bin/env python3
"""Test smart formatting for raw text"""

from pathlib import Path

from generator import format_raw_text_for_latex, generate_themed_latex

print("=" * 70)
print("Test: Smart Formatting for Raw Text")
print("=" * 70)

# Test 1: Raw text with bullets and structure
raw_text_1 = """MACHINE LEARNING OVERVIEW

Machine learning is the study of algorithms that improve through experience.

KEY CONCEPTS

- Supervised learning uses labeled data
- Unsupervised learning finds patterns
- Reinforcement learning learns through rewards

TYPES OF ALGORITHMS

1. Decision trees
2. Neural networks
3. Support vector machines

Machine learning has many applications in industry.

IMPORTANT NOTES

Special characters like $ & % # _ should be escaped properly."""

print("\nTest 1: Raw text with bullets, numbers, and ALL CAPS headers")
print("-" * 70)

latex_output = format_raw_text_for_latex(raw_text_1)
print(latex_output)
print()

# Test 2: Full PDF generation
print("=" * 70)
print("Test 2: Generate PDF with smart formatting")
print("=" * 70)

full_latex = generate_themed_latex(
    content=raw_text_1,
    class_code="CS101",
    date="2025-10-01",
    is_formatted=False,  # Raw text mode with smart formatting
)

output_path = Path("templates/test_smart_raw_CS101.tex")
output_path.write_text(full_latex)
print(f"✓ Generated: {output_path}")

# Test 3: Simple bullet list
print("\n" + "=" * 70)
print("Test 3: Simple bullet list")
print("=" * 70)

simple_bullets = """Today's lecture covered:
- Arrays and linked lists
- Stacks and queues
- Hash tables
- Binary search trees"""

latex_simple = format_raw_text_for_latex(simple_bullets)
print(latex_simple)
print()

# Test 4: Mixed content
print("=" * 70)
print("Test 4: Mixed content with special characters")
print("=" * 70)

mixed_content = """DATABASE FUNDAMENTALS

1. Tables store data in rows & columns
2. SQL uses SELECT * FROM users
3. Indexes improve query performance

Key points:
- Use primary keys for uniqueness
- Foreign keys maintain relationships
- Normalization reduces redundancy

Cost is O(log n) for tree operations."""

latex_mixed = generate_themed_latex(
    content=mixed_content, class_code="DB101", date="2025-10-01", is_formatted=False
)

output_mixed = Path("templates/test_mixed_DB101.tex")
output_mixed.write_text(latex_mixed)
print(f"✓ Generated: {output_mixed}")

# Test 5: No structure (plain paragraph)
print("\n" + "=" * 70)
print("Test 5: Plain paragraph (no structure)")
print("=" * 70)

plain_text = (
    "This is a plain paragraph with no special structure. "
    "It should just be escaped and formatted as regular text. "
    "Special characters like $ & % should be properly escaped."
)

latex_plain = format_raw_text_for_latex(plain_text)
print(latex_plain)
print()

print("=" * 70)
print("All tests completed!")
print("=" * 70)
print("\nGenerated files:")
print("  - templates/test_smart_raw_CS101.tex")
print("  - templates/test_mixed_DB101.tex")
print("\nTo compile PDFs:")
print("  cd templates")
print("  pdflatex test_smart_raw_CS101.tex")
print("  pdflatex test_mixed_DB101.tex")
