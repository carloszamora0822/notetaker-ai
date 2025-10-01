#!/usr/bin/env python3
"""
LaTeX Renderer - Converts JSON input to .tex files
Follows the contract specified in docs/API-CONTRACTS.md
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "latex.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# LaTeX template with placeholders
TEMPLATE = r"""\documentclass[11pt]{article}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{parskip}

% Define custom colors
\definecolor{ClassColor}{HTML}{0B72B9}
\definecolor{SectionColor}{HTML}{2C3E50}

% Section formatting
\titleformat{\section}
  {\large\bfseries\color{ClassColor}}
  {}{0pt}{}

\titleformat{\subsection}
  {\normalsize\bfseries\color{SectionColor}}
  {}{0pt}{}

% Header/footer
\pagestyle{fancy}
\fancyhf{}
\rhead{\thepage}
\lhead{%CLASS_CODE%}
\renewcommand{\headrulewidth}{0.4pt}

\begin{document}

\title{%TITLE%}
\date{%DATE%}
\maketitle

\section{Summary}
%SUMMARY%

\end{document}
"""


def escape_latex(text: str) -> str:
    """
    Escape LaTeX special characters to prevent compilation errors.

    Args:
        text: Raw text that may contain special characters

    Returns:
        Text with LaTeX special characters properly escaped
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
        "^": r"\textasciicircum{}",
    }

    # Replace backslash first to avoid double-escaping
    result = text.replace("\\", replacements["\\"])

    # Then replace other special characters
    for char, replacement in replacements.items():
        if char != "\\":
            result = result.replace(char, replacement)

    return result


def render(input_json: Path) -> Path:
    """
    Render JSON input to .tex file.

    Args:
        input_json: Path to input JSON file

    Returns:
        Path to generated .tex file

    Raises:
        Exception: If rendering fails
    """
    try:
        logging.info(f"Starting render: {input_json}")

        # Read and parse JSON
        data = json.loads(input_json.read_text())

        # Extract required fields
        summary = data.get("summary", "")
        metadata = data.get("metadata", {})
        output_name = data.get("output_name", "output")

        # Extract metadata fields
        class_code = metadata.get("class_code", "Unknown")
        date = metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
        title = metadata.get("title", class_code)

        # Escape special LaTeX characters
        summary_escaped = escape_latex(summary)
        title_escaped = escape_latex(title)
        class_code_escaped = escape_latex(class_code)

        # Replace placeholders in template
        tex_content = TEMPLATE.replace("%TITLE%", title_escaped)
        tex_content = tex_content.replace("%DATE%", date)
        tex_content = tex_content.replace("%CLASS_CODE%", class_code_escaped)
        tex_content = tex_content.replace("%SUMMARY%", summary_escaped)

        # Write .tex file to templates directory
        templates_dir = Path(__file__).parent.parent / "templates"
        templates_dir.mkdir(exist_ok=True)

        tex_file = templates_dir / f"{output_name}.tex"
        tex_file.write_text(tex_content, encoding="utf-8")

        logging.info(f"Successfully rendered: {tex_file}")
        print(f"[OK] Rendered: {tex_file}")

        return tex_file

    except Exception as e:
        logging.error(f"Render failed for {input_json}: {e}")
        print(f"[ERROR] Render failed: {e}", file=sys.stderr)
        raise


def main():
    """Main entry point for the renderer."""
    if len(sys.argv) < 2:
        print("Usage: render.py <input_json_file>", file=sys.stderr)
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"[ERROR] Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    try:
        render(input_file)
        sys.exit(0)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
