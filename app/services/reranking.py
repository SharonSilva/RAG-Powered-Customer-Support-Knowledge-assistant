import re 

from app.models import Chunk

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "do", "does", "did",
    "how", "what", "when", "where", "why", "who", "to", "for", "of",
    "in", "on", "at", "and", "or", "i", "my", "me", "can", "will",
    "have", "has", "had", "it", "this", "that",
}

def _extract_keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}

def _keyword_overlap_score(query_keywords: set[str], content: str) -> float:
    if not query_keywords:
        return 0.0
    
    content_keywords = _extract_keywords(content)
    overlap = query_keywords & content_keywords
    return len(overlap)/len(query_keywords)

def rerank(
    query: str,
    candidates: list[tuple[Chunk, float]],
    top_k: int = 5,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3,
) -> list[Chunk]:
    """
    Combines vector similarity with keyword overlap to re-score candidates.
    Vector distance is converted to a similarity score (1 - distance) so 
    higher is always better, then blended with the keyword overlap score
    using the given weights. Returns the top_k chunks by combined score
    """
    
    query_keywords = _extract_keywords(query)
    
    scored = []
    for chunk, distance in candidates:
        vector_similarity = 1 - distance
        keyword_score = _keyword_overlap_score(query_keywords, chunk.content)
        combined_score = (vector_weight * vector_similarity) + (keyword_weight * keyword_score)
        scored.append((chunk, combined_score))
        
    scored.sort(key=lambda pair: pair[1], reverse=True)
    
    return [chunk for chunk, score in scored[:top_k]]