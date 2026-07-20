import re 

def _split_into_sentences(text:str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]

def _group_by_char_limit(pieces: list[str], max_chunk_chars: int) -> list[str]:
    chunks =[]
    current_chunk = ""
    
    for piece in pieces:
        if len(current_chunk) + len(piece) + 1 <=max_chunk_chars:
            current_chunk = f"{current_chunk} {piece}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = piece
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def chunk_text(text:str, max_chunk_chars: int=800) -> list[str]:
    """
    Splits text into chunks, preffering paragraph breaks when present.
    Falls back to sentence-level grouping when the source has no blank
    lines (common with pdf text extraction), so we never end up with one giant chunk regardless of source
    formatting
    """
    
    raw_paragraphs = re.split(r"\n\s*\n", text.strip())
    paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
    
    if len(paragraphs) <= 1:
        sentences = _split_into_sentences(text)
        return _group_by_char_limit(sentences, max_chunk_chars)
    
    return _group_by_char_limit(paragraphs, max_chunk_chars)
