import os
from openai import OpenAI

from sqlalchemy.orm import Session

from app.services.retrieval import retrieve_candidates_with_distance
from app.services.reranking import rerank_with_scores

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_MODEL = "gpt-4o-mini"

CONFIDENCE_THRESHOLD = 0.35

FALLBACK_MESSAGE = "I don't have information on that in the knowledge base."

def _build_context(scores_chunks: list[tuple]) -> str:
    """
    Builds a numbered context block from the top chunks, so the LLM can
    cite them by number (e.g. [1], [2]) and we can map those numbers back
    to real document/section metadata afterward.
    """
    
    lines = []
    for i, (chunk, score) in enumerate(scores_chunks, start=1):
        section = chunk.section_title or "Untitled Section"
        lines.append(f"[{i}] ({section})\n{chunk.content}")
        
    return "\n\n".join(lines)

def generate_answer(query: str, db: Session, category: str | None = None) -> dict:
    candidates = retrieve_candidates_with_distance(query, db, top_k=10, category=category)
    
    if not candidates:
        return {"answer": FALLBACK_MESSAGE, "sources": []}
    
    scored_chunks = rerank_with_scores(query, candidates, top_k=5)
    
    top_score = scored_chunks[0][1]
    if top_score < CONFIDENCE_THRESHOLD:
        return {"answer": FALLBACK_MESSAGE, "sources": []}
    
    context = _build_context(scored_chunks)
    
    system_prompt = (
        "You are a customer support assistant. Answer the user's question "
        "using ONLY the information in the provided context. "
        "Cite the source of every claim using its bracketed number, e.g. [1]. "
        "If the context does not contain enough information to answer, say "
        "you don't have information on that — do not guess or use outside knowledge."
    )
    
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
    
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    
    answer_text = response.choices[0].message.content
    
    sources = [
        {
            "ref": i,
            "document_id": chunk.document_id,
            "section_title": chunk.section_title,
            "page_number": chunk.page_number,
        }
        for i, (chunk, score) in enumerate(scored_chunks, start=1)
    ]
    
    return {"answer": answer_text, "sources": sources}
        