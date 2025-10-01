#!/usr/bin/env python3
"""Test markdown to LaTeX conversion"""

from pathlib import Path

from generator import convert_markdown_to_latex, generate_themed_latex

# Test 1: Markdown conversion alone
print("=" * 60)
print("Test 1: Markdown to LaTeX Conversion")
print("=" * 60)

markdown_text = """# Introduction to Machine Learning

Machine learning is a subset of **artificial intelligence** that enables
systems to learn from *data*.

## Key Concepts

### Supervised Learning
- Classification tasks
- Regression analysis
- Training with labeled data

### Unsupervised Learning
- Clustering algorithms
- Dimensionality reduction
- Pattern recognition

## Code Example

Here's a simple Python snippet:

```python
def train_model(data):
    model = Model()
    model.fit(data)
    return model
```

## Important Terms

1. Training data
2. Test data
3. Validation set

The model learns patterns and can use `model.predict()` to make predictions.

**Note**: Always validate your model with *unseen data*.
"""

latex_output = convert_markdown_to_latex(markdown_text)
print(latex_output)
print()

# Test 2: Full themed LaTeX generation with formatted content
print("=" * 60)
print("Test 2: Full Themed PDF Generation (Formatted)")
print("=" * 60)

formatted_content = """# Neural Networks Overview

## Architecture Components

Neural networks consist of:
- **Input layer**: Receives raw data
- **Hidden layers**: Process information
- **Output layer**: Produces predictions

## Training Process

1. Initialize random weights
2. Forward propagation
3. Calculate loss
4. Backpropagation
5. Update weights

### Key Hyperparameters
- Learning rate: `0.001`
- Batch size: `32`
- Epochs: `100`

**Important**: Use *early stopping* to prevent overfitting.
"""

latex_formatted, filename = generate_themed_latex(
    content=formatted_content, class_code="AI101", date="2025-10-01", is_formatted=True
)

# Save to file
output_path = Path("templates/test_formatted_AI101.tex")
output_path.write_text(latex_formatted)
print(f"Generated: {output_path}")
print(f"Filename: {filename}")

# Test 3: Raw text (existing behavior)
print()
print("=" * 60)
print("Test 3: Raw Text (Unformatted)")
print("=" * 60)

raw_content = "This is raw text with special characters: $ & % # _ { }"

latex_raw, filename_raw = generate_themed_latex(
    content=raw_content,
    class_code="CS101",
    date="2025-10-01",
    is_formatted=False,  # Default behavior
)

output_path_raw = Path("templates/test_raw_CS101.tex")
output_path_raw.write_text(latex_raw)
print(f"Generated: {output_path_raw}")
print(f"Filename: {filename_raw}")

print()
print("=" * 60)
print("All tests completed!")
print("=" * 60)
