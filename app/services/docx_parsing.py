from io import BytesIO
from docx import Document as DocxDocument

from app.services.parsing import _normalize_whitespace

def extract_text_from_docx(file_bytes: bytes) -> list[dict]:
    """
    Returns a list with a single {"page_number": None, "text": str} dict,
    since DOCX files dontcarry reliable page-boundary information the way PDFs do.
    Heading styles(Heading 1 Heading 2, etc..) are preserved as short lines so the 
    existing heading-detection heuristic in chunking still picks them up correctly 
    """
    
    doc = DocxDocument(BytesIO(file_bytes))
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(lines)
    cleaned_text = _normalize_whitespace(full_text)
    return [{"page_number": None, "text": cleaned_text}]