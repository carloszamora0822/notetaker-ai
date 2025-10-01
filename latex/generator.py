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


def convert_markdown_to_latex(text: str) -> str:
    r"""
    Convert markdown-style formatting to LaTeX.

    Handles:
    - Headers (# -> \section, ## -> \subsection, ### -> \subsubsection)
    - Bold (**text** -> \textbf{text})
    - Italic (*text* -> \textit{text})
    - Lists (- -> \item)
    - Code blocks (``` -> \begin{verbatim})
    - Inline code (`code` -> \texttt{code})

    Args:
        text: Markdown-formatted text

    Returns:
        LaTeX-formatted text
    """
    import re

    if not text:
        return ""

    # Handle code blocks first (to preserve their content)
    code_blocks = []

    def save_code_block(match):
        code_blocks.append(match.group(1))
        return f"___CODE_BLOCK_{len(code_blocks)-1}___"

    text = re.sub(r"```([\s\S]*?)```", save_code_block, text)

    # Headers (must be done before other replacements)
    text = re.sub(r"^### (.+)$", r"\\subsubsection*{\1}", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", r"\\subsection*{\1}", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+)$", r"\\section*{\1}", text, flags=re.MULTILINE)

    # Bold and Italic (order matters: bold before italic)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"\*(.+?)\*", r"\\textit{\1}", text)

    # Inline code
    text = re.sub(r"`(.+?)`", r"\\texttt{\1}", text)

    # Process lists
    lines = text.split("\n")
    result = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                result.append("\\begin{itemize}")
                in_list = True
            # Remove the bullet and add item
            item_text = stripped[2:]
            result.append(f"  \\item {item_text}")
        elif stripped and stripped[0].isdigit() and ". " in stripped[:4]:
            # Numbered list
            if not in_list:
                result.append("\\begin{enumerate}")
                in_list = "enumerate"
            item_text = stripped.split(". ", 1)[1]
            result.append(f"  \\item {item_text}")
        else:
            if in_list:
                if in_list == "enumerate":
                    result.append("\\end{enumerate}")
                else:
                    result.append("\\end{itemize}")
                in_list = False
            result.append(line)

    if in_list:
        if in_list == "enumerate":
            result.append("\\end{enumerate}")
        else:
            result.append("\\end{itemize}")

    text = "\n".join(result)

    # Restore code blocks
    for i, code in enumerate(code_blocks):
        text = text.replace(
            f"___CODE_BLOCK_{i}___",
            f"\\begin{{verbatim}}\n{code}\n\\end{{verbatim}}",
        )

    return text


def format_raw_text_for_latex(text: str) -> str:
    """
    Apply basic formatting to raw text when LLM is unavailable.

    Handles:
    - Bullet lists (-, *, •)
    - Numbered lists (1., 2., etc.)
    - ALL CAPS lines as section headers
    - Paragraph breaks
    - Preserves structure

    Args:
        text: Raw unformatted text

    Returns:
        LaTeX-formatted text with escaped special characters
    """
    import re

    if not text:
        return ""

    lines = text.split("\n")
    formatted_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            if in_list:
                if in_list == "enumerate":
                    formatted_lines.append("\\end{enumerate}")
                else:
                    formatted_lines.append("\\end{itemize}")
                in_list = False
            formatted_lines.append("")
            continue

        # Detect bullets (-, *, •)
        if re.match(r"^[-*•]\s+", stripped):
            if not in_list:
                formatted_lines.append("\\begin{itemize}")
                in_list = True
            item_text = re.sub(r"^[-*•]\s+", "", stripped)
            formatted_lines.append(f"  \\item {escape_latex(item_text)}")

        # Detect numbered lists (1. 2. etc)
        elif re.match(r"^\d+\.\s+", stripped):
            if in_list and in_list != "enumerate":
                formatted_lines.append("\\end{itemize}")
            if not in_list or in_list != "enumerate":
                formatted_lines.append("\\begin{enumerate}")
                in_list = "enumerate"
            item_text = re.sub(r"^\d+\.\s+", "", stripped)
            formatted_lines.append(f"  \\item {escape_latex(item_text)}")

        # Detect ALL CAPS as section headers (at least 4 chars, no ending punctuation)
        elif (
            len(stripped) > 3
            and stripped.isupper()
            and not re.search(r"[.!?]$", stripped)
        ):
            if in_list:
                if in_list == "enumerate":
                    formatted_lines.append("\\end{enumerate}")
                else:
                    formatted_lines.append("\\end{itemize}")
                in_list = False
            # Convert to title case for better readability
            formatted_lines.append(f"\\subsection*{{{escape_latex(stripped.title())}}}")

        # Regular text
        else:
            if in_list:
                if in_list == "enumerate":
                    formatted_lines.append("\\end{enumerate}")
                else:
                    formatted_lines.append("\\end{itemize}")
                in_list = False
            formatted_lines.append(escape_latex(stripped))

    # Close any open list
    if in_list:
        if in_list == "enumerate":
            formatted_lines.append("\\end{enumerate}")
        else:
            formatted_lines.append("\\end{itemize}")

    return "\n".join(formatted_lines)


def generate_themed_latex(
    content: str,
    class_code: str,
    date: str,
    theme: Optional[Dict] = None,
    is_formatted: bool = False,
) -> str:
    """
    Generate LaTeX content with class-specific theme.

    Args:
        content: The note text content (raw or pre-formatted)
        class_code: Class identifier (e.g., "AI101", "CS229")
        date: Date string (e.g., "2025-10-01")
        theme: Optional custom theme dict with colors and styling
               If None, will auto-detect based on class_code
        is_formatted: If True, content is pre-formatted markdown from LLM
                     If False, content is raw text that needs escaping

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

    # Process content based on format
    if is_formatted:
        # Content from LLM - convert markdown to LaTeX
        logger.info("Processing LLM-formatted markdown content")
        content_processed = convert_markdown_to_latex(content)
    else:
        # Raw content - apply basic formatting then escape
        logger.info("Processing raw content with smart formatting")
        content_processed = format_raw_text_for_latex(content)

    # Replace placeholders
    latex = template.replace("PRIMARY_COLOR", primary)
    latex = latex.replace("SECONDARY_COLOR", secondary)
    latex = latex.replace("CLASS_NAME", class_code)
    latex = latex.replace("DATE", date)
    latex = latex.replace("CONTENT", content_processed)

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
