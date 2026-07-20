import re 
from collections import Counter
from io import BytesIO

from pypdf import PdfReader

def _normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def _detect_repeated_lines(pages_text: list[str], min_repeated_ratio: float = 0.5) -> set[str]:
    """
    Finds lines that appear on a large fraction of pages (likely headers/footers)
    so they can be stripped out. Only considers short lines, since real content lines are unlikely 
    to repeat verbatim across many pages.
    """
    line_counts = Counter()
    
    for page_text in pages_text:
        lines = {line.strip() for line in page_text.split("\n") if line.strip() and len(line.strip()) < 80}
        line_counts.update(lines)
        
    num_pages = len(pages_text)
    threshold = max(2, int(num_pages * min_repeated_ratio))
    
    return {line for line, count in line_counts.items() if count >= threshold}

def extract_text_from_pdf(file_bytes: bytes) -> list[dict]:
    """
    Returns a list of {"page_number": int, "text": str} dicts - one per page,
    with repeated headers/footers stripped and whitespace normalized
    """
    
    reader = PdfReader(BytesIO(file_bytes))
    raw_pages = []
    
    for page in reader.pages:
        page_text = page.extract_text() or ""
        raw_pages.append(page_text)
    
    repeated_lines = _detect_repeated_lines(raw_pages)
    
    cleaned_pages = []
    for i, page_text in enumerate(raw_pages):
        lines = page_text.split("\n")
        kept_lines = [line for line in lines if line.strip() not in repeated_lines]
        cleaned_text = _normalize_whitespace("\n".join(kept_lines))
        cleaned_pages.append({"page_number": i + 1, "text": cleaned_text})
        
    return cleaned_pages
    