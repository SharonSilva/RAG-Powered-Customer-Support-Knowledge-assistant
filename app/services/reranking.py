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

def _keyword_overlap_score(query_keywords: set[str], content:str) -> float:
    if not query_keywords:
        return 0.0
    
    content_keywords = _extract_keywords(content)
    overlap = query_keywords & content_keywords
    
    return len(overlap)/ len(query_keywords)

def rerank_with_scores(
    query: str,
    candidates: list[tuple[Chunk, float]],
    top_k: int=5,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> list[tuple[Chunk, float]]:
    """
    Same scoring logic is rerank(), but returns (Chunk,combined_score)
    pairs instead of just chunks. The score is needed by the generation
    step to decide whether the retrieval confidenceis high enough to answer or
    whether to fall back to "I dont have information on that."
    """
    
    query_keywords = _extract_keywords(query)
    
    scored = []
    for chunk, distance in candidates:
        vector_similarity = 1 - distance
        keyword_score = _keyword_overlap_score(query_keywords, chunk.content)
        
        combined_score = (vector_weight * vector_similarity) + (keyword_weight*keyword_score)
        scored.append((chunk, combined_score))
        
    scored.sort(key=lambda pair: pair[1], reverse=True)
    
    return scored[:top_k]

def rerank(
    query: str,
    candidates: list[tuple[Chunk, float]],
    top_k: int=5,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3,
) -> list[Chunk]:
    """
    Convenience wrapper around rerank_with_scores for callers that only
    need chunks, not the scores (e.g. the /query endpoints).
    """
    
    scored = rerank_with_scores(query, candidates, top_k, vector_weight, keyword_weight)
    return [chunk for chunk, score in scored]