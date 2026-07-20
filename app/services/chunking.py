import re


def _is_heading(line: str) -> bool:
    """
    Heuristic: a line is likely a heading if it's short, doesn't end in
    sentence-ending punctuation, and isn't just noise.
    """
    line = line.strip()
    if not (3 <= len(line) <= 60):
        return False
    if line[-1] in ".!?,;:":
        return False
    return True


def _split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _group_by_char_limit(pieces: list[str], max_chunk_chars: int) -> list[str]:
    chunks = []
    current_chunk = ""

    for piece in pieces:
        if len(current_chunk) + len(piece) + 1 <= max_chunk_chars:
            current_chunk = f"{current_chunk} {piece}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = piece

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def chunk_pages(pages: list[dict], max_chunk_chars: int = 800) -> list[dict]:
    """
    Groups text under detected headings, tagging each resulting chunk with
    the section title and page number it came from. Sections longer than
    max_chunk_chars are split further at sentence boundaries, but keep the
    same section_title so citations stay meaningful.

    Returns a list of {"content": str, "page_number": int, "section_title": str|None}.
    """
    sections = []
    current_section = {"title": None, "page_number": None, "lines": []}

    for page in pages:
        page_number = page["page_number"]
        lines = [l.strip() for l in page["text"].split("\n") if l.strip()]

        for line in lines:
            if _is_heading(line):
                if current_section["lines"]:
                    sections.append(current_section)
                current_section = {"title": line, "page_number": page_number, "lines": []}
            else:
                if current_section["page_number"] is None:
                    current_section["page_number"] = page_number
                current_section["lines"].append(line)

    if current_section["lines"]:
        sections.append(current_section)

    chunks = []
    for section in sections:
        section_text = " ".join(section["lines"])
        sentences = _split_into_sentences(section_text)
        sub_chunks = _group_by_char_limit(sentences, max_chunk_chars)

        for sub_chunk in sub_chunks:
            chunks.append({
                "content": sub_chunk,
                "page_number": section["page_number"],
                "section_title": section["title"],
            })

    return chunks
