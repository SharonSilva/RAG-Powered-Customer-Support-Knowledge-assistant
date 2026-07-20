import re
from app.services.parsing import _normalize_whitespace

def extract_text_from_markdown(file_bytes: bytes) ->list[dict]:
    """
    Returns a list with a single {"page_number":None, "text": str} dict.
    Markdown heading markers {#, ##, etc.} are stripped so the resulting 
    heading lines match the same short, punctuation-free pattern the 
    heading-detection heuristic in chunking already looks for
    """
    
    
    raw_text = file_bytes.decode("utf-8", errors="ignore")
    
    lines = raw_text.split("\n")
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        heading_match = re.match(r"^#{1,6}\s+(.*)", stripped)
        if heading_match:
            cleaned_lines.append(heading_match.group(1).strip())
        else:
            cleaned_lines.append(stripped)

    full_text = "\n".join(cleaned_lines)
    cleaned_text = _normalize_whitespace(full_text)

    return [{"page_number": None, "text": cleaned_text}]