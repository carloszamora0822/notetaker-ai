"""LLM client for synthesizing RAG results into coherent answers"""
import logging
from typing import Dict, List

import ollama
import requests

logger = logging.getLogger(__name__)


def get_available_models() -> List[str]:
    """Get list of available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        return []
    except Exception:
        return []


def get_best_available_model() -> str:
    """
    Auto-detect best available model for formatting

    Priority:
    1. llama3.2:3b (configured)
    2. llama3.1:8b (best quality)
    3. llama3.1:3b (good balance)
    4. Any llama3 variant
    5. Any model
    """
    available = get_available_models()

    if not available:
        logger.error("No Ollama models found!")
        return None

    # Priority list
    preferred = [
        "llama3.2:3b",
        "llama3.1:8b",
        "llama3.1:3b",
        "llama3:latest",
        "mistral:7b",
        "phi3:mini",
    ]

    for model in preferred:
        if model in available:
            logger.info(f"✅ Using model: {model}")
            return model

    # Fallback to first llama model
    llama_models = [m for m in available if "llama" in m.lower()]
    if llama_models:
        logger.info(f"✅ Using fallback model: {llama_models[0]}")
        return llama_models[0]

    # Use any available model
    logger.warning(f"⚠️ Using first available model: {available[0]}")
    return available[0]


def synthesize_answer(query: str, chunks: List[Dict], max_tokens: int = 500) -> str:
    """
    Synthesize RAG search results into a coherent answer

    Args:
        query: User's original question
        chunks: List of retrieved chunks with metadata
        max_tokens: Maximum length of generated answer

    Returns:
        Synthesized answer string
    """
    if not chunks:
        return "I couldn't find any relevant information in your notes."

    # Build context from chunks
    context = "\n\n".join(
        [f"[{chunk['citation']}]: {chunk['chunk']}" for chunk in chunks[:5]]  # Use top 5 chunks
    )

    # Create prompt
    prompt = f"""You are an AI assistant helping a student review their notes.

User's Question: {query}

Relevant Notes:
{context}

Instructions:
1. Answer the user's question based ONLY on the notes provided
2. Use markdown formatting with structure:
   - Start with a brief 1-sentence overview
   - Use ## headings for main topics
   - Use emojis to make it engaging (📚 🎯 💡 📝 ⚡ 🔍 etc.)
   - Use bullet points (•) or numbered lists
   - Use **bold** for key terms or names
   - Keep it concise (2-4 short sections)
3. If the notes mention specific dates, people, or events, highlight them with **bold**
4. If the notes don't fully answer the question, say so at the end
5. Use a friendly, conversational tone

Format Example:
📚 Brief one-sentence summary here.

## 🎯 Main Topic 1
• Key point with **important term**
• Another detail

## 💡 Main Topic 2  
• More information

Answer:"""

    try:
        # Call Ollama
        response = ollama.generate(
            model="llama3.2:3b",
            prompt=prompt,
            options={
                "temperature": 0.7,
                "num_predict": max_tokens,
            },
        )

        answer = response["response"].strip()
        logger.info(f"LLM synthesis complete: {len(answer)} chars")
        return answer

    except Exception as e:
        logger.error(f"LLM synthesis failed: {e}")
        # Fallback to simple concatenation
        return (
            f"Found {len(chunks)} relevant notes:\n\n"
            + "\n\n".join([f"• {c['chunk'][:200]}..." for c in chunks[:3]])
        )


def summarize_for_pdf(text: str, timeout: int = 30) -> dict:
    """
    Clean and format text for PDF generation.
    Maintains ALL information but improves readability.

    Args:
        text: Raw note content
        timeout: Maximum seconds to wait for LLM

    Returns:
        {
            "formatted_text": str,
            "success": bool,
            "used_llm": bool,
            "error": str | None
        }
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for summarization")
        return {
            "formatted_text": text,
            "success": False,
            "used_llm": False,
            "error": "Empty input",
        }

    # Auto-detect model
    model = get_best_available_model()

    if not model:
        logger.error("❌ No Ollama models available!")
        return {
            "formatted_text": text,
            "success": False,
            "used_llm": False,
            "error": "No Ollama models installed. Run: ollama pull llama3.1:8b",
        }

    # Separate system instructions from user content
    system_prompt = """You are an intelligent note assistant. Your job is to:
1. Analyze and understand the student's notes
2. Fix typos and improve clarity
3. Organize information logically with headers and bullet points
4. Add critical insights and actionable items
5. Preserve ALL original information while making it more useful

Output in clean markdown format (# for headers, - for bullets, **bold** for key terms)."""

    user_prompt = f"""Analyze and format these notes. Add insights about priorities, deadlines, and connections between items:

{text}

---
Provide formatted, actionable notes:"""

    try:
        logger.info(f"🤖 Using model '{model}' to format {len(text)} characters...")

        # Call Ollama with system/user separation
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={
                "temperature": 0.4,  # Slightly higher for creative insights
                "top_p": 0.9
            }
        )

        formatted = response["message"]["content"].strip()

        # Validate output
        if not formatted or len(formatted) < len(text) * 0.5:
            logger.warning(
                f"⚠️ LLM output too short ({len(formatted)} chars vs {len(text)} original)"
            )
            return {
                "formatted_text": text,
                "success": False,
                "used_llm": False,
                "error": "Output too short, using original",
            }

        logger.info(
            f"✅ LLM formatting successful: {len(text)} → {len(formatted)} chars"
        )
        return {
            "formatted_text": formatted,
            "success": True,
            "used_llm": True,
            "error": None,
            "model_used": model,
        }

    except Exception as e:
        error_msg = f"LLM formatting failed: {str(e)}"
        logger.error(f"❌ {error_msg}")

        # Provide helpful error message
        if "not found" in str(e).lower():
            error_msg = f"Model '{model}' not found. Install with: ollama pull {model}"
        elif "connection" in str(e).lower():
            error_msg = "Cannot connect to Ollama. Is it running? Start with: ollama serve"

        return {
            "formatted_text": text,
            "success": False,
            "used_llm": False,
            "error": error_msg,
        }
