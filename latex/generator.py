"""Generate themed LaTeX documents from text content"""
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

BASE_TEMPLATE_PATH = Path(__file__).parent / "base_template.tex"

# Default themes for different classes
DEFAULT_THEMES = {
    "AI": {
        "primary_color": "#0B72B9",
        "secondary_color": "#64B5F6",
        "description": "Blue theme for AI courses",
    },
    "CS": {
        "primary_color": "#1976D2",
        "secondary_color": "#42A5F5",
        "description": "Deep blue for Computer Science",
    },
    "MATH": {
        "primary_color": "#7B1FA2",
        "secondary_color": "#BA68C8",
        "description": "Purple for Mathematics",
    },
    "PHYS": {
        "primary_color": "#C62828",
        "secondary_color": "#EF5350",
        "description": "Red for Physics",
    },
    "BIO": {
        "primary_color": "#2E7D32",
        "secondary_color": "#66BB6A",
        "description": "Green for Biology",
    },
    "CHEM": {
        "primary_color": "#F57C00",
        "secondary_color": "#FFB74D",
        "description": "Orange for Chemistry",
    },
    "DEFAULT": {
        "primary_color": "#0B72B9",
        "secondary_color": "#64B5F6",
        "description": "Default blue theme",
    },
}


def get_theme_for_class(class_code: str) -> Dict:
    """
    Get theme based on class code prefix.

    Args:
        class_code: Class code (e.g., "AI101", "CS229")

    Returns:
        Theme dictionary with colors
    """
    # Extract prefix (letters before numbers)
    prefix = "".join([c for c in class_code if c.isalpha()]).upper()

    # Return matching theme or default
    return DEFAULT_THEMES.get(prefix, DEFAULT_THEMES["DEFAULT"])


def generate_themed_latex(
    content: str, class_code: str, date: str, theme: Optional[Dict] = None
) -> str:
    """
    Generate LaTeX content with class-specific theme.

    Args:
        content: The note text content
        class_code: Class identifier (e.g., "AI101", "CS229")
        date: Date string (e.g., "2025-10-01")
        theme: Optional custom theme dict with colors and styling
               If None, will auto-detect based on class_code

    Returns:
        Complete LaTeX source code
    """
    # Auto-detect theme if not provided
    if theme is None:
        theme = get_theme_for_class(class_code)
        logger.info(f"Auto-detected theme for {class_code}: {theme['description']}")

    # Load base template
    if BASE_TEMPLATE_PATH.exists():
        template = BASE_TEMPLATE_PATH.read_text()
    else:
        logger.warning(
            f"Base template not found at {BASE_TEMPLATE_PATH}, using fallback"
        )
        template = get_fallback_template()

    # Extract colors (remove # for LaTeX)
    primary = theme.get("primary_color", "#0B72B9").lstrip("#")
    secondary = theme.get("secondary_color", "#64B5F6").lstrip("#")

    # Escape LaTeX special characters in content
    content_escaped = escape_latex(content)

    # Replace placeholders
    latex = template.replace("PRIMARY_COLOR", primary)
    latex = latex.replace("SECONDARY_COLOR", secondary)
    latex = latex.replace("CLASS_NAME", class_code)
    latex = latex.replace("DATE", date)
    latex = latex.replace("CONTENT", content_escaped)

    return latex


def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters.

    Args:
        text: Raw text content

    Returns:
        Text with LaTeX special characters escaped
    """
    if not text:
        return ""

    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\^{}",
    }

    # Replace backslash first to avoid double-escaping
    result = text.replace("\\", replacements["\\"])

    # Then replace other special characters
    for char, escaped in replacements.items():
        if char != "\\":
            result = result.replace(char, escaped)

    return result


def get_fallback_template() -> str:
    """
    Simple fallback template if base template is missing.

    Returns:
        Minimal LaTeX template string
    """
    return r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{xcolor}
\usepackage{geometry}
\geometry{margin=1in}

\definecolor{primarycolor}{HTML}{PRIMARY_COLOR}
\definecolor{secondarycolor}{HTML}{SECONDARY_COLOR}

\title{\textcolor{primarycolor}{\textbf{CLASS_NAME Notes}}}
\date{\textcolor{secondarycolor}{DATE}}

\begin{document}
\maketitle

\section*{Summary}
CONTENT

\end{document}"""


def list_available_themes() -> Dict:
    """
    Get all available themes.

    Returns:
        Dictionary of theme names to theme configurations
    """
    return DEFAULT_THEMES.copy()


if __name__ == "__main__":
    # Test the generator
    test_content = "This is a test lecture about algorithms and data structures."
    test_class = "CS101"
    test_date = "2025-10-01"

    latex = generate_themed_latex(test_content, test_class, test_date)
    print(latex)
