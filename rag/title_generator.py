"""
AI-powered title and date extraction from note content
"""
import logging
import re
from datetime import datetime
from typing import Optional

import ollama

from rag.llm_client import get_best_available_model

logger = logging.getLogger(__name__)


def generate_title(text: str, max_chars: int = 35) -> str:
    """
    Generate a concise descriptive title from note content using AI

    Args:
        text: Note content
        max_chars: Maximum title length (default: 35)

    Returns:
        Clean title string (letters, numbers, spaces only)
    """
    if not text or not text.strip():
        return "Untitled Note"

    # Truncate very long text for performance
    content_preview = text[:500] if len(text) > 500 else text

    # Try LLM first
    try:
        model = get_best_available_model()

        if model:
            logger.info(f"🤖 Generating title with {model}...")

            prompt = f"""Generate a SHORT descriptive title (max {max_chars} chars) for these notes.

Rules:
- NO special characters except spaces
- NO quotes or punctuation
- Title only, no explanation
- Be specific and descriptive
- Maximum {max_chars} characters

Notes:
{content_preview}

Title:"""

            response = ollama.generate(
                model=model,
                prompt=prompt,
                options={"temperature": 0.3, "num_predict": 20},
            )

            title = response["response"].strip()

            # Clean the title
            title = _clean_title(title, max_chars)

            if title and len(title) > 3:
                logger.info(f"✅ Generated title: '{title}'")
                return title

    except Exception as e:
        logger.warning(f"⚠️ LLM title generation failed: {e}")

    # Fallback: Extract from content
    return _fallback_title(text, max_chars)


def _clean_title(title: str, max_chars: int) -> str:
    """Clean and validate generated title"""
    # Remove quotes, extra whitespace
    title = title.strip("\"'`")
    title = " ".join(title.split())

    # Remove special characters except spaces
    title = re.sub(r"[^a-zA-Z0-9\s]", "", title)

    # Truncate if too long
    if len(title) > max_chars:
        title = title[:max_chars].rsplit(" ", 1)[0]  # Break at word boundary

    return title.strip()


def _fallback_title(text: str, max_chars: int) -> str:
    """Generate fallback title from first line/sentence"""
    # Try first line
    first_line = text.split("\n")[0].strip()

    if first_line:
        clean = _clean_title(first_line, max_chars)
        if len(clean) > 3:
            logger.info(f"📝 Using fallback title: '{clean}'")
            return clean

    # Try first sentence
    sentences = re.split(r"[.!?]\s+", text)
    if sentences:
        clean = _clean_title(sentences[0], max_chars)
        if len(clean) > 3:
            return clean

    # Last resort: first N chars
    clean = _clean_title(text[:max_chars], max_chars)
    return clean if clean else "Untitled Note"


def extract_date_from_content(text: str) -> Optional[str]:
    """
    Extract date from note content using regex and AI assistance

    Args:
        text: Note content

    Returns:
        ISO format date string (YYYY-MM-DD) or None
    """
    if not text or not text.strip():
        return None

    # Date patterns to search for
    patterns = [
        # ISO format: 2025-09-15
        (r"\b(\d{4})-(\d{2})-(\d{2})\b", "iso"),
        # US format: 09/15/2025 or 9/15/2025
        (r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", "us"),
        # Month name: September 15, 2025 or Sept 15, 2025
        (
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(\d{1,2}),?\s+(\d{4})\b",
            "month_name",
        ),
        # Reverse: 15 September 2025
        (
            r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(\d{4})\b",
            "reverse_month",
        ),
    ]

    # Try regex patterns first
    for pattern, format_type in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            date_str = _parse_date_match(matches[0], format_type)
            if date_str:
                logger.info(f"✅ Extracted date from regex: {date_str}")
                return date_str

    # Try LLM assistance for ambiguous dates
    try:
        model = get_best_available_model()

        if model:
            logger.info("🤖 Using LLM to extract date...")

            # Only send first 300 chars for efficiency
            content_preview = text[:300]

            prompt = f"""Extract the date from these notes. Return ONLY the date in ISO format (YYYY-MM-DD).

If no clear date is found, respond with "NONE".

Notes:
{content_preview}

Date (YYYY-MM-DD only):"""

            response = ollama.generate(
                model=model,
                prompt=prompt,
                options={"temperature": 0.1, "num_predict": 15},
            )

            result = response["response"].strip()

            # Validate ISO format
            if re.match(r"^\d{4}-\d{2}-\d{2}$", result):
                # Verify it's a valid date
                try:
                    datetime.strptime(result, "%Y-%m-%d")
                    logger.info(f"✅ LLM extracted date: {result}")
                    return result
                except ValueError:
                    logger.warning(f"⚠️ LLM returned invalid date: {result}")

    except Exception as e:
        logger.debug(f"LLM date extraction failed: {e}")

    logger.info("📅 No date found in content")
    return None


def _parse_date_match(match: tuple, format_type: str) -> Optional[str]:
    """Convert regex match to ISO date format"""
    try:
        if format_type == "iso":
            year, month, day = match
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime("%Y-%m-%d")

        elif format_type == "us":
            month, day, year = match
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime("%Y-%m-%d")

        elif format_type == "month_name":
            month_str, day, year = match
            month_num = _month_name_to_number(month_str)
            if month_num:
                date_obj = datetime(int(year), month_num, int(day))
                return date_obj.strftime("%Y-%m-%d")

        elif format_type == "reverse_month":
            day, month_str, year = match
            month_num = _month_name_to_number(month_str)
            if month_num:
                date_obj = datetime(int(year), month_num, int(day))
                return date_obj.strftime("%Y-%m-%d")

    except (ValueError, TypeError) as e:
        logger.debug(f"Date parsing failed: {e}")
        return None

    return None


def _month_name_to_number(month_str: str) -> Optional[int]:
    """Convert month name/abbreviation to number"""
    months = {
        "january": 1,
        "jan": 1,
        "february": 2,
        "feb": 2,
        "march": 3,
        "mar": 3,
        "april": 4,
        "apr": 4,
        "may": 5,
        "june": 6,
        "jun": 6,
        "july": 7,
        "jul": 7,
        "august": 8,
        "aug": 8,
        "september": 9,
        "sep": 9,
        "sept": 9,
        "october": 10,
        "oct": 10,
        "november": 11,
        "nov": 11,
        "december": 12,
        "dec": 12,
    }

    return months.get(month_str.lower())
